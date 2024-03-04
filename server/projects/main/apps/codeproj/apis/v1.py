# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - v1 apis
"""
# python 原生import
import json
import logging
from urllib.parse import urlencode

# 第三方 import
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, ParseError, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

# 项目内 import
from apps.authen.backends import TCANodeTokenBackend
from apps.authen.core import UserManager
from apps.codeproj import core, models
from apps.codeproj.api_filters import base as base_filters
from apps.codeproj.apimixins import ProjectBaseAPIView
from apps.codeproj.serializers import base as serializers
from util.authticket import ServerInternalTicket
from util.exceptions import CDErrorBase
from util.httpclient import HttpClient
from util.operationrecord import OperationRecordHandler
from util.permissions import RepositoryPermission, RepositoryProjectPermission
from util.webclients import AnalyseClient

logger = logging.getLogger(__name__)


class AnalyseServerProxyApi(APIView):
    """转发到Analyse Server的Api接口，具体文档请查看Analyse Server域名下相同的url文档
    使用对象：节点

    """
    schema = None
    authentication_classes = [TCANodeTokenBackend]

    def action(self, request, **kwargs):
        url = "%s%s" % (settings.ANALYSE_SERVER_URL, request.path_info)
        if request.query_params:
            params = urlencode(request.query_params)
            url = "%s?%s" % (url, params)
        headers = {"SERVER-TICKET": ServerInternalTicket.generate_ticket(),
                   "CONTENT-TYPE": "application/json"}
        logger.debug("转发到：%s" % url)
        if request.method == "GET":
            rsp = HttpClient().get(url, headers=headers)
        elif request.method == "POST":
            data = request.data or {}
            rsp = HttpClient().post(url, data=data, headers=headers)
        else:
            raise Exception("Unsupported request method.")
        return HttpResponse(
            content=rsp.data,
            status=rsp.status,
            content_type=rsp.headers["Content-Type"],
        )

    def get(self, request, **kwargs):
        return self.action(request, **kwargs)

    def post(self, request, **kwargs):
        return self.action(request, **kwargs)


class ScanDirListApiView(generics.ListCreateAPIView):
    """扫描目录列表接口
    使用对象：节点

    ### GET
    应用场景：获取扫描目录列表
    >参数：无

    ### POST
    应用场景：新增扫描目录列表
    >参数：
    >> project: 项目id，需要与url中的project id一致

    >> dir_path: 目录，格式参考python fnmatch语法

    >> scan_type: 1表示包含（include），2表示过滤（exclude）
    """
    schema = None
    authentication_classes = [TCANodeTokenBackend]
    serializer_class = serializers.ScanDirSerializer

    def get_queryset(self):
        project = get_object_or_404(
            models.Project, id=self.kwargs["project_id"])
        return models.ScanDir.objects.filter(scan_scheme=project.scan_scheme)

    def perform_create(self, serializer):
        project = get_object_or_404(
            models.Project, id=self.kwargs["project_id"])
        exist_count = models.ScanDir.objects.filter(
            scan_scheme=project.scan_scheme, dir_path=serializer.validated_data["dir_path"]).count()
        if exist_count > 0:
            raise ParseError("创建失败，目录已存在，如需修改请调用修改接口。")
        OperationRecordHandler.add_scanscheme_operation_record(
            project.scan_scheme, "通过接口新增过滤目录", self.request.user, serializer.validated_data)
        serializer.save()


class ProjectConfApiView(generics.GenericAPIView, ProjectBaseAPIView):
    """项目扫描配置接口
    使用对象：节点

    ### Get
    应用场景：获取项目的代码功能配置
    """
    schema = None
    authentication_classes = [TCANodeTokenBackend]

    def get(self, request, **kwargs):
        project = self.get_project()
        if project.scan_scheme:
            metric_setting = core.ScanSchemeManager.get_metric_setting(
                project.scan_scheme)
            obj = {
                "lint_scan_enabled": core.ScanSchemeManager.get_lint_setting(project.scan_scheme).enabled,
                "cc_scan_enabled": metric_setting.cc_scan_enabled,
                "dup_scan_enabled": metric_setting.dup_scan_enabled,
                "cloc_scan_enabled": metric_setting.cloc_scan_enabled
            }
        else:
            obj = {
                "lint_scan_enabled": False,
                "cc_scan_enabled": False,
                "dup_scan_enabled": False,
                "cloc_scan_enabled": False
            }
        obj.update({"url": "%s/repos/%d/schemes/%d/info" %
                           (settings.LOCAL_DOMAIN, project.repo_id, project.scan_scheme_id)})
        return Response(obj)


class ProjectScanJobConfApiView(generics.GenericAPIView):
    """获取项目扫描配置
    使用对象：节点

    ### GET
    应用场景：获取项目扫描配置的api，供节点端离线扫描使用

    ### POST
    应用场景：创建新的扫描任务
    参数：
    ```json
    {
        "tasks": [
            {
                "task_version": "1.0",
                "module_name": "codelint",
                "tag": "test",
                "processes": ["analyse","build","handledata"],
                "task_name": "pylint",
                "task_params": {
                    "scan_languages": [
                        "js"
                    ],
                    "scm_last_revision": "123"
                },
                "result_code": 0,
                "result_msg": 1,
                "result_data_url": "http://your-result-data-path",
                "log_url": "http://your-log-path",
                "finished_processes": ["build","analyse"],
                "private_processes": ["handledata"],
                "progress_rate": 90
            }
        ],
        "job_context": {
            "scm_revision": "346688",
            "scan_type": 1,
            "scm_url": "http://local-project-scm-host/local/scm/path",
            "scm_type": "svn",
            "project_id": 1,
            "incr_scan": true,
            "code_line_num": 12,
            "comment_line_num": 12,
            "blank_line_num": 12,
            "total_line_num": 12,
            "start_time": "2019-10-10 01:01:01",
            "time_format": "%Y-%m-%d %H:%M:%S",
            "created_from": "api",
        }
    }
    ```
    job_context中scm_revision, scm_url, scan_type为必填。

    scan_type: 扫描类型,仅作扫描标识处理.**1增量扫描，2全量扫描，3合流任务
    """
    schema = None
    authentication_classes = [TCANodeTokenBackend]
    serializer_class = serializers.ScanJobCreateSerializer

    def get(self, request, *args, **kwargs):
        project = get_object_or_404(models.Project, id=kwargs["project_id"])
        languages = request.query_params.get("languages")
        labels = request.query_params.get("labels")
        job_manager = core.JobManager(project)
        try:
            return Response(job_manager.get_job_confs(languages=languages, labels=labels))
        except CDErrorBase as e:
            return Response({"errcode": e.code,
                             "errmsg": e.msg},
                            status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        project = get_object_or_404(models.Project, id=kwargs["project_id"])
        if not request.user.is_superuser:
            schemeperm = models.ScanSchemePerm.objects.filter(scan_scheme=project.scan_scheme).first()
            if schemeperm and schemeperm.execute_scope == models.ScanSchemePerm.ScopeEnum.PRIVATE \
                    and not schemeperm.check_user_execute_manager_perm(request.user):
                logger.error("本地扫描/CI流水线，代码库内创建分支项目/启动分支项目扫描无权限：%s" %
                             UserManager.get_username(request.user))
                raise PermissionDenied("您没有执行该操作的权限，该扫描方案已私有化，您不在该方案权限配置的关联分支项目权限成员列表中！！！")
        slz = self.get_serializer(data=request.data)
        if slz.is_valid(raise_exception=True):
            logger.info("参数校验通过，开始创建任务，参数如下：")
            logger.info(json.dumps(request.data, indent=4))
            try:
                job_id, scan_id = core.create_job(
                    project, slz.validated_data, creator=UserManager.get_username(request.user),
                    puppy_create=True, scan_type=slz.validated_data.get("scan_type"))
                return Response({"job": {"id": job_id},
                                 "scan": {"id": scan_id}})
            except CDErrorBase as e:
                return Response(e.data, status=status.HTTP_400_BAD_REQUEST)


class ScanSchemeScanJobConfApiView(generics.GenericAPIView):
    """获取指定扫描方案模板扫描配置
    使用对象：节点

    ### GET
    应用场景：获取指定扫描方案模板扫描配置信息，供节点端离线扫描使用
    """
    schema = None
    authentication_classes = [TCANodeTokenBackend]

    def get(self, request, *args, **kwargs):
        scan_scheme = get_object_or_404(models.ScanScheme, id=kwargs["scheme_id"], repo=None)
        job_manager = core.JobManager(project=None)
        try:
            return Response(job_manager.get_job_confs(scan_scheme=scan_scheme))
        except CDErrorBase as e:
            return ParseError({"errcode": e.code, "errmsg": e.msg})


class ProjectScanDetailApiView(generics.GenericAPIView, ProjectBaseAPIView):
    """项目指定扫描详情接口
    使用对象：节点

    ### Get
    应用场景：获取扫描结果
    """
    schema = None
    authentication_classes = [TCANodeTokenBackend]

    def get(self, request, scan_id, **kwargs):
        project = self.get_project()
        try:
            result = AnalyseClient().api(
                "get_scan", data=None, path_params=(project.id, scan_id))
            return Response(result)
        except CDErrorBase as e:
            return Response(e.data, status=status.HTTP_400_BAD_REQUEST)


class DefaultScanPathListApiView(generics.ListAPIView):
    """
    使用对象：节点

    ### Get
    应用场景：获取平台默认过滤路径
    """
    schema = None
    authentication_classes = [TCANodeTokenBackend]
    serializer_class = serializers.DefaultScanPathSerializer
    queryset = models.DefaultScanPath.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        slz = self.get_serializer(queryset, many=True)
        return Response(slz.data)


class ProjectScanSchemeDefaultScanPathListApiView(generics.ListAPIView):
    """
    使用对象：节点

    ### Get
    应用场景：获取项目的默认过滤路径配置
    """
    schema = None
    authentication_classes = [TCANodeTokenBackend]
    serializer_class = serializers.DefaultScanPathSerializer

    def get_exclude_paths(self):
        """获取过滤参数
        """
        exclude = self.request.query_params.get("exclude")
        try:
            if int(exclude) == 1:
                return True
            else:
                return False
        except Exception as err:
            logger.warning("convert exclude params error: %s" % err)
            return False

    def get_queryset(self):
        project = get_object_or_404(models.Project, id=self.kwargs["project_id"])
        if project.scan_scheme:
            if self.get_exclude_paths():
                # 筛选屏蔽的默认路径
                default_scan_paths = models.DefaultScanPath.objects.filter(
                    schemedefaultscanpathexcludemap__scan_scheme=project.scan_scheme)
            else:
                # 筛选未屏蔽的默认路径
                default_scan_paths = models.DefaultScanPath.objects.exclude(
                    schemedefaultscanpathexcludemap__scan_scheme=project.scan_scheme)
        else:
            raise NotFound({"cd_error": "未找到对应扫描方案"})
        return default_scan_paths

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        slz = self.get_serializer(queryset, many=True)
        return Response(slz.data)


class RepoBranchListApiView(generics.ListAPIView, ProjectBaseAPIView):
    """指定代码库已接入的分支列表接口

    ### GET
    应用场景：获取指定代码库分支列表
    """

    permission_classes = [RepositoryPermission]
    serializer_class = serializers.ScanBranchSerializer

    def get_scheme_status(self, request):
        """获取扫描方案状态筛选参数
        """
        scheme_status = request.query_params.get("scheme_status")
        if scheme_status is not None:
            try:
                return int(scheme_status)
            except Exception as err:
                logger.warning("get scheme status error: %s" % err)
                return None
        else:
            return None

    def get_queryset(self):
        repo = self.get_repo()
        scheme_status = self.get_scheme_status(self.request)
        projects = models.Project.objects.select_related("scan_scheme").filter(repo_id=repo.id)
        if scheme_status is not None:
            projects = projects.filter(scan_scheme__status=scheme_status)
        return projects.values("branch").distinct()


class RepositorySchemesInfoApiView(generics.GenericAPIView):
    """查询指定代码指定扫描方案是否存在

    ### GET
    应用场景：查询指定代码指定扫描方案是否存在
    > * 查询参数：
    >     - scm_url: 代码库地址
    >     - scan_scheme__name: 扫描方案名称
    > * 结果数据：

    ```python
    {
        {
            "id": 1, # 扫描方案编号
            "name": "扫描方案名称（展示名称）",
            "default_flag": true # true表示为默认方案，false表示为非默认方案
            # ...
        },
        ...
    }
    ```
    """

    def get_repo_with_url(self, scm_url, **kwargs):
        """通过代码库链接获取代码库
        """
        return core.RepositoryManager.find_repository(scm_url)

    def get_repo_scheme(self, scm_url, scan_scheme_name, **kwargs):
        """获取代码库指定扫描扫描方案
        :param scm_url: str，代码库地址
        :param scan_scheme_name: str, 扫描方案名称
        :return: list, 方案列表
        """
        if not scm_url:
            raise ParseError({"cd_error": "代码库地址scm_url参数不能为空"})
        repo = self.get_repo_with_url(scm_url, **kwargs)
        logger.info("查询代码库地址: %s, repo: %s" % (scm_url, repo))
        if not repo:
            raise NotFound({"cd_error": "%s不存在" % scm_url})
        # 当扫描方案名称存在时，查询指定扫描方案，不存在时则返回默认扫描方案
        if scan_scheme_name:
            scheme = core.ScanSchemeManager.get_scheme_with_repo(repo.id).filter(name=scan_scheme_name).first()
        else:
            scheme = core.ScanSchemeManager.get_scheme_with_repo(repo.id).filter(default_flag=True).first()
        if scheme:
            return serializers.ScanSchemeSimpleSerializer(scheme).data
        else:
            raise NotFound({"cd_error": "%s的扫描方案%s不存在" % (scm_url, scan_scheme_name)})

    def get(self, request, **kwargs):
        scm_url = request.query_params.get("scm_url")
        scan_scheme_name = request.query_params.get("scan_scheme_name")
        scheme = self.get_repo_scheme(scm_url, scan_scheme_name, **kwargs)
        return Response(data=scheme)


class ProjectListCreateView(generics.ListCreateAPIView):
    """项目列表接口

    ### Get
    应用场景：获取项目列表

    ### Post
    应用场景：创建一个项目 + 初始化配置
    """
    serializer_class = serializers.APIProjectsSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = base_filters.ApiProjectFilter

    def get_queryset(self):
        logger.info("[User: %s] find project: %s" % (self.request.user, self.request.query_params))
        return models.Project.objects.all().order_by("-id")


class ProjectDetailApiView(generics.RetrieveAPIView, ProjectBaseAPIView):
    """项目详情接口

    ### Get
    应用场景：获取项目详情
    """
    permission_classes = [RepositoryProjectPermission]
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSimpleSerializer

    def get_object(self):
        return self.get_project()


class ProjectScanSchemeDetailApiView(generics.RetrieveAPIView, ProjectBaseAPIView):
    """项目扫描方案详情接口

    ### Get
    应用场景：获取项目扫描方案详情
    """
    permission_classes = [RepositoryProjectPermission]
    serializer_class = serializers.ScanSchemeSerializer

    def get_object(self):
        project = self.get_project()
        return project.scan_scheme
