# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - project core
"""
# 原生 import
import json
import logging
import uuid

# 第三方 import
from django.db.models import Q
from django.db.utils import IntegrityError
from django.utils.timezone import now

# 项目内 import
from apps.authen.models import Organization, ScmAccount, ScmAuth
from apps.codeproj import models
from apps.scan_conf.core import CheckProfileManager, CheckRuleManager, add_checkrules_to_checkpackage
from apps.scan_conf.models import CheckProfile, PackageMap
from util.exceptions import ProjectCreateError, RepositoryCreateError, ServerConfigError, ServerOperationError, errcode
from util.operationrecord import OperationRecordHandler
from util.scm import ScmClient
from util.webclients import AnalyseClient

logger = logging.getLogger(__name__)


class RepositoryManager(object):
    """基础代码库管理
    """

    @classmethod
    def find_repository(cls, scm_url, queryset=None):
        """查找指定代码库
        :param scm_url: str，代码库地址
        :param queryset: QuerySet, 查询数据集
        """
        git_client = ScmClient(models.Repository.ScmTypeEnum.GIT, scm_url,
                               ScmAuth.ScmAuthTypeEnum.PASSWORD)
        svn_client = ScmClient(models.Repository.ScmTypeEnum.SVN, scm_url,
                               ScmAuth.ScmAuthTypeEnum.PASSWORD)
        scm_urls = [git_client.get_repository(), svn_client.get_repository()]
        if queryset:
            return queryset.filter(scm_url__in=scm_urls).first()
        else:
            return models.Repository.objects.filter(scm_url__in=scm_urls).first()

    @classmethod
    def get_repository(cls, scm_url, **kwargs):
        """获取指定代码库
        :param scm_url: str，代码库地址
        """
        fields = {"scm_url": scm_url}
        url_key = kwargs.get("url_key")
        if url_key:
            fields["url_key"] = url_key
        return models.Repository.objects.filter(**fields).first()

    @classmethod
    def get_repo_url_key(cls, url_key):
        """获取代码库链接 Key值
        """
        if not url_key:
            raise Exception("代码库key值无效")
        else:
            return url_key

    @classmethod
    def create_repository(cls, scm_type, scm_url, ssh_url, user, scm_auth_type=None,
                          scm_username=None, scm_password=None,
                          scm_ssh_info=None, scm_account=None, **kwargs):
        """创建代码库
        :param scm_type: str，代码库类型
        :param scm_url: str，代码库链接
        :param ssh_url: str， 代码库SSH链接
        :param user: User，创建人
        :param scm_auth_type: str，代码库鉴权类型
        :param scm_username: str, 用户名
        :param scm_password: str, 密码
        :param scm_ssh_info: ScmSSH
        :param scm_account: ScmAccount
        :return: Repository
        """
        scm_auth_type = scm_auth_type or ScmAuth.ScmAuthTypeEnum.PASSWORD
        # 代码库地址无效
        if not scm_url:
            raise Exception("代码库地址无效")
        url_key = cls.get_repo_url_key(kwargs.get("url_key"))
        organization = kwargs.get("organization")
        project_team = kwargs.get("project_team")

        repository, created = models.Repository.objects.get_or_create(
            scm_type=scm_type, scm_url=scm_url, url_key=url_key,
            defaults={"creator": user, "ssh_url": ssh_url,
                      "organization": organization, "project_team": project_team})
        # 代码库已接入
        if not created:
            return repository
        # 更新参数
        repository.name = kwargs.get("name")
        repository.created_from = kwargs.get("created_from") or models.Project.CreatedFromEnum.WEB
        repository.assign_perm(user, models.Repository.PermissionEnum.ADMIN)
        cls.set_repository_auth(repository, user, scm_auth_type=scm_auth_type, scm_username=scm_username,
                                scm_password=scm_password, scm_ssh_info=scm_ssh_info, scm_account=scm_account)
        repository.save(user=user)
        return repository

    @classmethod
    def v3_create_repo(cls, pt, scm_type, scm_url, user, **kwargs):
        """仅用于v3，创建代码库
        :param pt: ProjectTeam, 项目
        :param scm_type: str, 代码库类型
        :param scm_url: str, 代码库地址
        :param user: User，操作人
        :return: Repository
        """
        if not scm_url:
            raise RepositoryCreateError(errcode.E_SERVER_REPOSITORY_CREATE, "代码库地址无效")

        # 设置url_key
        url_key = cls.get_repo_url_key("ORG_%d_TEAM_%d" % (pt.organization_id, pt.id))

        # 创建代码库（可能已经创建）
        try:
            repository = models.Repository.objects.create(
                scm_type=scm_type, scm_url=scm_url, user=user, url_key=url_key, project_team=pt)
        except Exception as e:
            logger.exception("create repo exception: %s" % e)
            raise RepositoryCreateError(errcode.E_SERVER_REPOSITORY_CREATE, "代码库已接入")

        # 更新参数
        if kwargs.get("name"):
            repository.name = kwargs["name"]
        else:
            repository.name = scm_url.split('/')[-1]
        repository.ssh_url = kwargs.get("ssh_url")
        repository.created_from = kwargs.get("created_from") or models.Project.CreatedFromEnum.WEB
        repository.organization = pt.organization
        repository.assign_perm(user, models.Repository.PermissionEnum.ADMIN)
        repository.subscribers.add(user)
        repository.save(user=user)
        # 标签
        cls._repository_set_labels(repository, kwargs.get("labels", []))
        return repository

    @classmethod
    def create_repository_with_url(cls, scm_type, scm_url, user, **kwargs):
        """创建代码库
        :param scm_type: str，代码库类型
        :param scm_url: str，代码库链接
        :param user: User，创建人
        :return: Repository
        """
        # 代码库地址无效
        if not scm_url:
            return None
        url_key = cls.get_repo_url_key(kwargs.get("url_key"))
        # 创建代码库（可能已经创建）
        try:
            repository = models.Repository.objects.create(
                scm_type=scm_type, scm_url=scm_url, user=user, url_key=url_key)
        except Exception as e:
            logger.exception("create repo exception: %s" % e)
            return None

        # 更新参数
        repository.ssh_url = kwargs.get("ssh_url")
        repository.name = kwargs.get("name")
        repository.created_from = kwargs.get("created_from") or models.Project.CreatedFromEnum.WEB
        repository.symbol = kwargs.get("symbol")
        repository.assign_perm(user, models.Repository.PermissionEnum.ADMIN)
        repository.subscribers.add(user)
        repository.save(user=user)
        return repository

    @classmethod
    def set_repository_auth(cls, repository, user, scm_auth_type=None, scm_username=None, scm_password=None,
                            scm_ssh_info=None, scm_account=None):
        if scm_auth_type == ScmAuth.ScmAuthTypeEnum.SSHTOKEN:
            repository.scm_ssh_info = scm_ssh_info
            repository.scm_auth_type = ScmAuth.ScmAuthTypeEnum.SSHTOKEN
        else:
            repository.scm_auth_type = ScmAuth.ScmAuthTypeEnum.PASSWORD
            if scm_account:
                repository.scm_account = scm_account
            elif scm_username and scm_password:
                scm_account, created = ScmAccount.objects.get_or_create(
                    user=user, scm_username=scm_username, defaults={"scm_password": scm_password})
                if not created:
                    scm_account.scm_password = scm_password
                    scm_account.save()
                repository.scm_account = scm_account
        repository.save(user=user)
        return repository

    @classmethod
    def check_org_team_create_repo_num(cls, pt):
        """检查团队项目内允许创建代码库的数量
        :param pt: ProjectTeam, 项目
        """
        level_repo_count_choices = dict(Organization.LEVEL_REPO_TEAM_COUNT_CHOICES)
        if models.Repository.objects.filter(project_team=pt).count() >= level_repo_count_choices[pt.organization.level]:
            return False
        return True

    @classmethod
    def _repository_set_labels(cls, repo, labels):
        """代码库设置标签，过滤掉非该代码库的标签
        :param repo: Repository, 代码库
        :param labels: List Label, 标签
        """
        filter_labels = []
        for label in labels:
            if label.project_team == repo.project_team:
                filter_labels.append(label)
        repo.labels.set(filter_labels)

    @classmethod
    def add_repo_members(cls, repo, users, perm):
        """增加代码库成员，仅能添加管理员
        :param repo: Repository, 代码库
        :param users: List<User> user 列表
        :param perm: int, 角色
        :return: nickcnames，成功添加的用户名称
        """
        add_nicknames = []
        if perm == models.Repository.PermissionEnum.ADMIN:
            for user in users:
                # 仅能添加团队内的成员
                if user.has_perm("view_projectteam", repo.project_team):
                    repo.assign_perm(user, perm)
                    add_nicknames.append(user.codedoguser.nickname)
        return add_nicknames

    @classmethod
    def delete_repo(cls, repo_id, user):
        """删除代码库
        """
        repo = models.Repository.objects.filter(id=repo_id).first()
        if not repo:
            raise ServerOperationError("代码库[%s]不存在" % repo_id)
        old_scm_url = repo.scm_url
        deleted_time = now()
        repo.scm_url = ("%s [deleted by %s(%s)]" % (repo.scm_url, user.username, deleted_time))[:198]
        repo.save()
        models.Project.objects.filter(repo_id=repo_id).delete()
        logger.info("[User: %s] 在 %s 删除了代码库 %s-%s 关联的扫描项目" % (user.username, deleted_time, repo_id, old_scm_url))
        models.ScanScheme.objects.filter(repo_id=repo_id).delete()
        logger.info("[User: %s] 在 %s 删除了代码库 %s-%s 关联的扫描方案" % (user.username, deleted_time, repo_id, old_scm_url))
        logger.info("[User: %s] 在 %s 删除了代码库 %s-%s" % (user.username, deleted_time, repo_id, old_scm_url))
        repo.delete(user=user)
        OperationRecordHandler.add_repo_operation_record(
            repo, "删除代码库", user.username, message="删除代码库-%s" % old_scm_url
        )


class ScanSchemeManager(object):
    """基础扫描方案管理
    """

    @classmethod
    def get_default_scanscheme(cls, repo_id):
        """获取默认代码库
        :param repo_id: int，代码库编号
        :return: ScanScheme
        """
        return models.ScanScheme.objects.filter(repo_id=repo_id, default_flag=True).first()

    @classmethod
    def set_default_scanscheme(cls, scan_scheme):
        """设置默认扫描方案，如果已经存在，则直接返回
        :return: ScanScheme
        """
        default_scanscheme = cls.get_default_scanscheme(scan_scheme.repo_id)
        if default_scanscheme:
            return False
        else:
            # 设置默认扫描方案标识
            if models.ScanScheme.objects.select_for_update().filter(repo_id=scan_scheme.repo_id,
                                                                    default_flag=True).count() == 0:
                scan_scheme.default_flag = True
                scan_scheme.save()
            return scan_scheme

    @classmethod
    def filter_usable_global_scheme_templates(cls, org_sid, user):
        """筛选团队内当前用户可用的分析方案模板
        :param org_sid: int, 团队唯一标识
        :param user: User, 用户
        :return schemes: 方案模板
        """
        org_scheme_key = "%s_%s" % (models.ScanScheme.SchemeKey.ORG_KEY, org_sid)
        scheme_ids = list(models.ScanSchemePerm.objects.filter(scan_scheme__repo__isnull=True).filter(
            Q(edit_managers__in=[user]) | Q(execute_managers__in=[user])).values_list("scan_scheme_id", flat=True))
        # 系统模板、团队内公开模板、团队内有权限模板
        global_scheme_templates = models.ScanScheme.objects.filter(repo__isnull=True).filter(
            Q(scheme_key=models.ScanScheme.SchemeKey.PUBLIC) |
            Q(scheme_key=org_scheme_key, scanschemeperm__execute_scope=models.ScanSchemePerm.ScopeEnum.OPEN) |
            Q(scheme_key=org_scheme_key, id__in=scheme_ids)
        ).distinct()
        return global_scheme_templates

    @classmethod
    def init_global_scheme_template(cls, name, scheme_key, user, **kwargs):
        """创建通用的扫描方案
        """
        if not name:
            raise ServerConfigError("名称字段不能为空")
        if scheme_key == models.ScanScheme.SchemeKey.PUBLIC:
            filter_fields = [{"repo__isnull": True, "name": name, "scheme_key": scheme_key}]
        else:
            filter_fields = [{"repo__isnull": True, "name": name, "scheme_key": scheme_key, "creator": user},
                             {"repo__isnull": True, "name": name, "scheme_key": models.ScanScheme.SchemeKey.PUBLIC}]
        filter_list = Q()
        for field in filter_fields:
            filter_list |= Q(**field)
        if models.ScanScheme.objects.select_for_update().filter(filter_list).count() > 0:
            raise ServerConfigError("当前扫描方案名称重复，请调整名称后创建")
        scan_scheme = models.ScanScheme.objects.create(name=name, scheme_key=scheme_key, user=user)
        cls.update_scheme_basic_conf(scan_scheme, user, **kwargs)
        scan_scheme_perm, _ = models.ScanSchemePerm.objects.get_or_create(
            scan_scheme=scan_scheme, defaults={"creator": user})
        scan_scheme_perm.edit_managers.add(user)
        scan_scheme_perm.execute_managers.add(user)
        scan_scheme_perm.edit_scope = models.ScanSchemePerm.ScopeEnum.PRIVATE
        scan_scheme_perm.execute_scope = models.ScanSchemePerm.ScopeEnum.OPEN
        scan_scheme_perm.save()
        return scan_scheme

    @classmethod
    def init_scheme(cls, repo_id, name=None, user=None, **kwargs):
        """创建初始扫描方案
        """
        if not name or models.ScanScheme.objects.filter(repo_id=repo_id, name=name).count() > 0:
            name = str(uuid.uuid4()).replace("-", "")
        scan_scheme = models.ScanScheme.objects.create(repo_id=repo_id, name=name, user=user)
        cls.update_scheme_basic_conf(scan_scheme, user, **kwargs)
        scan_scheme_perm, _ = models.ScanSchemePerm.objects.get_or_create(scan_scheme=scan_scheme,
                                                                          defaults={"creator": user})
        return scan_scheme

    @classmethod
    def create_init_scheme(cls, repo_id, user=None, **kwargs):
        """创建扫描方案
        :param repo_id: int，代码库编号
        :param user: User，创建人
        """
        if kwargs.get("global_scheme"):
            scan_scheme = kwargs.pop("global_scheme")
        else:
            scan_scheme = cls.init_scheme(repo_id, user=user, **kwargs)
        # 配置代码扫描
        lint_setting, _ = models.LintBaseSetting.objects.get_or_create(scan_scheme=scan_scheme,
                                                                       defaults={"creator": user})
        if kwargs.get("lint_enabled"):
            lint_setting.enabled = True
            lint_setting.pre_cmd = kwargs.get("pre_cmd")
            lint_setting.build_cmd = kwargs.get("build_cmd")
            lint_setting.envs = kwargs.get("envs")
            # 设置扫描规则集
            lint_setting.checkprofile = cls.create_default_check_profile(
                scan_scheme, user=user, labels=kwargs.get("labels"))
            lint_setting.save()
        # 配置代码度量
        metric_setting, _ = models.MetricSetting.objects.get_or_create(scan_scheme=scan_scheme,
                                                                       defaults={"creator": user})
        metric_setting.cc_scan_enabled = kwargs.get("cc_scan_enabled", False)
        metric_setting.dup_scan_enabled = kwargs.get("dup_scan_enabled", False)
        metric_setting.cloc_scan_enabled = kwargs.get("cloc_scan_enabled", False)
        metric_setting.save()
        return scan_scheme

    @classmethod
    def update_scheme(cls, scheme_id, user=None, **kwargs):
        """更新扫描方案
        :param scheme_id: int，扫描方案编号
        :param user: User，更新人
        :param kwargs: 方案配置信息
        """
        scan_scheme = models.ScanScheme.objects.get(id=scheme_id)
        scan_scheme = cls.update_scheme_basic_conf(scan_scheme, user, **kwargs)
        cls.update_scheme_lint_settings(scan_scheme, user, **kwargs)
        cls.update_scheme_metric_setting(scan_scheme, user, **kwargs)
        return scan_scheme

    @classmethod
    def get_lint_setting(cls, scan_scheme):
        """获取指定扫描方案的扫描配置
        :param scan_scheme: ScanScheme，扫描方案
        :return: LintBaseSetting
        """
        lint_setting, _ = models.LintBaseSetting.objects.get_or_create(scan_scheme=scan_scheme)
        return lint_setting

    @classmethod
    def get_metric_setting(cls, scan_scheme):
        """获取指定扫描方案的扫描配置
        :param scan_scheme: ScanScheme，扫描方案
        :return: MetricSetting
        """
        metric_setting, _ = models.MetricSetting.objects.get_or_create(scan_scheme=scan_scheme)
        return metric_setting

    @classmethod
    def get_check_profile(cls, scan_scheme):
        """获取指定扫描方案的规则集
        :param scan_scheme: ScanScheme，扫描方案
        :return: CheckProfile
        """
        lint_setting, _ = models.LintBaseSetting.objects.get_or_create(scan_scheme=scan_scheme)
        return lint_setting.checkprofile

    @classmethod
    def create_default_check_profile(cls, scan_scheme, user, labels=None, **kwargs):
        """根据扫描语言创建默认规则集
        :param scan_scheme: ScanScheme，扫描方案
        :param user: User，创建用户
        :param labels: list, 标签
        :return:
        """
        checkprofile = CheckProfileManager.create_scheme_checkprofile(scan_scheme, user=user, labels=labels)
        logger.info("create or update checkprofile: %s-%s" % (scan_scheme, checkprofile))
        return checkprofile

    @classmethod
    def copy_from_check_profile(cls, scan_scheme, from_checkprofile_id, user):
        """拷贝指定的规则集作为指定扫描的规则集
        :param scan_scheme: ScanScheme，扫描方案
        :param from_checkprofile_id: int，规则集编号
        :param user: User，操作用户
        """
        checkprofile_name = "ScanScheme[%d]规则集" % scan_scheme.id
        from_checkprofile = CheckProfile.objects.filter(id=from_checkprofile_id).first()
        if not from_checkprofile:
            logger.error("[Scanscheme: %s] 拷贝的规则集编号 %s 不存在" % (scan_scheme.id, from_checkprofile_id))
            return
        checkprofile = CheckProfileManager.create_from_checkprofile(checkprofile_name, from_checkprofile, user)
        return checkprofile

    @classmethod
    def update_check_profile(cls, scan_scheme, checkprofile_id, user):
        """更新扫描方案的规则集编号
        :param scan_scheme:
        :param checkprofile_id:
        :param user:
        :return:
        """
        lint_setting, _ = models.LintBaseSetting.objects.get_or_create(scan_scheme=scan_scheme)
        lint_setting.checkprofile_id = checkprofile_id
        lint_setting.save(user=user)

    @classmethod
    def get_languages(cls, scan_scheme):
        """获取指定扫描方案的语言列表
        """
        return scan_scheme.languages.all()

    @classmethod
    def update_languages(cls, scan_scheme, language_list):
        """更新指定扫描配置的语言列表
        :param scan_scheme: ScanScheme
        :param language_list: list<CheckProfile> 规则集列表
        """
        scan_scheme.languages.add(*language_list)
        ids = [language.id for language in language_list]
        remove_languages = scan_scheme.languages.exclude(id__in=ids)
        scan_scheme.languages.remove(*remove_languages)

    @classmethod
    def create_scheme_with_ref_scheme(cls, repo_id, ref_scheme, user=None, **kwargs):
        """参考指定方案创建扫描方案
        :param repo_id: int，代码库编号
        :param ref_scheme: ScanScheme，参考扫描方案
        :param user: User
        :return: ScanScheme
        """
        scan_scheme = cls.init_scheme(repo_id, user=user, **kwargs)
        scan_scheme.refer_scheme = ref_scheme
        scan_scheme.save()
        cls.sync_with_ref_scheme(scan_scheme, ref_scheme, user, sync_all=True)
        return scan_scheme

    @classmethod
    def sync_with_ref_scheme(cls, scan_scheme, ref_scheme, user, **kwargs):
        """同步参考扫描方案配置
        :param scan_scheme: ScanScheme, 分析方案
        :param ref_scheme: ScanScheme, 参考分析方案/方案模板
        :param user: User
        **kwargs: 参数
            sync_all: boolean, 同步全部
            sync_basic_conf: boolean, 同步基础配置
            sync_lint_conf, 同步代码检查配置
            sync_metric_conf, 同步代码度量配置
            sync_filter_conf, 同步过滤配置
        """
        ref_lint_setting = models.LintBaseSetting.objects.filter(scan_scheme=ref_scheme).first()
        ref_metric_setting = models.MetricSetting.objects.filter(scan_scheme=ref_scheme).first()
        ref_scan_dirs = models.ScanDir.objects.filter(scan_scheme=ref_scheme)
        ref_default_scan_exclude_paths = models.SchemeDefaultScanPathExcludeMap.objects.filter(scan_scheme=ref_scheme)

        sync_all = kwargs.get("sync_all", False)
        if sync_all or kwargs.get("sync_basic_conf"):
            # 同步基础配置
            scan_scheme.tag = ref_scheme.tag
            scan_scheme.description = ref_scheme.description
            cls.update_languages(scan_scheme, language_list=ref_scheme.languages.all())

        lint_setting, _ = models.LintBaseSetting.objects.get_or_create(scan_scheme=scan_scheme)
        if ref_lint_setting:
            if sync_all or kwargs.get("sync_lint_rule_conf"):
                # 同步代码检查规则配置
                if lint_setting.checkprofile:
                    checkprofile = CheckProfileManager.copy_from_checkprofile(lint_setting.checkprofile,
                                                                              ref_lint_setting.checkprofile)
                else:
                    # 拷贝规则集
                    checkprofile = cls.copy_from_check_profile(scan_scheme, ref_lint_setting.checkprofile_id, user=user)
                lint_setting.checkprofile = checkprofile
            if sync_all or kwargs.get("sync_lint_build_conf"):
                # 同步代码检查编译配置
                lint_setting.enabled = ref_lint_setting.enabled
                lint_setting.default_author = ref_lint_setting.default_author
                lint_setting.build_cmd = ref_lint_setting.build_cmd
                lint_setting.envs = ref_lint_setting.envs
                lint_setting.pre_cmd = ref_lint_setting.pre_cmd
            lint_setting.save(user=user)

        if sync_all or kwargs.get("sync_metric_conf"):
            # 同步代码度量配置
            metric_setting, _ = models.MetricSetting.objects.get_or_create(scan_scheme=scan_scheme)
            if ref_metric_setting:
                metric_setting.codediff_scan_enabled = ref_metric_setting.codediff_scan_enabled
                metric_setting.cc_scan_enabled = ref_metric_setting.cc_scan_enabled
                metric_setting.min_ccn = ref_metric_setting.min_ccn
                metric_setting.cc = ref_metric_setting.cc
                metric_setting.dup_scan_enabled = ref_metric_setting.dup_scan_enabled
                metric_setting.dup_block_length_min = ref_metric_setting.dup_block_length_min
                metric_setting.dup_block_length_max = ref_metric_setting.dup_block_length_max
                metric_setting.dup_min_dup_times = ref_metric_setting.dup_min_dup_times
                metric_setting.dup_max_dup_times = ref_metric_setting.dup_max_dup_times
                metric_setting.dup_min_midd_rate = ref_metric_setting.dup_min_midd_rate
                metric_setting.dup_min_high_rate = ref_metric_setting.dup_min_high_rate
                metric_setting.dup_min_exhi_rate = ref_metric_setting.dup_min_exhi_rate
                metric_setting.dup_issue_limit = ref_metric_setting.dup_issue_limit
                metric_setting.cloc_scan_enabled = ref_metric_setting.cloc_scan_enabled
                metric_setting.core_file_path = ref_metric_setting.core_file_path
                metric_setting.file_mon_path = ref_metric_setting.file_mon_path
                metric_setting.save(user=user)

        if sync_all or kwargs.get("sync_filter_path_conf"):
            # 同步过滤路径配置
            # 拷贝扫描目录
            for scan_dir in ref_scan_dirs:
                try:
                    models.ScanDir.objects.get_or_create(
                        scan_scheme=scan_scheme, dir_path=scan_dir.dir_path,
                        scan_type=scan_dir.scan_type, path_type=scan_dir.path_type)
                except models.ScanDir.MultipleObjectsReturned:
                    pass
            # 同步默认路径屏蔽信息
            for exclude_path_map in ref_default_scan_exclude_paths:
                try:
                    models.SchemeDefaultScanPathExcludeMap.objects.get_or_create(
                        scan_scheme=scan_scheme, default_scan_path=exclude_path_map.default_scan_path,
                        defaults={"creator": exclude_path_map.creator}
                    )
                except models.SchemeDefaultScanPathExcludeMap.MultipleObjectsReturned:
                    pass
                except IntegrityError:
                    pass
        if sync_all or kwargs.get("sync_filter_other_conf"):
            # 同步过滤其他配置
            scan_scheme.ignore_merged_issue = ref_scheme.ignore_merged_issue
            scan_scheme.ignore_branch_issue = ref_scheme.ignore_branch_issue
            scan_scheme.ignore_submodule_clone = ref_scheme.ignore_submodule_clone
            scan_scheme.ignore_submodule_issue = ref_scheme.ignore_submodule_issue
            scan_scheme.issue_global_ignore = ref_scheme.issue_global_ignore
            scan_scheme.lfs_flag = ref_scheme.lfs_flag
        scan_scheme.save()

        # 创建权限，不做copy
        scan_scheme_perm, _ = models.ScanSchemePerm.objects.get_or_create(scan_scheme=scan_scheme,
                                                                          defaults={"creator": user})

    @classmethod
    def get_sync_message(cls, ref_scheme, **kwargs):
        """获取同步的配置信息
        """
        message = []
        if kwargs.get("sync_all"):
            message.append("全部配置")
        if kwargs.get("sync_basic_conf"):
            message.append("基础配置")
        if kwargs.get("sync_lint_rule_conf"):
            message.append("代码检查规则配置")
        if kwargs.get("sync_lint_build_conf"):
            message.append("代码检查编译配置")
        if kwargs.get("sync_metric_conf"):
            message.append("代码度量配置")
        if kwargs.get("sync_filter_path_conf"):
            message.append("过滤路径配置")
        if kwargs.get("sync_filter_other_conf"):
            message.append("过滤其他配置")
        return '【%s：%s】同步操作，同步项：%s' % ('分析方案' if ref_scheme.repo else '方案模板', ref_scheme, "、".join(message))

    @classmethod
    def create_scheme_with_template(cls, repo_id, scheme_template_data, languages, user=None, **kwargs):
        """通过模板创建扫描方案
        :param repo_id: int，代码库编号
        :param scheme_template_data: dict, 模板数据
        :param languages: list<Language>, 语言列表
        :param user: User，用户
        :return: ScanScheme
        """
        refer_template_ids = kwargs.get("refer_template_ids")
        name = kwargs.get("name") or scheme_template_data.pop("name")
        scan_scheme = cls.init_scheme(repo_id, name=name,
                                      user=user, refer_template_ids=refer_template_ids)
        cls.update_scheme_basic_conf(scan_scheme, user=user, **{"tag": scheme_template_data["tag"],
                                                                "languages": languages,
                                                                **scheme_template_data["basic_conf"]})
        labels = models.ScanConfLabel.objects.filter(name__in=scheme_template_data["labels"])

        cls.update_scheme_lint_settings(scan_scheme, user=user, **{"labels": labels,
                                                                   **scheme_template_data["lint_conf"]})
        cls.update_scheme_metric_setting(scan_scheme, user=user, **scheme_template_data["metric_conf"])
        cls.update_scheme_checkprofile_custom_package(scan_scheme, user, scheme_template_data["profile_conf"])
        return scan_scheme

    @classmethod
    def update_scheme_basic_conf(cls, scan_scheme, user=None, **kwargs):
        """更新扫描方案基础配置
        """
        # 设置扫描语言
        if kwargs.get("languages"):
            cls.update_languages(scan_scheme, kwargs["languages"])
        # 设置执行节点
        if kwargs.get("tag"):
            scan_scheme.tag = kwargs["tag"]
        scan_scheme.name = kwargs.get("name", scan_scheme.name)
        scan_scheme.description = kwargs.get("description", scan_scheme.description)
        scan_scheme.refer_scheme = kwargs.get("refer_scheme", scan_scheme.refer_scheme)
        scan_scheme.refer_template_ids = kwargs.get("refer_template_ids", scan_scheme.refer_template_ids)
        scan_scheme.created_from = kwargs.get("created_from", scan_scheme.created_from)
        scan_scheme.issue_global_ignore = kwargs.get("issue_global_ignore", scan_scheme.issue_global_ignore)
        scan_scheme.ignore_merged_issue = kwargs.get("ignore_merged_issue", scan_scheme.ignore_merged_issue)
        scan_scheme.ignore_branch_issue = kwargs.get("ignore_branch_issue", scan_scheme.ignore_branch_issue)
        scan_scheme.ignore_submodule_clone = kwargs.get("ignore_submodule_clone", scan_scheme.ignore_submodule_clone)
        scan_scheme.ignore_submodule_issue = kwargs.get("ignore_submodule_issue", scan_scheme.ignore_submodule_issue)
        scan_scheme.lfs_flag = kwargs.get("lfs_flag", scan_scheme.lfs_flag)
        scan_scheme.save(user=user)
        return scan_scheme

    @classmethod
    def get_scan_dirs_with_scheme(cls, scan_scheme):
        """获取指定扫描方案的扫描目录
        :param scan_scheme:
        :return:
        """
        return models.ScanDir.objects.filter(scan_scheme=scan_scheme)

    @classmethod
    def get_path_list_with_scheme(cls, scan_scheme, path_type, scan_type):
        """获取指定扫描方案指定类型的路径列表
        """
        path_list = list(models.ScanDir.objects.filter(
            scan_scheme=scan_scheme, scan_type=scan_type, path_type=path_type
        ).values_list("dir_path", flat=True))
        if scan_type == models.ScanDir.ScanTypeEnum.EXCLUDE:
            path_list += list(models.DefaultScanPath.objects.exclude(
                schemedefaultscanpathexcludemap__scan_scheme=scan_scheme
            ).filter(
                path_type=path_type
            ).values_list("dir_path", flat=True))
        return path_list

    @classmethod
    def get_scheme_with_repo(cls, repo, user=None):
        """获取指定代码库下的扫描方案
        排序：默认方案在最前面，新创建的在最前面
        """
        if user:
            return models.ScanScheme.user_objects(user).filter(
                repo=repo, status=models.ScanScheme.StatusEnum.ACTIVE).order_by("-default_flag", "-id")
        else:
            return models.ScanScheme.objects.filter(
                repo=repo, status=models.ScanScheme.StatusEnum.ACTIVE).order_by("-default_flag", "-id")

    @classmethod
    def create_scheme_lint_setting(cls, scan_scheme, user=None, **lint_setting_data):
        """创建指定扫描方案的代码扫描配置

        :param scan_scheme: ScanScheme，扫描方案
        :param user: User，创建人
        :return: ScanScheme
        """
        return models.LintBaseSetting.objects.create(scan_scheme=scan_scheme, user=user, **lint_setting_data)

    @classmethod
    def update_scheme_lint_settings(cls, scan_scheme, user=None, **lint_setting_data):
        """ 更新指定扫描方案的代码扫描配置
        :param scan_scheme: ScanScheme，扫描方案
        :param user: User，更新人
        :param lint_setting_data: dict，扫描配置
        """
        lint_setting, _ = models.LintBaseSetting.objects.get_or_create(
            scan_scheme=scan_scheme, defaults={"creator": user})
        lint_setting.enabled = lint_setting_data.get("lint_enabled") or lint_setting_data.get("enabled")
        lint_setting.pre_cmd = lint_setting_data.get("pre_cmd")
        lint_setting.build_cmd = lint_setting_data.get("build_cmd")
        lint_setting.envs = lint_setting_data.get("envs")
        # 设置扫描规则集
        logger.info("[Scheme: %s] 当前标签列表为: %s" % (scan_scheme.id, list(lint_setting_data.get("labels", []))))
        if not lint_setting.checkprofile:
            lint_setting.checkprofile = cls.create_default_check_profile(
                scan_scheme, user=user, labels=lint_setting_data.get("labels"))
        lint_setting.save(user=user)
        return lint_setting

    @classmethod
    def create_scheme_scan_dirs(cls, scan_scheme, scan_dirs):
        """更新指定扫描方案的扫描目录

        :param scan_scheme: ScanScheme，扫描方案
        :param scan_dirs: list，扫描目录
        """
        for scan_dir in scan_dirs:
            models.ScanDir.objects.create(
                scan_scheme=scan_scheme, **scan_dir)

    @classmethod
    def create_scheme_metric_setting(cls, scan_scheme, user=None, **metric_setting_data):
        """更新指定扫描方案的代码扫描配置

        :param scan_scheme: ScanScheme，扫描方案
        :param user: User，更新人
        :return: ScanScheme
        """
        return models.MetricSetting.objects.create(scan_scheme=scan_scheme, user=user, **metric_setting_data)

    @classmethod
    def update_scheme_metric_setting(cls, scan_scheme, user=None, **metric_setting_data):
        """更新指定扫描方案的代码度量配置

        :param scan_scheme:
        :param user: User，更新人
        :param metric_setting_data:
        :return:
        """
        metric_setting, _ = models.MetricSetting.objects.get_or_create(scan_scheme=scan_scheme,
                                                                       defaults={"creator": user})
        metric_setting.codediff_scan_enabled = metric_setting_data.get("codediff_scan_enabled",
                                                                       metric_setting.codediff_scan_enabled)
        metric_setting.cc_scan_enabled = metric_setting_data.get("cc_scan_enabled", metric_setting.cc_scan_enabled)
        metric_setting.min_ccn = metric_setting_data.get("min_ccn", metric_setting.min_ccn)
        metric_setting.cc = metric_setting_data.get("cc", metric_setting.cc)
        metric_setting.dup_scan_enabled = metric_setting_data.get("dup_scan_enabled", metric_setting.dup_scan_enabled)
        metric_setting.dup_block_length_min = metric_setting_data.get("dup_block_length_min",
                                                                      metric_setting.dup_block_length_min)
        metric_setting.dup_block_length_max = metric_setting_data.get("dup_block_length_max",
                                                                      metric_setting.dup_block_length_max)
        metric_setting.dup_min_dup_times = metric_setting_data.get("dup_min_dup_times",
                                                                   metric_setting.dup_min_dup_times)
        metric_setting.dup_max_dup_times = metric_setting_data.get("dup_max_dup_times",
                                                                   metric_setting.dup_max_dup_times)
        metric_setting.dup_min_midd_rate = metric_setting_data.get("dup_min_midd_rate",
                                                                   metric_setting.dup_min_midd_rate)
        metric_setting.dup_min_high_rate = metric_setting_data.get("dup_min_high_rate",
                                                                   metric_setting.dup_min_high_rate)
        metric_setting.dup_min_exhi_rate = metric_setting_data.get("dup_min_exhi_rate",
                                                                   metric_setting.dup_min_exhi_rate)
        metric_setting.dup_issue_limit = metric_setting_data.get("dup_issue_limit", metric_setting.dup_issue_limit)
        metric_setting.cloc_scan_enabled = metric_setting_data.get("cloc_scan_enabled",
                                                                   metric_setting.cloc_scan_enabled)
        metric_setting.core_file_path = metric_setting_data.get("core_file_path",
                                                                metric_setting.core_file_path)
        metric_setting.file_mon_path = metric_setting_data.get("file_mon_path",
                                                               metric_setting.file_mon_path)
        metric_setting.save(user)

    @classmethod
    def update_scheme_checkprofile_custom_package(cls, scan_scheme, user, profile_conf):
        """更新指定扫描方案的自定义规则配置
        """
        lint_setting, _ = models.LintBaseSetting.objects.get_or_create(scan_scheme=scan_scheme,
                                                                       defaults={"creator": user})
        checkprofile = lint_setting.checkprofile
        custom_checkpackage = checkprofile.custom_checkpackage
        profile_conf_dict = {item["checkrule_id"]: item for item in profile_conf}
        checkrule_dict = {item.id: item for item in
                          CheckRuleManager.all().filter(id__in=list(profile_conf_dict.keys()))}
        add_checkrules_to_checkpackage(custom_checkpackage, list(checkrule_dict.values()), user=user)
        for rule_id, checkrule_dict in profile_conf_dict.items():
            packagemap = PackageMap.objects.filter(checkpackage=custom_checkpackage, checkrule_id=rule_id).first()
            if packagemap:
                packagemap.severity = checkrule_dict.get('severity', packagemap.severity)
                packagemap.rule_params = checkrule_dict.get('rule_params', packagemap.rule_params)
                packagemap.state = checkrule_dict.get('state', packagemap.state)
                packagemap.save()

    @classmethod
    def check_scheme_usable_permission(cls, scan_scheme, user):
        """检查当前用户是否有指定扫描方案的使用权限
        """
        if user.is_superuser:
            return True
        schemeperm = models.ScanSchemePerm.objects.filter(scan_scheme=scan_scheme).first()
        if schemeperm and schemeperm.execute_scope == models.ScanSchemePerm.ScopeEnum.PRIVATE \
                and not schemeperm.check_user_execute_manager_perm(user):
            return False
        return True


class ScanSchemeTemplateManager(object):
    """扫描方案模版管理
    1. 模板本身管理：编辑和更新
    2. 通过模板创建扫描方案
    """

    @classmethod
    def update_labels(cls, scheme_template, labels):
        """更新指定扫描模板的标签列表
        :param scheme_template: ScanSchemeTemplate
        :param labels: list<Lable> 标签列表
        """
        scheme_template.labels.add(*labels)
        label_names = [label.name for label in labels]
        remove_labels = scheme_template.labels.exclude(name__in=label_names)
        scheme_template.labels.remove(*remove_labels)

    @classmethod
    def update_owners(cls, scheme_template, owners):
        """更新指定扫描模板的负责人列表
        :param scheme_template: ScanSchemeTemplate
        :param owners: list<User> 用户列表
        """
        scheme_template.owners.add(*owners)
        owner_usernames = [owner.username for owner in owners]
        remove_owners = scheme_template.owners.exclude(username__in=owner_usernames)
        scheme_template.owners.remove(*remove_owners)

    @classmethod
    def create_scheme_template(cls, scheme_template_data, owners, creator):
        """创建方案模板
        """
        name = scheme_template_data.get("name")
        display_name = scheme_template_data.get("display_name")
        public = scheme_template_data.get("public")
        recommend = scheme_template_data.get("recommend")
        need_compile = scheme_template_data.get("need_compile")
        basic_conf_data = scheme_template_data["basic_conf"] if scheme_template_data.get("basic_conf") else {}
        lint_conf_data = scheme_template_data["lint_conf"] if scheme_template_data.get("lint_conf") else {}
        metric_conf_data = scheme_template_data["metric_conf"] if scheme_template_data.get("metric_conf") else {}
        basic_conf = models.ScanScheme.get_basic_conf_template()
        basic_conf.update(**basic_conf_data)
        lint_conf = models.LintBaseSetting.get_lint_conf_template()
        lint_conf.update(**lint_conf_data)
        metric_conf = models.MetricSetting.get_metric_conf_template()
        metric_conf.update(**metric_conf_data)

        scheme_template = models.ScanSchemeTemplate.objects.create(
            name=name,
            display_name=display_name,
            public=public,
            recommend=recommend,
            need_compile=need_compile,
            short_desc=scheme_template_data.get("short_desc"),
            description=scheme_template_data.get("description"),
            tag=scheme_template_data.get("tag"),
            basic_conf=json.dumps(basic_conf),
            lint_conf=json.dumps(lint_conf),
            metric_conf=json.dumps(metric_conf),
            creator=creator
        )
        scheme_template.checkprofile = CheckProfileManager.create_temp_checkprofile(scheme_template, creator)
        scheme_template.save()
        cls.update_owners(scheme_template, owners)
        cls.update_labels(scheme_template, scheme_template_data.get("labels"))
        cls.update_scheme_template_checkprofile(scheme_template, scheme_template_data.get("checkrule_list", []),
                                                creator)
        return scheme_template

    @classmethod
    def update_scheme_template(cls, scheme_template, scheme_template_data, owners, user):
        """更新指定扫描方案模板
        """
        scheme_template.name = scheme_template_data.get("name", scheme_template.name)
        scheme_template.display_name = scheme_template_data.get("display_name", scheme_template.display_name)
        scheme_template.tag = scheme_template_data.get("tag", scheme_template.tag)
        scheme_template.public = scheme_template_data.get("public", scheme_template.public)
        scheme_template.recommend = scheme_template_data.get("recommend", scheme_template.recommend)
        scheme_template.short_desc = scheme_template_data.get("short_desc", scheme_template.short_desc)
        scheme_template.description = scheme_template_data.get("description", scheme_template.description)
        cls.update_owners(scheme_template, owners)
        cls.update_labels(scheme_template, scheme_template_data.get("labels"))
        basic_conf_data = scheme_template_data.get("basic_conf") or {}
        lint_conf_data = scheme_template_data.get("lint_conf") or {}
        metric_conf_data = scheme_template_data.get("metric_conf") or {}
        basic_conf = json.loads(scheme_template.basic_conf)
        basic_conf.update(**basic_conf_data)
        scheme_template.basic_conf = json.dumps(basic_conf)
        lint_conf = json.loads(scheme_template.lint_conf)
        lint_conf.update(**lint_conf_data)
        scheme_template.lint_conf = json.dumps(lint_conf)
        metric_conf = json.loads(scheme_template.metric_conf)
        metric_conf.update(**metric_conf_data)
        scheme_template.metric_conf = json.dumps(metric_conf)
        if not scheme_template.checkprofile:
            scheme_template.checkprofile = CheckProfileManager.create_temp_checkprofile(scheme_template, user)
        scheme_template.save(user=user)
        cls.update_scheme_template_checkprofile(scheme_template, scheme_template_data.get("checkrule_list", []), user)
        return scheme_template

    @classmethod
    def update_scheme_template_checkprofile(cls, scheme_template, checkrule_list, user):
        """更新扫描方案模板的规则集
        """
        checkprofile = scheme_template.checkprofile
        custom_checkpackage = checkprofile.custom_checkpackage
        checkrules = [
            checkrule_dict.get("checkrule") for checkrule_dict in checkrule_list]
        # 规则添加到自定义规则包
        add_checkrules_to_checkpackage(custom_checkpackage, checkrules, user=user)
        # 修改packagemap
        for checkrule_dict in checkrule_list:
            checkrule = checkrule_dict.pop("checkrule")
            packagemap = PackageMap.objects.filter(
                checkpackage=custom_checkpackage, checkrule=checkrule).first()
            if packagemap:
                packagemap.severity = checkrule_dict.get('severity', packagemap.severity)
                packagemap.rule_params = checkrule_dict.get('rule_params', packagemap.rule_params)
                packagemap.state = checkrule_dict.get('state', packagemap.state)
                packagemap.save()

    @classmethod
    def merge_scheme_template(cls, scheme_template_data_list):
        """合并扫描方案模板
        用户选择多个方案模板时，会自动将这批模板自动合并形成一个新的自定义模板
        """
        if len(scheme_template_data_list) == 0:
            return None
        if len(scheme_template_data_list) == 1:
            return scheme_template_data_list[0].to_dict()

        scheme_template_data = scheme_template_data_list[0].to_dict()
        for item in scheme_template_data_list[1:]:
            item = item.to_dict()
            scheme_template_data["name"] += "_%s" % item["name"]
            scheme_template_data["labels"] += item["labels"]
            scheme_template_data["basic_conf"] = models.ScanScheme.merge_basic_conf_template(
                scheme_template_data["basic_conf"], item["basic_conf"])
            scheme_template_data["lint_conf"] = models.LintBaseSetting.merge_lint_conf_template(
                scheme_template_data["lint_conf"], item["lint_conf"]
            )
            scheme_template_data["metric_conf"] = models.MetricSetting.merge_metric_conf_template(
                scheme_template_data["metric_conf"], item["metric_conf"]
            )
            scheme_template_data["profile_conf"] = cls.merge_scheme_template_checkpackage_content(
                scheme_template_data["profile_conf"], item["profile_conf"])
        logger.info("[SchemeTemplate]合并后的方案模板参数为 %s" % scheme_template_data)
        return scheme_template_data

    @classmethod
    def merge_scheme_template_checkpackage_content(cls, custom_package_content_1, custom_package_content_2):
        """合并两份规则集
        """
        custom_package_content_dict_1 = {str(item["checkrule_id"]): item for item in custom_package_content_1}
        custom_package_content_dict_2 = {str(item["checkrule_id"]): item for item in custom_package_content_2}

        for checkrule_id, checkrule in custom_package_content_dict_1.items():
            if custom_package_content_dict_2.get(checkrule_id):
                checkrule_2 = custom_package_content_dict_2.pop(checkrule_id)
                if checkrule["severity"] > checkrule_2["severity"]:
                    checkrule["severity"] = checkrule_2["severity"]
                if checkrule["state"] == PackageMap.StateEnum.ENABLED:
                    checkrule["state"] = checkrule_2["state"]

        custom_package_content_dict_1.update(**custom_package_content_dict_2)
        return list(custom_package_content_dict_1.values())


class ScanSchemePermManager(object):
    """扫描方案权限管理
    """

    @classmethod
    def check_user_view_perm(cls, scan_scheme, user, org_sid=None):
        """检查指定用户是否有查看权限
        """
        # 系统模板都具备查看权限
        if scan_scheme.scheme_key and scan_scheme.scheme_key == scan_scheme.SchemeKey.PUBLIC:
            return True
        org_scheme_key = scan_scheme.get_org_scheme_key(org_sid)
        # 非系统模板，即自定义模板
        if scan_scheme.scheme_key and scan_scheme.scheme_key == org_scheme_key:
            if scan_scheme.scanschemeperm.execute_scope == models.ScanSchemePerm.ScopeEnum.OPEN:
                return True
            elif cls.check_user_edit_manager_perm(scan_scheme, user) or \
                    cls.check_user_execute_manager_perm(scan_scheme, user):
                # 团队内私有模板，校验用户是否具备权限。
                return True
        return False

    @classmethod
    def check_user_edit_manager_perm(cls, scan_scheme, user):
        """检查指定用户是否有可编辑的维护权限
        """
        if user and user.is_superuser:
            return True
        elif user and scan_scheme.scanschemeperm.edit_managers.filter(username=user.username).exists():
            return True
        else:
            return False

    @classmethod
    def check_user_execute_manager_perm(cls, scan_scheme, user):
        """检查指定用户是否有可执行的维护权限
        """
        if user and user.is_superuser:
            return True
        elif user and scan_scheme.scanschemeperm.execute_managers.filter(username=user.username).exists():
            return True
        else:
            return False


class ProjectManager(object):
    """项目管理
    """

    @classmethod
    def format_scan_path(cls, scan_path):
        """格式化scan_path
        """
        scan_path = scan_path.strip()
        if not scan_path or scan_path == "/" or scan_path == "./":
            scan_path = "/"
        elif scan_path.startswith("./"):
            scan_path = scan_path[2:].strip("/")
        else:
            scan_path = scan_path.strip("/")
        return scan_path

    @classmethod
    def create_project(cls, repo, scan_scheme, branch, scan_path=None, **kwargs):
        """创建项目
        """
        if not scan_path:
            scan_path = "/"
        else:
            scan_path = cls.format_scan_path(scan_path)

        project_key = models.Project.gen_project_key(
            repo_id=repo.id, scheme_id=scan_scheme.id, branch=branch, scan_path=scan_path)
        project, created = models.Project.objects.get_or_create(
            project_key=project_key,
            defaults={
                "repo_id": repo.id,
                "branch": branch,
                "scan_scheme_id": scan_scheme.id,
                "scan_path": scan_path,
                "creator": kwargs.get("creator"),
                "created_from": kwargs.get("created_from") or models.Project.CreatedFromEnum.WEB,
                "refer_project": kwargs.get("refer_project"),
            })
        return project, created

    @classmethod
    def create_project_on_analysis_server(cls, project, user):
        """在Analysis服务器创建项目
        """
        try:
            AnalyseClient().api('create_project', data={
                "id": project.id,
                "repo_id": project.repo_id,
                "scan_scheme_id": project.scan_scheme_id,
                "scan_path": project.scan_path,
                "creator": user.username,
                "scm_type": project.scm_type,
                "scm_url": project.scm_url,
                "org_sid": project.repo.organization.org_sid if project.repo.organization else None,
                "team_name": project.repo.project_team.name if project.repo.project_team else None,
            })
        except Exception as err:
            logger.exception("create project on analysis server failed: %s" % str(err))
            raise ProjectCreateError("创建分支项目失败，请稍后重试")

    @classmethod
    def delete_project(cls, repo_id, project_id, user):
        """删除代码库
        """
        project = models.Project.objects.filter(id=project_id, repo_id=repo_id).first()
        if not project:
            raise ServerOperationError("分支项目[%s-%s]不存在" % (repo_id, project_id))
        project_str = str(project)
        old_project_key = project.project_key
        project.project_key = None
        project.status = models.Project.StatusEnum.DISACTIVE
        project.update_remark({"project_key": old_project_key})
        project.save()
        logger.info("[User: %s] 在 %s 删除了 %s 分支项目" % (user.username, now(), project))
        project.delete(user=user)
        OperationRecordHandler.add_project_operation_record(
            project, "删除分支项目", user.username, message="删除分支项目: %s" % project_str
        )

    @classmethod
    def filter_disactive_projects(cls, queries):
        """筛选失活项目
        """
        return models.Project.objects.filter(status=models.Project.StatusEnum.DISACTIVE).filter(**queries)

    @classmethod
    def filter_deleted_projects(cls, queries):
        """筛选已删除的项目
        """
        return models.Project.everything.filter(deleted_time__isnull=False).filter(**queries)
