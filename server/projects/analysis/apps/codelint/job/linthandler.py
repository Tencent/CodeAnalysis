# -*- coding:utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codelint - linthandler job
"""
import datetime
import json
import logging
import os
import shutil
import time
import uuid
from datetime import datetime

from django.db import OperationalError
from django.db.models import Count, Q
from django.utils import timezone

from apps.codelint import models
from apps.codelint.job.utils import grouper, queryset_to_dict, download_and_unzip_file, download_and_load_json_file
from apps.codelint.tasks.datahandler import clean_deleted_issuedetail
from util.encode import encode_with_ignore
from util.genkey import gen_path_key
from util.retrylib import RetryDecor

logger = logging.getLogger(__name__)


class LintResultSummaryHandler(object):

    def __init__(self, scan, task_results):
        """初始化函数
        """
        self._scan = scan
        self._project_id = scan.project_id
        self._task_results = task_results
        self._log_prefix = "[Project: %s][Scan: %s]" % (self._scan.project_id, self._scan.id)
        self._current_time = timezone.make_aware(datetime.now(), timezone.get_current_timezone())

    def get_current_time(self):
        """获取当前时间
        """
        return self._current_time

    def close_toolremove_issues(self):
        """关闭工具移除的问题

        设置为state=closed, resolution=ruleremoved
        """
        checktool_names = [item["name"] for item in self._task_results]
        issue_toolremove_num = models.Issue.everything.filter(project=self._project_id).exclude(
            state__in=[models.Issue.StateEnum.CLOSED, models.Issue.StateEnum.RESOLVED]
        ).exclude(
            checktool_name__in=checktool_names
        ).update(
            state=models.Issue.StateEnum.CLOSED,
            resolution=models.Issue.ResolutionEnum.RULEREMOVE,
            fixed_time=self._current_time,
            scan_fix=self._scan
        )
        logger.info("%s 将%d个工具已移除的问题置为关闭状态" % (self._log_prefix, issue_toolremove_num))
        return issue_toolremove_num

    def close_all_issues(self):
        """入库前关闭所有问题
        先将所有bug state都置为已关闭，但是resolution为空，后续再进行赋值
        """
        issue_tempclose_num = models.Issue.everything.filter(project_id=self._project_id).exclude(
            state__in=[models.Issue.StateEnum.CLOSED, models.Issue.StateEnum.RESOLVED]
        ).update(
            state=models.Issue.StateEnum.CLOSED
        )
        logger.info("%s 将%d个未关闭的问题置为关闭状态" % (self._log_prefix, issue_tempclose_num))
        return issue_tempclose_num

    def refresh_closed_issues(self):
        """修改文件所有已关闭的问题resolution为空的为fixed
        """
        issue_ids = list(models.Issue.everything.filter(
            project_id=self._project_id,
            state=models.Issue.StateEnum.CLOSED,
            resolution__isnull=True
        ).values_list("id", flat=True))
        update_issue_num = 0

        for issue_ids_chunk in grouper(issue_ids, 1000):
            update_issue_num += models.Issue.everything.filter(
                id__in=issue_ids_chunk
            ).update(
                resolution=models.Issue.ResolutionEnum.FIXED,
                fixed_time=self._current_time,
                scan_fix=self._scan
            )
        logger.info('%s 修改文件所有已关闭的问题resolution为空的为fixed: %s' % (
            self._log_prefix, update_issue_num))

    def get_summary(self, issues):
        """
        获取issue结果的统计报告，格式：
            {
                "correctness": {    #问题类别，共有8种
                    "fatal": {      #问题严重级别，共有有4种
                        "rule_count": 10,   #规则数量
                        "active": 10,       #未处理问题
                        "resolved": 10,     #已处理问题
                        "closed": 10        #已关闭问题
                    },
                    "error": {}     #其他严重级别的情况，同上
                    "warning": {}
                    "info": {}
                },
                "security": {},     #其他类别的情况，同上
                ...
            }
        """
        severity_choices = dict(models.Issue.SEVERITY_ENG_CHOICES)
        category_choices = dict(models.Issue.CATEGORY_ENG_CHOICES)
        state_choices = dict(models.Issue.STATE_ENG_CHOICES)
        # 获取发现问题的规则数量，返回（category,severity,rule_count)
        rule_info = issues.values_list("category", "severity") \
            .annotate(rule_count=Count('checkrule_real_name', distinct=True))
        # 获取发现问题的数量，返回（category, severity, state, count)
        state_info = issues.values_list("category", "severity", "state") \
            .annotate(rule_count=Count('id'))
        result = {}
        for (category, severity, rule_count) in rule_info:
            category_dict = result.get(category_choices[category], {})
            category_dict.update(
                {severity_choices[severity]: {"rule_count": rule_count}})
            result.update({category_choices[category]: category_dict})
        for (category, severity, state, count) in state_info:
            category_dict = result.get(category_choices[category], {})
            severity_dict = category_dict.get(severity_choices[severity], {})
            severity_dict.update({state_choices[state]: count})
            category_dict.update({severity_choices[severity]: severity_dict})
            result.update({category_choices[category]: category_dict})
        return result

    def _save_base_lintscan_summary(self, project_issues, **kwargs):
        """保存基础的LintScan概览数据
        """
        scan_issues = project_issues.filter(scan_open_id=self._scan.id, state=models.Issue.StateEnum.ACTIVE)
        severity_choices = dict(models.Issue.SEVERITY_ENG_CHOICES)
        category_choices = dict(models.Issue.CATEGORY_ENG_CHOICES)
        state_choices = dict(models.Issue.STATE_ENG_CHOICES)
        open_num = project_issues.filter(
            scan_open_id=self._scan.id, scan_fix_id__isnull=True, state=models.Issue.StateEnum.ACTIVE).count()
        close_num = project_issues.filter(scan_fix_id=self._scan.id).count()
        active_severity_detail = dict([(severity_choices.get(s, s), c) for (
            s, c) in scan_issues.values_list("severity").annotate(count=Count('id'))])
        active_category_detail = dict([(category_choices.get(i, i), c) for (
            i, c) in scan_issues.values_list("category").annotate(count=Count('id'))])
        total_state_detail = dict([(state_choices.get(field, field), count) for (
            field, count) in project_issues.values_list("state").annotate(count=Count('id'))])
        total_severity_detail = queryset_to_dict(project_issues.values_list(
            "severity", "state").annotate(count=Count('id')), severity_choices, state_choices)
        total_category_detail = queryset_to_dict(project_issues.values_list(
            "category", "state").annotate(count=Count('id')), category_choices, state_choices)
        lintscan, _ = models.LintScan.objects.get_or_create(scan=self._scan)
        lintscan.issue_open_num = open_num
        lintscan.issue_fix_num = close_num
        lintscan.active_issue_num = total_state_detail.get("active", 0)
        lintscan.issue_detail_num = kwargs.get("issue_detail_count", 0)
        lintscan.author_num = project_issues.filter(state=models.Issue.StateEnum.ACTIVE).values(
            "author").distinct().count()
        lintscan.active_severity_detail = json.dumps(active_severity_detail)
        lintscan.active_category_detail = json.dumps(active_category_detail)
        lintscan.total_state_detail = json.dumps(total_state_detail)
        lintscan.total_severity_detail = json.dumps(total_severity_detail)
        lintscan.total_category_detail = json.dumps(total_category_detail)
        lintscan.scan_summary = json.dumps(self.get_summary(scan_issues))
        lintscan.total_summary = json.dumps(self.get_summary(project_issues))
        lintscan.save()

    def save_lintscan_summary(self, **kwargs):
        """保存LintScan概览数据
        :param kwargs: 不定项参数
            - issue_detail_count: int, 未聚合问题总数
        :return:
        """
        project_issues = models.Issue.everything.filter(project_id=self._project_id)
        self._save_base_lintscan_summary(project_issues, **kwargs)

    def start(self):
        """开始保存结果
        """
        self.close_toolremove_issues()
        self.close_all_issues()

    def after_saving_detail(self, **kwargs):
        """保存结果后
        """
        issue_detail_count = kwargs.get("issue_detail_count")
        self.refresh_closed_issues()
        logger.info('%s 统计结果...' % self._log_prefix)
        self.save_lintscan_summary(issue_detail_count=issue_detail_count)

    def finish(self):
        """完成保存结果
        """
        clean_deleted_issuedetail.delay(self._project_id)


class LintResultHandler(object):
    """代码扫描结果处理
    """

    def __init__(self, scan, task_result, current_time):
        """初始化函数
        """
        self._scan = scan
        self._project = self._scan.project
        self._tool_name = task_result["name"]
        self._task_result = task_result
        self._current_time = current_time or timezone.make_aware(datetime.now(), timezone.get_current_timezone())
        self._result_data_dir = None
        self._result_data_paths = []
        self._log_prefix = "[Project: %s][Scan: %s][Tool: %s]" % (self._scan.project_id, self._scan.id, self._tool_name)

    @property
    def issue_detail_num(self):
        return self._task_result["result_data"]["issue_count"]

    def _check_incr_scan(self):
        """判断当前扫描是否为增量扫描
        """
        if self._task_result["result_data"].get("incr_scan") is not None:
            incr_scan = self._task_result["result_data"].get("incr_scan")
            logger.info("%s 通过结果数据获取incr_scan标识: %s" % (self._log_prefix, incr_scan))

        else:
            incr_scan = self._task_result["task_params"].get("incr_scan") is True
            logger.info("%s 通过任务参数获取incr_scan标识: %s" % (self._log_prefix, incr_scan))
        return incr_scan

    def _collect_scan_rule_list(self):
        """获取扫描规则数据
        """
        scan_rules = {}
        scan_rule_pkg_maps = []
        for rule in self._task_result["task_params"].get("rule_list", []):
            scan_rules[rule["name"]] = rule
            if rule.get("pkg_type") == 2:
                scan_rule_pkg_maps.append(models.PackageRuleMap(
                    checkpackage_gid=rule.get("pkg_id"), checkrule_gid=rule.get("gid")))
        self._create_scan_rule_pkg_maps(scan_rule_pkg_maps)
        return scan_rules

    def _create_scan_rule_pkg_maps(self, scan_rule_pkg_maps):
        """创建扫描规则与规则包映射关系
        """
        models.PackageRuleMap.objects.bulk_create(scan_rule_pkg_maps, batch_size=1000, ignore_conflicts=True)

    def _collect_issue_paths(self):
        """获取问题详情数据的路径列表
        :return: list，路径列表
        """
        result_data_paths = []
        for detail_file in self._task_result["result_data"]["issue_detail_paths"]:
            result_data_paths.append(os.path.join(self._result_data_dir, detail_file))
        return result_data_paths

    def _get_issue_global_ignore_flag(self):
        """获取全局忽略标志
        """
        return self._task_result["task_params"].get("issue_global_ignore", False)

    def _yield_issue_from_paths(self):
        for path in self._result_data_paths:
            logger.info('读取issue文件%s结果' % path)
            with open(path, 'r') as f:
                while True:
                    context = f.readline()
                    if not context:
                        break
                    yield json.loads(context)

    def _get_batch_size(self):
        """获取单次批量入库数据量
        """
        if len(self._result_data_paths) < 50:
            return 500
        else:
            return 1000

    def read_codelint_issue_data_and_save(self, callback=None, **kwargs):
        """从多个结果文件逐行读取issue，然后批量入库（task_version=3.0）
        """
        current_path = None
        file_count = 0
        path_issue_count = 0
        file_hash_list = []
        file_issues = {}
        file_issues_list = []

        global_ignore = self._get_issue_global_ignore_flag()
        batch_size = self._get_batch_size()

        for issue in self._yield_issue_from_paths():
            if issue.get("path"):
                if file_issues:
                    logger.info("添加问题列表到待入库列表: %s，共%d个" % (current_path, len(file_issues["issues"])))
                    file_issues_list.append(file_issues)
                    if len(file_issues_list) >= batch_size:
                        logger.info("待入库列表达到阈值，执行入库: %s" % len(file_issues_list))
                        if callback and callable(callback):
                            callback(file_issues_list, global_ignore=global_ignore, **kwargs)
                        file_issues_list = []

                file_count += 1
                current_path = issue["path"]
                current_file_hash = gen_path_key(current_path)
                file_hash_list.append(current_file_hash)
                path_issue_count = issue.get("issues_cnt") or 0
                issue.update({"file_hash": current_file_hash})
                file_issues = {"file_desc": issue, "issues": []}
                logger.info("开始处理第%d个问题文件的数据[问题数:%d]: %s" % (file_count, path_issue_count, issue["path"]))
            elif path_issue_count > 0:
                file_issues["issues"].append(issue)
                path_issue_count -= 1
            else:
                logger.error("当前issue找不到所属文件: %s" % issue)

        if file_issues:
            logger.info("添加问题列表到待入库列表: %s，共%d个" % (current_path, len(file_issues["issues"])))
            file_issues_list.append(file_issues)
        if file_issues_list:
            logger.info("待入库列表剩余问题入库，共%d个" % len(file_issues_list))
            if callback and callable(callback):
                callback(file_issues_list, global_ignore=global_ignore, **kwargs)
        return file_hash_list

    def _init_issuedetail(self, issue_hash, issuedetail_uuid, raw_issue, scm_url, real_revision):
        """初始化IssueDetail
        """
        issuedetail = models.IssueDetail(
            project=self._project,
            issue_hash=issue_hash,
            line=raw_issue['line'],
            column=raw_issue.get('column'),
            scan_revision=self._scan.current_revision if not scm_url else real_revision,
            real_revision=real_revision,
            issuedetail_uuid=issuedetail_uuid,
            author=raw_issue.get('author')
        )
        return issuedetail

    def batch_put_file_result(self, file_issues_list, **kwargs):
        """批量将指定文件的所有issue进行入库
        """
        issue_hash_set = set()
        active_issue_hash_set = set()
        closed_issue_hash_set = set()
        issues_dict = {}
        new_issues_dict = {}
        new_issue_details = []
        new_issue_refs = []
        global_issue_hash_set = set()
        file_hash_set = set()

        for file_issues in file_issues_list:
            if not file_issues:
                continue
            file_desc = file_issues.get("file_desc")
            logger.info("开始入库文件结果，路径：%s" % file_desc["path"])
            if not file_desc.get("issues_cnt"):
                logger.info("文件被删除或无问题，无需入库。路径：%s" % file_desc["path"])
                continue
            scm_url = file_desc.get("scm_url") or ""
            real_revision = file_desc.get('scm_rev') or ""
            real_path = file_desc.get('rel_path') or ""
            file_hash_set.add(file_desc["file_hash"])
            file_owners = file_desc.get("owners")
            if file_owners:
                file_owners = file_owners[:250]
            for raw_issue in file_issues.get("issues"):
                # 处理字段编码异常，采用ignore方式进行处理
                if raw_issue.get('author'):
                    raw_issue["author"] = encode_with_ignore(raw_issue["author"])
                issue_hash = raw_issue.get("issue_hash")
                g_issue_hash = raw_issue.get("g_issue_hash")
                issuedetail_uuid = uuid.uuid1().hex
                # 根据model类型存储对应的数据
                new_issue_details.append(
                    self._init_issuedetail(issue_hash, issuedetail_uuid, raw_issue, scm_url, real_revision))
                for seq, raw_ref in enumerate(raw_issue.get('refs', [])):
                    new_issue_refs.append(models.IssueRefer(
                        project_id=self._project.id,
                        issue_hash=issue_hash,
                        issuedetail_uuid=issuedetail_uuid,
                        file_path=raw_ref['path'],
                        line=raw_ref['line'],
                        msg=raw_ref['msg'],
                        seq=seq + 1))
                if issue_hash not in issue_hash_set:
                    issue_hash_set.add(issue_hash)
                    rule = self.get_scan_rule_info(raw_issue)
                    resolution = raw_issue.get('resolution')
                    if not resolution:
                        active_issue_hash_set.add(issue_hash)
                        global_issue_hash_set.add(g_issue_hash)
                    else:
                        closed_issue_hash_set.add(issue_hash)
                    issue = models.Issue(
                        project=self._project,
                        scan_open_id=self._scan.id,
                        g_issue_hash=g_issue_hash,
                        issue_hash=issue_hash,
                        file_path=file_desc["path"],
                        file_hash=file_desc["file_hash"],
                        language=file_desc.get("language"),
                        real_file_path=real_path,
                        scm_url=scm_url,
                        msg=raw_issue['msg'],
                        author=raw_issue.get('author'),
                        file_owners=file_owners,
                        revision=raw_issue['revision'],
                        ci_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(raw_issue.get('ci_time'))),
                        checkrule_gid=rule["gid"],
                        checkrule_real_name=rule["name"],
                        checktool_name=rule["tool_name"],
                        checkrule_rule_title=rule["rule_title"],
                        checkrule_display_name=rule["display_name"],
                        category=rule["category"],
                        severity=rule["severity"],
                        resolution=resolution,
                        state=models.Issue.StateEnum.CLOSED if resolution else models.Issue.StateEnum.ACTIVE,
                        scan_fix_id=self._scan.id if resolution else None,
                    )
                    issues_dict[issue_hash] = issue
                    new_issues_dict[issue_hash] = issue
        logger.info("正在重新打开issue...")

        # 筛选之前已关闭但又发现的问题，更新问题状态和scan_open信息
        reopen_issue_ids = list(models.Issue.everything.filter(
            project=self._project,
            file_hash__in=list(file_hash_set),
            issue_hash__in=list(active_issue_hash_set),
            resolution__in=[models.Issue.ResolutionEnum.FIXED,
                            models.Issue.ResolutionEnum.BLACKLIST]
        ).exclude(
            state=models.Issue.StateEnum.ACTIVE
        ).values_list("id", flat=True))
        reopen_num = self._reopen_issues_with_ids(reopen_issue_ids, scan_open_id=self._scan.id)
        logger.info("重新打开已关闭且解决方式为已修复的问题数: %s" % reopen_num)

        restore_issue_ids = list(models.Issue.everything.filter(
            project=self._project,
            file_hash__in=list(file_hash_set),
            issue_hash__in=list(active_issue_hash_set)
        ).exclude(
            state=models.Issue.StateEnum.ACTIVE
        ).exclude(
            resolution__in=[
                models.Issue.ResolutionEnum.WONTFIX,
                models.Issue.ResolutionEnum.INVALID,
                models.Issue.ResolutionEnum.HISTORY
            ]
        ).values_list("id", flat=True))
        restore_num = self._reopen_issues_with_ids(restore_issue_ids)
        logger.info("恢复临时关闭的问题数（包含新规则关闭后重新打开的问题）: %s" % restore_num)
        logger.info("正在刷新已存在的issue...")
        logger.info("本次扫描上报关闭问题数为: %s, 列表为: %s" % (len(closed_issue_hash_set), list(closed_issue_hash_set)))
        issues_to_update = []
        for issue_item in models.Issue.everything.filter(project=self._project).filter(
                Q(issue_hash__in=list(active_issue_hash_set), state=models.Issue.StateEnum.ACTIVE) |
                Q(issue_hash__in=list(closed_issue_hash_set))).iterator():
            new_issue_item = new_issues_dict.get(issue_item.issue_hash)
            if not new_issue_item:
                continue
            issue_item.scm_url = new_issue_item.scm_url
            issue_item.real_file_path = new_issue_item.real_file_path
            issue_item.severity = new_issue_item.severity
            issue_item.category = new_issue_item.category
            issue_item.file_owners = new_issue_item.file_owners
            issue_item.author = new_issue_item.author
            issue_item.language = new_issue_item.language
            if not issue_item.scan_fix_id:
                issue_item.scan_fix_id = new_issue_item.scan_fix_id
            if issue_item.resolution not in [models.Issue.ResolutionEnum.WONTFIX,
                                             models.Issue.ResolutionEnum.INVALID,
                                             models.Issue.ResolutionEnum.HISTORY]:
                issue_item.resolution = new_issue_item.resolution
            issues_to_update.append(issue_item)
            new_issues_dict.pop(issue_item.issue_hash)
        new_issue_num = (new_issues_dict.values())
        logger.info("%s 已重新打开issue: %d" % (self._log_prefix, reopen_num))
        logger.info("%s 刷新已存在的问题数据: %d" % (self._log_prefix, len(issues_to_update)))
        models.Issue.everything.bulk_update(
            issues_to_update, ["scm_url", "real_file_path", "severity", "resolution",
                               "file_owners", "language", "scan_fix_id"], 3000)
        # 新建当前文件下的所有问题（如果hash冲突会忽略，即实际新增）
        logger.info("%s 新增Issue，预期有：%d个" % (self._log_prefix, len(new_issue_num)))
        create_issues_bulk = models.Issue.everything.bulk_create(
            new_issues_dict.values(), 3000, ignore_conflicts=True)
        logger.info("%s 新增Issue，预期有：%d个，实际创建：%d个" % (
            self._log_prefix, len(new_issue_num), len(create_issues_bulk)))
        # 批量删除和创建 IssueDetail
        logger.info("%s 删除历史IssueDetail，筛选条件：%d个问题hash值" % (self._log_prefix, len(issue_hash_set)))
        updated_num = self._batch_update_issuedetails(list(issue_hash_set))
        logger.info("%s 删除历史IssueDetail，筛选条件：%d个问题hash值，实际删除: %s" % (
            self._log_prefix, len(issue_hash_set), updated_num))
        logger.info("%s 新增IssueDetail，预期有：%d个" % (self._log_prefix, len(new_issue_details)))
        issue_details_bulk = models.IssueDetail.objects.bulk_create(
            new_issue_details, 3000, ignore_conflicts=True)
        logger.info("%s 新增IssueDetail，预期有：%d个，实际创建：%d个" % (
            self._log_prefix, len(new_issue_details), len(issue_details_bulk)))
        # 批量创建 IssueRefer
        logger.info("%s 新增IssueRefer，预期有：%d个" %
                    (self._log_prefix, len(new_issue_refs)))
        issue_refers_bulk = models.IssueRefer.objects.bulk_create(
            new_issue_refs, 3000, ignore_conflicts=True)
        logger.info("%s 新增IssueRefer，预期有：%d个，实际创建：%d个" % (
            self._log_prefix, len(new_issue_refs), len(issue_refers_bulk)))

        if kwargs.get("global_ignore") is True:
            # 判断是否有全局无效、全局无需修复的问题
            self._batch_update_issue_with_wontfix_resolution(list(global_issue_hash_set))
            self._batch_update_issue_with_invalid_resolution(list(global_issue_hash_set))
        return

    def _reopen_issues_with_ids(self, reopen_issue_ids, scan_open_id=None):
        """分批重开Issue问题，避免全表查询（In查询数据量过大时，也会使用全表查询）
        """
        total_reopen_num = 0
        update_params = {"state": models.Issue.StateEnum.ACTIVE, "resolution": None, "scan_fix": None,
                         "fixed_time": None}
        if scan_open_id:
            update_params["scan_open_id"] = scan_open_id
        for reopen_issue_ids_chunk in grouper(reopen_issue_ids, 1000):
            total_reopen_num += models.Issue.everything.filter(
                id__in=reopen_issue_ids_chunk).update(**update_params)
        return total_reopen_num

    def _batch_update_issuedetails(self, issue_hash_list):
        """批量更新issuedetail数据
        """
        # 分批刷新
        updated_num = 0
        now = timezone.now()
        for issue_hash_list_chunk in grouper(issue_hash_list, 1000):
            attempts = 0
            while attempts < 3:  # 重试三次
                try:
                    updated_num += models.IssueDetail.everything.filter(
                        issue_hash__in=issue_hash_list_chunk).update(deleted_time=now)
                    logger.info("%s update issuedetail: %s" % (self._log_prefix, updated_num))
                    break
                except OperationalError as e:
                    logger.warning("%s update issuedetail failed，%s retry" % (self._log_prefix, attempts))
                    code = e.args[0]
                    if attempts == 2 or code != 1213:
                        raise e
                    attempts += 1
                    time.sleep(60)
        return updated_num

    def _batch_update_issue_with_invalid_resolution(self, global_issue_hash_list):
        """批量将问题处理方式标记为误报
        """
        logger.info("%s 当前问题列表数量: %d" % (self._log_prefix, len(global_issue_hash_list)))
        invalid_issue_hash_list = models.InvalidIssue.objects.filter(
            g_issue_hash__in=global_issue_hash_list,
            scope=models.InvalidIssue.ScopeEnum.REPO,
            project__repo_id=self._project.repo_id).values_list("g_issue_hash", flat=True)
        logger.info("%s 查询到的全局误报问题数: %d" % (self._log_prefix, invalid_issue_hash_list.count()))
        if invalid_issue_hash_list.count() == 0:
            return
        issue_infos = list(models.Issue.objects.filter(
            project_id=self._project.id,
            g_issue_hash__in=invalid_issue_hash_list,
            state=models.Issue.StateEnum.ACTIVE
        ).values("id", "issue_hash"))
        logger.info("%s 将%d个问题设置为误报并添加相关评论" % (self._log_prefix, len(issue_infos)))
        current_time = timezone.make_aware(datetime.now(), timezone.get_current_timezone())
        issue_ids = [item["id"] for item in issue_infos]
        models.Issue.objects.filter(id__in=issue_ids).update(
            scan_fix_id=self._scan.id, fixed_time=current_time,
            state=models.Issue.StateEnum.RESOLVED,
            resolution=models.Issue.ResolutionEnum.INVALID)
        issue_comments = []
        for issue_info in issue_infos:
            issue_comments.append(
                models.IssueComment(
                    issue_id=issue_info["id"],
                    issue_hash=issue_info["issue_hash"],
                    project_id=self._project.id,
                    action="全局无效标记",
                    message="当前问题属于代码库标记的全局无效问题，在[Scan: %d]扫描时自动设置处理方式" % self._scan.id,
                    creator="CodeDog"))
        models.IssueComment.objects.bulk_create(issue_comments, batch_size=1000)

    def _batch_update_issue_with_wontfix_resolution(self, global_issue_hash_list):
        """批量将问题处理方式标记为忽略
        """
        logger.info("%s 当前问题列表数量: %d" % (self._log_prefix, len(global_issue_hash_list)))
        wontfix_issue_hash_list = models.WontFixIssue.objects.filter(
            g_issue_hash__in=global_issue_hash_list,
            scope=models.InvalidIssue.ScopeEnum.REPO,
            project__repo_id=self._scan.project.repo_id).values_list("g_issue_hash", flat=True)
        logger.info("%s 查询到的全局无需处理问题数: %d" % (self._log_prefix, wontfix_issue_hash_list.count()))
        if wontfix_issue_hash_list.count() == 0:
            return
        issue_infos = list(models.Issue.objects.filter(
            project_id=self._project.id, g_issue_hash__in=wontfix_issue_hash_list,
            state=models.Issue.StateEnum.ACTIVE
        ).values("id", "issue_hash"))
        logger.info("%s 将%d个问题设置为无需修复并添加相关评论" % (self._log_prefix, len(issue_infos)))
        current_time = timezone.make_aware(datetime.now(), timezone.get_current_timezone())
        issue_ids = [item["id"] for item in issue_infos]
        models.Issue.objects.filter(id__in=issue_ids).update(
            scan_fix_id=self._scan.id, fixed_time=current_time,
            state=models.Issue.StateEnum.RESOLVED,
            resolution=models.Issue.ResolutionEnum.WONTFIX)
        issue_comments = []
        for issue_info in issue_infos:
            issue_comments.append(
                models.IssueComment(
                    issue_id=issue_info["id"],
                    issue_hash=issue_info["issue_hash"],
                    project_id=self._project.id,
                    action="全局无需修复标记",
                    message="当前问题属于代码库标记的全局无需修复问题，在[Scan: %d]扫描时自动设置处理方式" % self._scan.id,
                    creator="CodeDog"))
        models.IssueComment.objects.bulk_create(issue_comments, batch_size=1000)

    def reopen_issues_with_no_change_files(self, file_hash_list):
        """根据文件哈希值列表重开问题
        忽略有变化的文件或活跃的问题，其他问题重新打开，原因：
        1. 忽略有变化的文件：可能已经修复问题或文件已删除
        2. 忽略活跃问题：问题入库时已置为活跃
        3. 重新打开原因：问题入库前对所有活跃问题进行关闭
        """
        # 忽略有变化的文件或活跃的问题，其他问题重新打开，原因：
        # 1. 忽略有变化的文件：可能已经修复问题或文件已删除
        # 2. 忽略活跃问题：问题入库时已置为活跃
        # 3. 重新打开原因：问题入库前对所有活跃问题进行关闭
        reopen_num = models.Issue.everything.filter(
            project_id=self._project.id,
            checktool_name=self._tool_name,
            resolution__isnull=True
        ).exclude(
            file_hash__in=file_hash_list  # 排除活跃的文件
        ).exclude(
            state=models.Issue.StateEnum.ACTIVE  # 排除活跃的问题
        ).update(
            state=models.Issue.StateEnum.ACTIVE,
            resolution=None,
            scan_fix=None,
            fixed_time=None
        )
        logger.info("已重新打开%d个文件未变更的issue" % reopen_num)

    @RetryDecor()
    def download_task_result(self):
        """下载结果文件
        """
        logger.info('1.1 解析参数，下载task_params: %s' % self._task_result["params_url"])
        self._task_result["task_params"] = download_and_load_json_file(self._task_result["params_url"])
        logger.info('1.1 解析参数，下载result_data: %s' % self._task_result["result_data_url"])
        dir_path, _ = download_and_unzip_file(self._task_result["result_data_url"])
        self._result_data_dir = os.path.join(dir_path, "issue_dir")  # 解压后在issue_dir 目录下
        if not os.path.exists(self._result_data_dir):
            self._result_data_dir = os.path.join(dir_path, "tmp_dir")
        with open(os.path.join(self._result_data_dir, "report.json")) as f:  # 结果在report.json 文件中
            self._task_result["result_data"] = json.loads(f.read())
            logger.info("1.1 获取结果result_data如下：")
            logger.info(json.dumps(self._task_result["result_data"], indent=2))

    def init_lint_handler(self):
        """初始化处理器
        """
        self._incr_scan = self._check_incr_scan()
        self._scan_rules = self._collect_scan_rule_list()
        self._result_data_paths = self._collect_issue_paths()

    def close_ruleremove_issues(self):
        """关闭当前工具下规则移除的bug, 将所有state==closed的bug的resolution=ruleremoved
        """
        scan_rule_list = list(self._scan_rules.keys())
        issue_ids = list(models.Issue.everything.filter(
            project_id=self._project.id,
            state=models.Issue.StateEnum.CLOSED,
            resolution__isnull=True,
            checktool_name=self._tool_name
        ).exclude(
            checkrule_real_name__in=scan_rule_list
        ).values_list("id", flat=True))
        if len(issue_ids) > 0:
            issue_ruleremove_num = 0
            for issue_ids_chunk in grouper(issue_ids, 1000):
                issue_ruleremove_num += models.Issue.everything.filter(id__in=issue_ids_chunk).update(
                    resolution=models.Issue.ResolutionEnum.RULEREMOVE,
                    fixed_time=self._current_time,
                    scan_fix=self._scan
                )
            logger.info("1.1 将%d个规则已移除的问题置为关闭状态" % issue_ruleremove_num)

    def get_scan_rule_info(self, raw_issue):
        """提取规则信息

        工具上报的rule信息包含：rule(规则名称)，checker(工具名称)
        codelint issue关于规则相关字段：
          checkrule_gid(规则id，可为None)
          checkrule_real_name(规则使用名称，必填)
          checkrule_display_name(规则显示名称，非必填)
          checkrule_rule_title(规则详情，非必填) #原rule_title
          checktool_name(工具名称，必填)
          category(规则类别，必填，默认使用 其他)
          severity(严重级别，必填，默认使用 提示）
        """
        rule = self._scan_rules.get(raw_issue["rule"])
        if not rule:
            logger.warning("发现新规则 %s" % raw_issue)
            rule = {
                "gid": None,
                "name": raw_issue["rule"],
                "tool_name": raw_issue["checker"],
                "rule_title": None,
                "display_name": raw_issue["rule"],
                "category": models.Issue.CategoryEnum.OTHER,
                "severity": models.Issue.SeverityEnum.INFO,
            }
            logger.info("新规则简易初始化: %s" % json.dumps(rule))
        return rule

    def save_newrule_issues(self):
        # 更新之前未包含在任务参数内的规则问题列表（即 checkrule_gid为空）
        updated_rule_issues = []
        null_rule_issues = models.Issue.everything.filter(
            project=self._project,
            checktool_name=self._tool_name,
            checkrule_gid__isnull=True)
        logger.info("%s 当前项目包含未入库规则个数有：%d个" % (self._log_prefix, null_rule_issues.count()))
        for null_rule_issue in null_rule_issues:
            rule = self._scan_rules.get(null_rule_issue.checkrule_real_name)
            if not rule:
                continue
            null_rule_issue.checkrule_gid = rule["gid"]
            null_rule_issue.checkrule_rule_title = rule["rule_title"]
            null_rule_issue.checkrule_display_name = rule["display_name"]
            null_rule_issue.category = rule["category"]
            null_rule_issue.severity = rule["severity"]
            updated_rule_issues.append(null_rule_issue)
        logger.info("%s 更新Issue未入库规则编号，预期有：%d个" % (self._log_prefix, len(updated_rule_issues)))
        models.Issue.everything.bulk_update(updated_rule_issues, [
            "checkrule_gid", "checkrule_rule_title", "checkrule_display_name", "category", "severity"])

    def save_checktool_summary(self):
        """保存检测工具的概览数据
        """
        project_issues = models.Issue.everything.filter(project_id=self._project.id,
                                                        checktool_name=self._tool_name)
        scan_issues = project_issues.filter(scan_open=self._scan, state=models.Issue.StateEnum.ACTIVE)
        severity_choices = dict(models.Issue.SEVERITY_ENG_CHOICES)
        state_choices = dict(models.Issue.STATE_ENG_CHOICES)
        open_num = project_issues.filter(scan_open=self._scan, scan_fix__isnull=True,
                                         state=models.Issue.StateEnum.ACTIVE).count()
        close_num = project_issues.filter(scan_fix=self._scan).count()
        active_severity_detail = dict([(severity_choices.get(s, s), c) for (
            s, c) in scan_issues.values_list("severity").annotate(count=Count('id'))])
        total_state_detail = dict([(state_choices.get(field, field), count) for (
            field, count) in project_issues.values_list("state").annotate(count=Count('id'))])
        total_severity_detail = queryset_to_dict(project_issues.values_list(
            "severity", "state").annotate(count=Count('id')), severity_choices, state_choices)
        checktool_scan, _ = models.CheckToolScan.objects.get_or_create(scan=self._scan, name=self._tool_name)
        checktool_scan.issue_open_num = open_num
        checktool_scan.issue_fix_num = close_num
        checktool_scan.active_severity_detail = json.dumps(active_severity_detail)
        checktool_scan.total_state_detail = json.dumps(total_state_detail)
        checktool_scan.total_severity_detail = json.dumps(total_severity_detail)
        checktool_scan.save()

    def clean_data(self):
        logger.info("1. 结束工具%s的结果入库，删除结果缓存目录：%s" % (self._tool_name, self._result_data_dir))
        shutil.rmtree(self._result_data_dir)

    def handle(self):
        """处理
        """
        self.download_task_result()
        self.init_lint_handler()
        if self._incr_scan is False:
            logger.info("%s 当前扫描为全量扫描，更新规则已移除的问题置为关闭状态" % self._log_prefix)
            self.close_ruleremove_issues()

        file_hash_list = self.read_codelint_issue_data_and_save(callback=self.batch_put_file_result)
        if self._incr_scan is True:
            logger.info("%s 当前扫描为增量扫描，重新打开当前工具下无变化文件的issue" % self._log_prefix)
            self.reopen_issues_with_no_change_files(file_hash_list)
        self.save_newrule_issues()
        logger.info("%s 工具问题概览数据" % self._log_prefix)
        self.save_checktool_summary()
        self.clean_data()
