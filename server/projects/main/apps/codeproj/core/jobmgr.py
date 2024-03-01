# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - job core
"""
# 原生 import
import copy
import logging
from datetime import datetime, timedelta

# 第三方 import
from django.conf import settings
from django.db import transaction
from django.utils import timezone

# 项目内 import
from apps.codeproj import models
from apps.codeproj.core.projmgr import ScanSchemeManager
from apps.codeproj.core.scmmgr import ScmClientManager
from apps.job.core import JobCloseHandler, JobDispatchHandler
from apps.job.models import Job, ScanTypeEnum, Task, TaskProcessRelation
from apps.nodemgr.models import ExecTag
from apps.scan_conf.core import CheckPackageManager
from apps.scan_conf.models import CheckTool, Label, Language, PackageMap, ScanApp, ToolProcessRelation
from util import errcode
from util.exceptions import CDErrorBase, CDScmError, ClientError, ProjectScanConfigError
from util.retrylib import RetryDecor
from util.scm.base import ScmAccessDeniedError, ScmClientError, ScmError, ScmNotFoundError
from util.webclients import AnalyseClient

logger = logging.getLogger(__name__)


class JobManager(object):
    """任务管理
    """

    def __init__(self, project=None):
        """初始化函数
        """
        self._project = project
        self._log_prefix = "[Project: %d]" % project.id if project else ""
        self._analysis_client = AnalyseClient()

    def _format_scm_time(self, scm_time):
        """格式化scm时间
        """
        # 时间戳格式转换为日期字符串格式
        if type(scm_time) == int or type(scm_time) == float:
            scm_time = str(datetime.fromtimestamp(scm_time))
        return scm_time

    def _filter_languages(self, languages):
        """筛选语言
        """
        if not languages:
            return []
        languages = languages.split(',')
        return Language.objects.filter(name__in=languages)

    def _filter_labels(self, labels):
        """筛选标签
        """
        if not labels:
            return []
        labels = labels.split(',')
        return Label.objects.filter(name__in=labels)

    def insert_auth_into_job_context(self, job_context):
        """将项目的鉴权信息插入任务参数
        """
        scm_username = self._project.auth_info.get("scm_username")
        logger.info("Auth type: %s[%s]" % (self._project.auth_info.get("auth_type"), scm_username))
        scm_password = self._project.auth_info.get("scm_password")
        job_context.update({
            "scm_auth_info": self._project.auth_info,
            "scm_username": scm_username,
            "scm_password": scm_password
        })

    def get_checktool_scheme_libs_info(self, tool_scheme):
        """获取工具依赖方案依赖信息
        """
        tool_libs = []
        # 已默认按pos排序过
        toollib_maps = tool_scheme.toollibmap.select_related("toollib").all()
        for toollib_map in toollib_maps:
            toollib = toollib_map.toollib
            tool_libs.append({
                "key": str(toollib),
                "name": toollib.name,
                "scm_url": toollib.scm_url,
                "scm_type": toollib.scm_type,
                "envs": toollib.envs,
                "extra_data": toollib.extra_data,
                "auth_info": toollib.auth_info,
                "os": toollib.os,
                "pos": toollib_map.pos
            })
        return tool_libs

    def get_checktool_schemes_info(self, checktool):
        """获取工具依赖信息
        """
        schemes_info = []
        # 获取工具依赖方案
        tool_schemes = checktool.libscheme.all()
        for scheme in tool_schemes:
            # 获取工具依赖方案依赖映射
            schemes_info.append({
                "condition": scheme.condition,
                "default_flag": scheme.default_flag,
                "os": scheme.os,
                "tool_libs": self.get_checktool_scheme_libs_info(scheme)
            })
        return schemes_info

    def get_checktool_info(self, checktool):
        """获取工具详情
        """
        checktool_info = {
            "scm_url": checktool.scm_url,
            "run_cmd": checktool.run_cmd,
            "envs": checktool.envs,
            "display_name": checktool.display_name,
            "virtual_name": checktool.virtual_name,
            "show_display_name": checktool.show_display_name,
            "build_flag": checktool.build_flag,
            "tool_key": checktool.tool_key,
            "tool_schemes": self.get_checktool_schemes_info(checktool)
        }
        checktool_info.update(self.get_checktool_auth_into(checktool))
        return checktool_info

    def get_checktool_auth_into(self, checktool):
        """获取工具auth_info
        """
        if not checktool.auth_info:
            return {}
        else:
            scm_username = checktool.auth_info.get("scm_username")
        logger.info("Auth type: %s[%s]" % (checktool.auth_info.get("auth_type"), scm_username))
        scm_password = checktool.auth_info.get("scm_password")
        return {
            "scm_auth_info": checktool.auth_info,
            "scm_username": scm_username,
            "scm_password": scm_password
        }

    def get_scan_type(self, scan_data, job_context):
        """获取扫描类型
        """
        if scan_data.get("scan_type") is not None and ScanTypeEnum.has_value(scan_data.get("scan_type")):
            scan_type = scan_data["scan_type"]
        else:
            scan_type = ScanTypeEnum.INCRESE if scan_data.get("incr_scan", True) else ScanTypeEnum.FULL
        return scan_type

    def check_job_scm_url(self, job_context):
        """检查当前任务的代码库地址是否匹配
        """
        error = {}
        scm_client = ScmClientManager.get_scm_client_with_project(self._project)
        if not scm_client.url_equal(job_context["scm_url"]):
            logger.error("job_context内的scm_url与项目的scm_url不匹配: %s != %s" % (
                job_context["scm_url"], scm_client.get_http_url()))
            error.update({"job_context": error.get("job_context", []) + ["scm_url不匹配：%s" % job_context["scm_url"]]})
        if error:
            raise CDErrorBase(code=errcode.E_CLIENT, msg="参数错误", data=error)

    def get_job_basic_confs(self, job_context, scan_scheme=None):
        """获取项目的基础任务配置
        """
        if job_context is None:
            job_context = {}
        if not scan_scheme:
            if self._project:
                scan_scheme = self._project.scan_scheme
            else:
                raise ProjectScanConfigError(msg="未指定项目或扫描方案，无法获取任务参数配置")
        job_context.update({
            "scheme_id": scan_scheme.id,
            "scheme_name": scan_scheme.name,
            "issue_global_ignore": scan_scheme.issue_global_ignore,
            "ignore_merged_issue": scan_scheme.ignore_merged_issue,
            "ignore_branch_issue": scan_scheme.ignore_branch_issue,
            "ignore_submodule_clone": scan_scheme.ignore_submodule_clone,
            "ignore_submodule_issue": scan_scheme.ignore_submodule_issue,
            "lfs_flag": scan_scheme.lfs_flag,
            "path_filters": {
                "inclusion": ScanSchemeManager.get_path_list_with_scheme(
                    scan_scheme=scan_scheme, scan_type=models.ScanDir.ScanTypeEnum.INCLUDE,
                    path_type=models.ScanDir.PathTypeEnum.WILDCARD),
                "exclusion": ScanSchemeManager.get_path_list_with_scheme(
                    scan_scheme=scan_scheme, scan_type=models.ScanDir.ScanTypeEnum.EXCLUDE,
                    path_type=models.ScanDir.PathTypeEnum.WILDCARD),
                "re_inclusion": ScanSchemeManager.get_path_list_with_scheme(
                    scan_scheme, path_type=models.ScanDir.PathTypeEnum.REGULAR,
                    scan_type=models.ScanDir.ScanTypeEnum.INCLUDE),
                "re_exclusion": ScanSchemeManager.get_path_list_with_scheme(
                    scan_scheme, path_type=models.ScanDir.PathTypeEnum.REGULAR,
                    scan_type=models.ScanDir.ScanTypeEnum.EXCLUDE)
            },
        })
        if self._project:
            project_team = self._project.repo.project_team
            organization = self._project.repo.organization
            job_context.update({
                "project_id": self._project.id,
                "repo_id": self._project.repo.id,
                "scan_path": self._project.scan_path,
                "team_name": project_team.name if project_team else None,
                "org_sid": organization.org_sid if organization else None,
                "scm_type": self._project.scm_type,
                "scm_url": self._project.get_scm_url_with_auth(),
                "scm_initial_revision": self._project.scm_initial_revision,
            })

        return job_context

    def get_task_process_confs(self, task_confs):
        """获取任务参数进程
        :param task_confs: list，任务参数列表
        :return: list
        """
        for task_conf in task_confs:
            # 获取工具进程并排序
            tool_processes = ToolProcessRelation.objects.filter(checktool__name=task_conf['task_name']).order_by(
                'priority')
            task_conf.update({"processes": tool_processes.values_list("process__name", flat=True)})
            try:
                checktool = CheckTool.objects.get(name=task_conf['task_name'])
            except CheckTool.DoesNotExist:
                scan_app, _ = ScanApp.objects.get_or_create(name=task_conf['module_name'])
                checktool = CheckTool.objects.create(name=task_conf['task_name'], scan_app=scan_app)
            checktool_conf = self.get_checktool_info(checktool)
            task_conf["task_params"].update({"checktool": checktool_conf})
        return task_confs

    def get_lint_setting(self, scan_scheme):
        """获取lint setting
        """
        lint_setting, _ = models.LintBaseSetting.objects.get_or_create(scan_scheme=scan_scheme)
        return lint_setting

    def get_execute_tag(self, job_context, scan_scheme):
        """获取执行标签
        """
        if job_context.get("tag"):
            tag = job_context["tag"]
        else:
            tag = scan_scheme.tag.name if scan_scheme.tag else None
        return tag

    def get_checktool_rules_by_package_maps(self, package_maps):
        """通过规则报映射获取规则列表
        """
        checktool_rules = {}
        for packagemap in package_maps:
            # 判断该规则工具是否正常运营、体验运营
            if packagemap.checktool.status not in [CheckTool.StatusEnum.RUNNING, CheckTool.StatusEnum.TRIAL]:
                continue
            rules = checktool_rules.get(packagemap.checktool.name, [])
            # 判断规则是否未屏蔽且规则有效
            if packagemap.state != PackageMap.StateEnum.DISABLED and not packagemap.checkrule.disable:
                rules.append({'name': packagemap.checkrule.real_name,
                              'gid': packagemap.checkrule.id,
                              'pkg_id': packagemap.checkpackage.id,
                              'pkg_name': packagemap.checkpackage.name,
                              'pkg_type': packagemap.checkpackage.package_type,
                              'pkgmap_id': packagemap.id,
                              'tool_name': packagemap.checktool.name,
                              'category': packagemap.checkrule.category,
                              'display_name': packagemap.checkrule.display_name,
                              'rule_title': packagemap.checkrule.rule_title,
                              'severity': packagemap.severity or packagemap.checkrule.severity,
                              'custom': packagemap.checkrule.custom,
                              'params': packagemap.rule_params or packagemap.checkrule.rule_params})
            checktool_rules.update({packagemap.checktool.name: rules})
        return checktool_rules

    def _get_codelint_task_confs_by_checkprofile(self, checkprofile, task_basic_params):
        """通过规则集获取工具规则配置信息
        """
        context = []
        package_maps = checkprofile.get_checkrules().order_by('checktool_id')
        # 获取配置的规则
        checktool_rules = self.get_checktool_rules_by_package_maps(package_maps)
        envs = "%s \n%s" % (checkprofile.get_checkpackage_envs(), task_basic_params.get("envs") or "")
        for checktool_name, rule_list in checktool_rules.items():
            if not rule_list:  # 空规则列表不下发任务
                continue
            task_params = copy.deepcopy(task_basic_params)
            task_params.update({
                "rules": [item["name"] for item in rule_list],
                "rule_list": rule_list,
                "envs": envs
            })
            context.append({
                "task_name": checktool_name,
                "module_name": "codelint",
                "task_params": task_params,
                "tag": task_params.get("tag"),
                "task_version": "2.0"
            })
        return context

    def _get_codelint_task_confs_by_languages_and_labels(self, languages, labels, task_basic_params):
        """通过规则包获取工具规则配置信息
        """
        context = []
        checkpackages = CheckPackageManager.get_office_checkpackages(languages, labels)
        pkg_maps = CheckPackageManager.get_checkrules_by_checkpackages(checkpackages).order_by('checktool_id')
        checktool_rules = self.get_checktool_rules_by_package_maps(pkg_maps)

        cpkg_envs = []
        for cpkg in checkpackages:
            if not cpkg.envs:
                continue
            cpkg_envs.append(cpkg.envs)
        envs = "%s \n%s" % (" \n".join(cpkg_envs), task_basic_params.get("envs") or "")
        for checktool_name, rule_list in checktool_rules.items():
            if not rule_list:  # 空规则列表不下发任务
                continue
            task_params = copy.deepcopy(task_basic_params)
            task_params.update({
                "rules": [item["name"] for item in rule_list],
                "rule_list": rule_list,
                "envs": envs,
            })
            context.append({
                "task_name": checktool_name,
                "module_name": "codelint",
                "task_params": task_params,
                "tag": task_params.get("tag"),
                "task_version": "2.0"
            })
        return context

    def get_codelint_task_confs(self, job_context, scm_last_revision=None, **kwargs):
        """
        获取codelint下所有工具的任务参数，返回结果：
        [{
            "processes": ["analyze", "datahandle"],
            "tag": "Codedog_Linux",
            "task_name": "cpd",
            "task_params": {},
            "module_name": "codemetric",
            "task_version": "1.0"
        }]
        #如未启用，则返回 []
        """
        # 基础参数获取
        if kwargs.get("scan_scheme"):
            scan_scheme = kwargs["scan_scheme"]
        else:
            scan_scheme = self._project.scan_scheme
        lint_setting = self.get_lint_setting(scan_scheme)
        if not lint_setting.enabled:
            return []
        tag = self.get_execute_tag(job_context, scan_scheme)
        checkprofile = lint_setting.checkprofile
        # 检查参数
        if not scm_last_revision:
            last_scan = models.CodeLintInfo.objects.filter(project=self._project).first()
            scm_last_revision = last_scan.scan_revision if last_scan else None
        if kwargs.get("languages"):
            scan_scheme_languages = [l.name for l in kwargs["languages"]]
        else:
            scan_scheme_languages = [l.name for l in scan_scheme.languages.all()]
        if not scan_scheme_languages:
            raise ClientError(errcode.E_USER_CONFIG_LANG_ERROR, '配置错误，请在项目配置中设置项目语言。')
        task_basic_params = {
            "scan_languages": scan_scheme_languages,
            "pre_cmd": lint_setting.pre_cmd,
            "build_cmd": lint_setting.build_cmd,
            "envs": lint_setting.envs.strip() if lint_setting.envs else "",
            "scm_last_revision": scm_last_revision,
            "incr_scan": job_context.get("incr_scan", True) if scm_last_revision else False,
            "ignore_merged_issue": scan_scheme.ignore_merged_issue,
            "ignore_branch_issue": scan_scheme.ignore_branch_issue,
            "ignore_submodule_clone": scan_scheme.ignore_submodule_clone,
            "ignore_submodule_issue": scan_scheme.ignore_submodule_issue,
            "lfs_flag": scan_scheme.lfs_flag,
            "tag": tag,
        }

        if kwargs.get("labels") and kwargs.get("languages"):
            return self._get_codelint_task_confs_by_languages_and_labels(
                kwargs["languages"], kwargs["labels"], task_basic_params)
        elif checkprofile:
            return self._get_codelint_task_confs_by_checkprofile(
                checkprofile, task_basic_params)
        else:
            raise ClientError(errcode.E_USER_CONFIG_CODELINT_PKG_ERROR, '未配置扫描规则，请在"扫描方案-代码扫描"中添加')

    def get_codemetric_task_confs(self, job_context, scm_last_revision=None, **kwargs):
        """
        获取codelint下所有工具的任务参数，返回结果：
        [{
            "processes": ["analyze", "datahandle"],
            "tag": "Codedog_Linux",
            "task_name": "cpd",
            "task_params": {},
            "module_name": "codemetric",
            "task_version": "1.0"
        }]
        #如未启用，则返回 []
        """
        if kwargs.get("scan_scheme"):
            scan_scheme = kwargs["scan_scheme"]
        else:
            scan_scheme = self._project.scan_scheme
        lint_setting, _ = models.LintBaseSetting.objects.get_or_create(scan_scheme=scan_scheme)
        metric_setting, _ = models.MetricSetting.objects.get_or_create(scan_scheme=scan_scheme)
        if not metric_setting.dup_scan_enabled \
                and not metric_setting.cloc_scan_enabled \
                and not metric_setting.cc_scan_enabled:
            return []
        if kwargs.get("languages"):
            scan_scheme_languages = [l.name for l in kwargs["languages"]]
        else:
            scan_scheme_languages = [l.name for l in scan_scheme.languages.all()]

        tag = self.get_execute_tag(job_context, scan_scheme)
        basic_params = {
            "envs": lint_setting.envs.strip() if lint_setting.envs else "",
            "ignore_merged_issue": scan_scheme.ignore_merged_issue,
            "ignore_branch_issue": scan_scheme.ignore_branch_issue,
            "ignore_submodule_clone": scan_scheme.ignore_submodule_clone,
            "ignore_submodule_issue": scan_scheme.ignore_submodule_issue,
            "lfs_flag": scan_scheme.lfs_flag,
        }
        tasks = []
        # 增加cpd task 重复代码扫描
        if metric_setting.dup_scan_enabled:
            if not scan_scheme_languages:
                raise ClientError(errcode.E_USER_CONFIG_LANG_ERROR, '配置错误，请在项目配置中设置项目语言。')
            last_dup_scan = models.CodeMetricDupInfo.objects.filter(project=self._project).first()
            if not scm_last_revision and self._project:
                scm_last_revision = last_dup_scan.scan_revision if last_dup_scan else self._project.scm_initial_revision
            task_params = {
                "scan_languages": scan_scheme_languages,
                "dup_min_exhi_rate": metric_setting.dup_min_exhi_rate,
                "dup_min_high_rate": metric_setting.dup_min_high_rate,
                "dup_min_midd_rate": metric_setting.dup_min_midd_rate,
                "dup_block_length_min": metric_setting.dup_block_length_min,
                "dup_block_length_max": metric_setting.dup_block_length_max,
                "dup_issue_limit": metric_setting.dup_issue_limit,
                "dup_min_dup_times": metric_setting.dup_min_dup_times,
                "dup_max_dup_times": metric_setting.dup_max_dup_times,
                "scm_last_revision": scm_last_revision,
                **basic_params,
            }
            tasks.append({
                "task_name": 'cpd',
                "task_version": "1.0",
                "module_name": "codemetric",
                "task_params": task_params,
                "tag": tag
            })

        # 增加lizard task 圈复杂度
        if metric_setting.cc_scan_enabled:
            if not scan_scheme_languages:
                raise ClientError(errcode.E_USER_CONFIG_LANG_ERROR, '配置错误，请在项目配置中设置项目语言。')

            last_cc_scan = models.CodeMetricCCInfo.objects.filter(project=self._project).first()
            if not scm_last_revision and self._project:
                scm_last_revision = last_cc_scan.scan_revision if last_cc_scan else self._project.scm_initial_revision
            task_params = {
                "scan_languages": scan_scheme_languages,
                "scm_last_revision": scm_last_revision,
                "min_ccn": metric_setting.min_ccn,
            }
            tasks.append({
                "task_name": 'lizard',
                "task_version": "3.0",
                "module_name": "codemetric",
                "task_params": task_params,
                "tag": tag
            })

        if metric_setting.cloc_scan_enabled:
            last_cloc_scan = models.CodeMetricClocInfo.objects.filter(project=self._project).first()
            if not scm_last_revision and self._project:
                scm_last_revision = last_cloc_scan.scan_revision \
                    if last_cloc_scan else self._project.scm_initial_revision

            task_params = {
                "scm_last_revision": scm_last_revision,
                "corefile_path": metric_setting.core_file_path,
                "filemon_path": metric_setting.file_mon_path,
                "use_lang": metric_setting.use_lang,
                "incr_scan": True,
                "business_infos": [],
                **basic_params
            }
            tasks.append({
                "task_name": 'codecount',
                "task_version": "1.0",
                "module_name": "codemetric",
                "task_params": task_params,
                "tag": tag
            })

        # Todo：支持组件分析
        return tasks

    def get_job_confs(self, job_context=None, last_revision=None, **kwargs):
        """
        获取指定扫描方案的任务参数，返回结果:
        {
            "job_context": {
                "scm_initial_revision": null,
                "path_filters": {
                    "exclusion": [],
                    "inclusion": []
                },
                "scm_url": "http://xxx.git",
                "scm_type": "git",
                "project_id": xxx
            },
            "tasks": [{
                "processes": ["analyze", "datahandle"],
                "tag": "Codedog_Linux",
                "task_name": "cpd",
                "task_params": {},
                "module_name": "codemetric",
                "task_version": "1.0"
            }]
        }
        """
        job_context = self.get_job_basic_confs(job_context, kwargs.get("scan_scheme"))
        languages = self._filter_languages(kwargs.get("languages"))
        labels = self._filter_labels(kwargs.get("labels"))
        logger.info("%s开始获取任务参数，显式指定的语言列表: %s，标签列表: %s" % (self._log_prefix, languages, labels))
        try:
            logger.info("%s开始获取codelint参数" % self._log_prefix)
            lint_tasks = self.get_codelint_task_confs(job_context, last_revision, languages=languages,
                                                      labels=labels, scan_scheme=kwargs.get("scan_scheme"))
            logger.info("%s开始获取codemetric参数" % self._log_prefix)
            metric_tasks = self.get_codemetric_task_confs(job_context, last_revision,
                                                          scan_scheme=kwargs.get("scan_scheme"))
            if not lint_tasks and not metric_tasks:
                raise ClientError(errcode.E_USER_CONFIG_NO_LINT_OR_METRIC, '配置错误，请在设置中启用代码检查或代码度量功能')
            tasks = lint_tasks + metric_tasks
        except Exception as e:
            if isinstance(e, CDErrorBase):
                err_code = e.code
                errmsg = e.msg
            else:
                err_code = errcode.E_SERVER
                errmsg = "%s: %s" % (e.__class__.__name__, e)
            logger.error("%s创建任务参数异常: %s" % (self._log_prefix, e))
            logger.exception(errmsg)
            raise CDErrorBase(code=err_code, msg=errmsg)

        for task in tasks:
            # 获取工具进程并排序
            tool_processes = ToolProcessRelation.objects.filter(checktool__name=task['task_name']).order_by('priority')
            task.update({"processes": tool_processes.values_list("process__name", flat=True)})
            try:
                checktool = CheckTool.objects.get(name=task['task_name'])
            except CheckTool.DoesNotExist:
                scan_app, _ = ScanApp.objects.get_or_create(name=task['module_name'])
                checktool = CheckTool.objects.create(name=task['task_name'], scan_app=scan_app)
            checktool_conf = self.get_checktool_info(checktool)
            task["task_params"].update({"checktool": checktool_conf})
        return {"job_context": job_context, "tasks": tasks}

    def _get_task_confs(self, job_context, last_revision=None):
        """
        获取指定扫描方案的任务参数，返回结果:
        {
            "job_context": {
                "scm_initial_revision": null,
                "path_filters": {
                    "exclusion": [],
                    "inclusion": []
                },
                "scm_url": "http://xxx.git",
                "scm_type": "git",
                "project_id": xx
            },
            "tasks": [{
                "processes": ["analyze", "datahandle"],
                "tag": "Codedog_Linux",
                "task_name": "cpd",
                "task_params": {},
                "module_name": "codemetric",
                "task_version": "1.0"
            }]
        }
        """
        try:
            logger.info("%s开始获取codelint参数" % self._log_prefix)
            lint_tasks = self.get_codelint_task_confs(job_context, last_revision)
            logger.info("%s开始获取codemetric参数" % self._log_prefix)
            metric_tasks = self.get_codemetric_task_confs(job_context, last_revision)
            if not lint_tasks and not metric_tasks:
                raise ClientError(errcode.E_USER_CONFIG_NO_LINT_OR_METRIC, '配置错误，请在设置中启用代码检查或代码度量功能')
            tasks = lint_tasks + metric_tasks
        except Exception as e:
            if isinstance(e, CDErrorBase):
                err_code = e.code
                errmsg = e.msg
            else:
                err_code = errcode.E_SERVER
                errmsg = "%s: %s" % (e.__class__.__name__, e)
            logger.error("%s创建任务参数异常: %s" % (self._log_prefix, e))
            logger.exception(errmsg)
            raise CDErrorBase(code=err_code, msg=errmsg)

        for task in tasks:
            # 获取工具进程并排序
            tool_processes = ToolProcessRelation.objects.filter(checktool__name=task['task_name']).order_by('priority')
            task.update({"processes": tool_processes.values_list("process__name", flat=True)})
            try:
                checktool = CheckTool.objects.get(name=task['task_name'])
            except CheckTool.DoesNotExist:
                scan_app, _ = ScanApp.objects.get_or_create(name=task['module_name'])
                checktool = CheckTool.objects.create(name=task['task_name'], scan_app=scan_app)
            checktool_conf = self.get_checktool_info(checktool)
            task["task_params"].update({"checktool": checktool_conf})
        return tasks

    def _upload_task_params(self, task, task_params):
        """上传任务参数
        """
        try:
            task.task_params = task_params
            task.save()
        except Exception as err:
            logger.exception("[Project: %s][Job: %s][Task: %s] 上传Task参数异常，err: %s" % (
                self._project.id, task.job_id, task.id, err))
            if isinstance(err, CDErrorBase):
                result_code = err.code
                result_msg = err.msg
            else:
                result_code = errcode.E_SERVER
                result_msg = "创建任务异常: %s" % str(err)
            JobCloseHandler.revoke_job(task.job, result_code=result_code, result_msg=result_msg)
            raise

    def _upload_job_context(self, job, job_context):
        """上传任务参数
        """
        try:
            job.context = job_context
            job.save()
        except Exception as err:
            logger.exception("[Project: %s][Job: %s] 上传Job参数异常，err: %s" % (job.project_id, job.id, err))
            if isinstance(err, CDErrorBase):
                result_code = err.code
                result_msg = err.msg
            else:
                result_code = errcode.E_SERVER
                result_msg = "创建任务异常: %s" % str(err)
            JobCloseHandler.revoke_job(job, result_code=result_code, result_msg=result_msg)
            raise

    def _check_task_need_scan(self, task_params, incr_scan, puppy_create):
        """检查任务是否需要运行
        不需要运行的条件：
            1. 非CodeDog Puppy主动创建
            2. 上一次扫描版本存在且与当前准备扫描的版本号相同
            3. 增量扫描
        """
        if puppy_create:
            return True
        if task_params.get("scm_last_revision") and \
                task_params.get("scm_last_revision") == task_params.get("scm_revision") and \
                incr_scan is True:
            return False
        else:
            return True

    @RetryDecor(total=2, interval=60, ignore_errors=[CDScmError])
    def get_scan_scm_info(self, target_revision=None):
        """获取扫描需要的SCM信息
        """
        scm_client = ScmClientManager.get_scm_client_with_project(self._project)
        try:
            if target_revision:
                latest_reivison = target_revision
                logger.info("[%s] 指定版本号启动" % latest_reivison)
            else:
                latest_reivison = scm_client.latest_revision
                logger.info("[%s] 使用最新版本号" % latest_reivison)

            scm_info = {
                "scm_revision": latest_reivison,
                "scm_time": str(scm_client.get_revision_datetime(latest_reivison)),
            }
            return scm_info
        except ScmAccessDeniedError as err:
            logger.warning("[Project: %d] get scan scm info with no perm, err: %s" % (self._project.id, err))
            raise CDScmError(code=errcode.E_SERVER_SCM_FORBIDDEN_ACCESS, msg=err.msg)
        except ScmNotFoundError as err:
            logger.warning("[Project: %d] get scan scm info with no found, err: %s" % (self._project.id, err))
            raise CDScmError(code=errcode.E_SERVER_SCM_NOT_FOUND, msg=err.msg)
        except ScmClientError as err:
            logger.warning("[Project: %d] get scan scm info with wrong auth info, err: %s" % (self._project.id, err))
            raise CDScmError(code=errcode.E_SERVER_SCM_AUTH_ERROR, msg=err.msg)
        except ScmError as err:
            logger.exception("[Project: %d] get scan scm info scm err: %s" % (self._project.id, err))
            raise CDErrorBase(code=errcode.E_SERVER_SCM, msg=err.msg)
        except Exception as err:
            logger.exception("[Project: %d] get scan scm info err: %s" % (self._project.id, err))
            raise CDErrorBase(code=errcode.E_SERVER, msg=str(err))

    def create_waiting_scan_on_analysis_server(self, job, scan_type):
        """在Analysis服务器创建等待中的Scan
        """

        scan = self._analysis_client.api('create_scan', data={
            "repo_id": self._project.repo_id,
            "state": Job.StateEnum.WAITING,
            "create_time": str(job.create_time),
            "job_gid": job.id,
            "type": scan_type,
            "creator": job.creator,
        }, path_params=(self._project.id,))
        logger.info("AnalyseServer创建scan返回结果：scan_id=%s，详情如下:" % scan["id"])
        logger.info(scan)
        job.scan_id = scan["id"]  # 将scan_id写入表中
        job.save()
        return scan

    def update_scan_revision_on_analysis_server(self, job, job_context):
        """在Analysis服务器更新Scan的信息
        """
        scm_time = self._format_scm_time(job_context["scm_time"])
        try:
            scan = self._analysis_client.api('update_scan', data={
                "current_revision": job_context.get('scm_revision'),
                "scm_time": scm_time,
                "state": Job.StateEnum.RUNNING,
            }, path_params=(self._project.id, job.scan_id,))
            logger.info("AnalyseServer更新scan返回结果：scan_id=%s，详情如下:" % scan["id"])
            logger.info(scan)
            return scan
        except Exception as err:  # 访问analyse server异常时，取消任务
            if isinstance(err, CDErrorBase):
                result_code = err.code
                result_msg = err.msg
            else:
                result_code = errcode.E_SERVER_JOB_INIT_ERROR
                result_msg = "初始化任务异常: %s" % str(err)
            JobCloseHandler.revoke_job(job, result_code=result_code, result_msg=result_msg)
            raise

    def create_scan_on_analysis_server(self, job, job_context, scan_type):
        """在Analysis服务器创建扫描
        """
        scm_time = self._format_scm_time(job_context["scm_time"])
        # 调用analyse Server启动扫描
        try:
            scan = self._analysis_client.api('create_scan', data={
                "repo_id": self._project.repo_id,
                "current_revision": job_context.get('scm_revision'),
                "scm_time": scm_time,
                "create_time": str(job.create_time),
                "job_gid": job.id,
                "type": scan_type,  # 1是增量扫描，2是全量扫描
                "creator": job.creator,
            }, path_params=(self._project.id,))
            logger.info("AnalyseServer创建scan返回结果：scan_id=%s，详情如下:" % scan["id"])
            logger.info(scan)
            job.scan_id = scan["id"]  # 将scan_id写入表中
            job.save()
            return scan
        except Exception as err:  # 访问analyse server异常时，取消任务
            if isinstance(err, CDErrorBase):
                result_code = err.code
                result_msg = err.msg
            else:
                result_code = errcode.E_SERVER
                result_msg = "创建任务异常: %s" % str(err)
            JobCloseHandler.revoke_job(job, result_code=result_code, result_msg=result_msg)
            raise

    def _start_job_task(self, job, job_context, task_confs, puppy_create=False):
        """启动任务
        """
        logger.info("%s[Job: %d]开始获取Scm信息" % (self._log_prefix, job.id))
        job_context.update(self.get_scan_scm_info(job_context.get("scm_revision")))
        job_confs = {"job_context": job_context, "tasks": task_confs}
        self.insert_auth_into_job_context(job_confs["job_context"])
        self.update_job(job, job_confs)
        logger.info("%s[Job: %d]更新Analysis服务器的Scan信息" % (self._log_prefix, job.id))
        self.update_scan_revision_on_analysis_server(job, job_context)
        logger.info("%s[Job: %d]开始创建Task" % (self._log_prefix, job.id))
        self.create_tasks(job, job_confs, puppy_create=puppy_create)

    def initialize_job(self, force_create, creator, created_from, async_flag=False, client_flag=False):
        """初始化任务，默认不异步
        """
        error = {}
        # 创建扫描任务
        # 原子化查询和创建新任务，避免race condition
        with transaction.atomic():
            # 判断是否新建任务，如是则创建，否则抛出异常结束
            if not force_create:
                exist_job = Job.objects.select_for_update().filter(project=self._project).exclude(
                    state=Job.StateEnum.CLOSED)
                # force_create为False的情况下，不允许重复启动任务
                if exist_job.count() != 0:
                    scan_ids = list(exist_job.values_list("scan_id", flat=True))
                    raise CDErrorBase(
                        errcode.E_CLIENT, "当前项目分支[%s]%s还有未完成任务，编号为: %s" % (
                            self._project.id, self._project.branch, scan_ids),
                        data={"job_context": error.get("job_context", []) +
                                             ["分支%s: %s 还有未完成任务" % (self._project.id, self._project.branch)]})
            job = Job.objects.create(project=self._project, creator=creator, created_from=created_from,
                                     async_flag=async_flag, client_flag=client_flag)
        return job

    def start_job(self, job, job_context, puppy_create=False):
        """启动任务
        """
        try:
            logger.info("%s[Job: %d]开始初始化任务参数" % (self._log_prefix, job.id))
            job_context = self.get_job_basic_confs(job_context)
            task_confs = self._get_task_confs(job_context, job_context.get("scm_last_revision"))
            self._start_job_task(job, job_context, task_confs, puppy_create)
        except CDErrorBase as err:
            logger.exception("%s[Job: %d]任务启动失败，异常原因: %s" % (self._log_prefix, job.id, err))
            JobCloseHandler.revoke_job(job, err.code, err.msg)
        except Exception as err:
            logger.exception("%s[Job: %d]任务启动失败，异常原因: %s" % (self._log_prefix, job.id, err))
            JobCloseHandler.revoke_job(job, errcode.E_SERVER_JOB_CREATE_ERROR, err)

    def update_job(self, job, job_confs):
        """更新任务
        """
        # 获取任务参数
        now_time = timezone.now()
        job_context = job_confs["job_context"]
        tasks = job_confs["tasks"]
        job_runtime_limit = int(job_confs.get("job_runtime_limit", settings.JOB_RUNTIME_LIMIT))  # 任务执行时长
        job.task_num = len(tasks)
        job.code_line_num = job_context.get("code_line_num")
        job.comment_line_num = job_context.get("comment_line_num")
        job.blank_line_num = job_context.get("blank_line_num")
        job.total_line_num = job_context.get("total_line_num")
        job.filtered_code_line_num = job_context.get("filtered_code_line_num")
        job.filtered_comment_line_num = job_context.get("filtered_comment_line_num")
        job.filtered_blank_line_num = job_context.get("filtered_blank_line_num")
        job.filtered_total_line_num = job_context.get("filtered_total_line_num")
        job.efficient_comment_line_num = job_context.get("efficient_comment_line_num")
        job.filtered_efficient_comment_line_num = job_context.get("filtered_efficient_comment_line_num")
        job.expected_end_time = now_time + timedelta(minutes=job_runtime_limit)
        job.save()

        # 任务参数中包含创建时间，以该时间作为 Job的创建时间和开始时间
        if job_context.get("start_time"):
            try:
                start_time = datetime.strptime(job_context.get("start_time"),
                                               job_context.get("time_format", "%Y-%m-%d %H:%M:%S"))
                job.create_time = start_time
                job.start_time = start_time
                job.expected_end_time = start_time + timedelta(minutes=job_runtime_limit)
                job.save()
            except Exception as e:
                logger.error("[Project: %d][Job: %d] 传入的start_time参数有误：" % (self._project.id, job.id))
                logger.exception(e)
        return job

    def finish_initialized_job(self, job):
        """完成任务初始化
        """
        Job.objects.filter(id=job.id, state=Job.StateEnum.INITING).update(
            state=Job.StateEnum.INITED, initialized_time=timezone.now())

    def init_tasks(self, job, task_names):
        """初始化工具任务
        """
        logger.info("%s [Job: %s] init tasks: %s" % (self._log_prefix, job.id, task_names))
        task_infos = {}
        for task in task_names:
            if task in ["lizard", "cpd", "codecount"]:
                module = "codemetric"
            else:
                module = "codelint"
            t, _ = Task.objects.get_or_create(job=job, task_name=task, module=module,
                                              defaults={"state": Task.StateEnum.RUNNING})
            task_infos[task] = t.id
            tool_processes = ToolProcessRelation.objects.filter(checktool__name=task).order_by("priority")
            for tool_process in tool_processes:
                TaskProcessRelation.objects.get_or_create(task=t, process=tool_process.process)
        return task_infos

    def create_tasks(self, job, job_confs, puppy_create=False):
        """创建任务
        """
        now_time = timezone.now()
        tasks = job_confs["tasks"]
        job_context = job_confs["job_context"]
        incr_scan = job_context.get("incr_scan", True)
        task_done = 0
        ignore_task_num = 0
        # 创建Task
        for task in tasks:
            task_result_code = task.get("result_code", None)
            task_result_msg = task.get("result_msg", None)
            task_result_path = task.get("result_data_url", None)
            task_log_path = task.get("log_url", None)
            finished_processes = task.get("finished_processes", [])
            private_processes = task.get("private_processes", [])
            task_start_time = datetime.strptime(
                task["start_time"], task.get("time_format", "%Y-%m-%d %H:%M:%S")) if task.get("start_time") else None
            task_end_time = datetime.strptime(
                task["end_time"], task.get("time_format", "%Y-%m-%d %H:%M:%S")) if task.get("end_time") else None

            task_params = task["task_params"]
            for key, value in job_context.items():
                if key not in task_params:
                    task_params[key] = value

            # 判断增量扫描时当前版本号与上一次版本号是否相同，如果相同则不创建task，并记录忽略的任务数
            if not self._check_task_need_scan(task_params, incr_scan, puppy_create):
                ignore_task_num += 1
                task_done += 1
                continue

            # 初始创建的task状态为creating，因为创建后还需要保存task参数和标签
            t, created = Task.objects.get_or_create(job=job, task_name=task["task_name"])
            t.module = task["module_name"]
            t.tag = ExecTag.objects.filter(name=task.get("tag")).first()
            t.create_version = task.get("task_version", None)
            t.result_code = task_result_code
            t.result_msg = task_result_msg
            t.result_path = task_result_path
            t.log_url = task_log_path
            t.create_time = task_start_time if task_start_time else t.create_time
            t.start_time = task_start_time
            t.end_time = task_end_time
            t.private = len(private_processes) > 0
            t.save()

            tool_processes = ToolProcessRelation.objects.filter(checktool__name=task["task_name"]).order_by("priority")
            for tool_process in tool_processes:
                # 判断task子进程是否在已结束的进程列表中，如果已经在，则把子进程状态标记为关闭
                state = TaskProcessRelation.StateEnum.CLOSED if tool_process.process.name in finished_processes \
                    else TaskProcessRelation.StateEnum.WAITING
                result_code = task_result_code if state == TaskProcessRelation.StateEnum.CLOSED else None
                result_msg = task_result_msg if state == TaskProcessRelation.StateEnum.CLOSED else None
                result_url = task_result_path if state == TaskProcessRelation.StateEnum.CLOSED else None
                log_url = task_log_path if state == TaskProcessRelation.StateEnum.CLOSED else None
                tpr, created = TaskProcessRelation.objects.get_or_create(task=t, process=tool_process.process)
                tpr.state = state
                tpr.priority = tool_process.process.priority
                tpr.result_code = result_code
                tpr.result_msg = result_msg
                tpr.result_url = result_url
                tpr.log_url = log_url
                tpr.private = tool_process.process.name in private_processes
                tpr.save()

            self._upload_task_params(t, task_params)
            process_count = tool_processes.count()
            t.state = Task.StateEnum.CLOSED if process_count > 0 and process_count == len(
                finished_processes) else Task.StateEnum.WAITING
            t.execute_version = task.get("task_version", None) if t.state == Task.StateEnum.CLOSED else None
            t.progress_rate = task.get("progress_rate", 0)
            if t.state == Task.StateEnum.CLOSED:
                t.progress_rate = 100
                t.start_time = now_time if not t.start_time else t.start_time
                t.end_time = now_time if not t.end_time else t.end_time
            t.save()
            if t.state == Task.StateEnum.CLOSED:
                task_done += 1
        job.task_done = task_done
        if job.task_done == job.task_num:
            job.state = Job.StateEnum.RUNNING
            job.start_time = now_time if not job.start_time else job.start_time
        job.save()

        self._upload_job_context(job, job_context)
        failed_tasks = job.task_set.filter(result_code__gte=errcode.E_SERVER)
        if failed_tasks:
            logger.info("[Job: %d] 存在失败的tasks，开始取消任务..." % job.id)
            task = failed_tasks.order_by("result_code").first()
            JobCloseHandler.revoke_job(job, task.result_code, "task[%d] %s" % (task.id, task.result_msg))
        elif ignore_task_num and ignore_task_num == job.task_num:
            logger.info("[Job: %d] 创建完成，因代码无变更，不需要启动扫描，开始结束任务..." % job.id)
            JobCloseHandler.revoke_job(job, errcode.INCR_IGNORE, "代码无变更，无需再次增量扫描。如有需要，请启动全量扫描。")
        else:
            logger.info("[Job: %d] 创建完成，尝试结束任务..." % job.id)
            JobCloseHandler.close_job(job.id)
        self.finish_initialized_job(job)
        JobDispatchHandler.add_job_to_queue(job)
