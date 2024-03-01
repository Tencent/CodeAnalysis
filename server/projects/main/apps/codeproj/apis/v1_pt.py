# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - api v1 for project_team
"""
# python 原生import
import logging

# 第三方 import
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics

# 项目内 import
from apps.authen.backends import TCANodeTokenBackend
from apps.base.apimixins import CustomSerilizerMixin
from apps.codeproj import core, models
from apps.codeproj import permissions
from apps.codeproj.api_filters import v3 as v3_filters
from apps.codeproj.apimixins import ProjectTeamBaseAPIView
from apps.codeproj.apis import v1, v3
from apps.codeproj.serializers import v3 as v3_serializers

logger = logging.getLogger(__name__)


class PTRepoListAPIView(CustomSerilizerMixin, generics.ListCreateAPIView, ProjectTeamBaseAPIView):
    """指定项目组的代码库列表

    ### GET
    应用场景：获取指定项目的代码库列表

    ### POST
    应用场景：创建指定项目的代码库
    """
    serializer_class = v3_serializers.RepositoryListSerializer
    post_serializer_class = v3_serializers.RepositoryCreateSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = v3_filters.RepositoryFilter
    permission_classes = [permissions.ProjectTeamDefaultPermission]

    def get_queryset(self):
        pt = self.get_project_team()
        queryset = models.Repository.objects.filter(project_team=pt).order_by("-created_time")
        return queryset


class PTRepoDetailAPIView(v3.RepositoryDetailApiView):
    """指定项目组的代码库详情

    ### GET
    应用场景：获取代码库详情

    ### PUT
    应用场景：更新代码库详情
    """


class PTRepositorySchemeInfoAPIView(v1.RepositorySchemesInfoApiView):
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

    permission_classes = [permissions.ProjectTeamDefaultPermission]

    def get_repo_with_url(self, scm_url, **kwargs):
        """通过代码库链接获取代码库
        """
        org_sid = kwargs["org_sid"]
        team_name = kwargs["team_name"]
        repo_queryset = models.Repository.objects.filter(organization__org_sid=org_sid, project_team__name=team_name)
        return core.RepositoryManager.find_repository(scm_url, repo_queryset)


class PTRepoBranchListAPIView(v1.RepoBranchListApiView, ProjectTeamBaseAPIView):
    """指定代码库已接入的分支列表接口

    ### GET
    应用场景：获取指定代码库分支列表
    """
    permission_classes = [permissions.RepositoryDefaultPermission]


class PTProjectScanDetailAPIView(v1.ProjectScanDetailApiView, ProjectTeamBaseAPIView):
    """项目指定扫描详情接口
    使用对象：节点

    ### Get
    应用场景：获取扫描结果
    """
    permission_classes = [permissions.RepositoryDefaultPermission]


class PTProjectListCreateView(v1.ProjectListCreateView, ProjectTeamBaseAPIView):
    """指定PT下的分支任务列表接口

    ### Get
    应用场景：获取项目列表

    ### Post
    应用场景：创建一个项目 + 初始化配置
    """
    permission_classes = [permissions.ProjectTeamOperationPermission]
    serializer_class = v3_serializers.APIProjectsSerializer

    def get_queryset(self):
        logger.info("[Org: %s][PT: %s][User: %s] find project: %s" % (
            self.kwargs["org_sid"], self.kwargs["team_name"], self.request.user, self.request.query_params))
        org = models.Organization.objects.get(org_sid=self.kwargs["org_sid"])
        pt = models.ProjectTeam.objects.get(name=self.kwargs["team_name"], organization=org)
        return models.Project.objects.filter(repo__organization=org, repo__project_team=pt)


class PTProjectScanSchemeDetailApiView(v1.ProjectScanSchemeDetailApiView, ProjectTeamBaseAPIView):
    """项目扫描方案详情接口

    ### Get
    应用场景：获取项目扫描方案详情
    """
    permission_classes = [permissions.ProjectTeamOperationPermission]


class PTProjectListAPIView(v3.ProjectListApiView):
    """指定代码库的分支任务列表

    ### GET
    应用场景：获取已接入的项目列表

    ### POST
    应用场景：创建新的扫描项目
    """


class PTProjectDetailAPIView(v3.ProjectDetailApiView):
    """项目详情接口

    ### Get
    应用场景：获取项目详情
    """


class PTScanSchemeListAPIView(v3.ScanSchemeListApiView):
    """指定代码库扫描方案列表

    ### GET
    应用场景：获取指定代码库的扫描方案列表

    ### POST
    应用场景：创建指定代码库的扫描方案
    """


class PTRepositorySchemeCopyApiView(v3.RepositorySchemeCopyApiView):
    """拷贝方案模板

    ### POST
    应用场景：仅用于拷贝方案模板
    """


class PTScanSchemeBasicConfAPIView(v3.ScanSchemeBasicConfApiView):
    """指定扫描方案详情接口，仅basic配置

    ### GET
    应用场景：获取指定的扫描方案

    ### PUT
    应用场景：更新指定扫描方案
    """


class PTScanSchemeLintConfAPIView(v3.ScanSchemeLintConfApiView):
    """扫描方案代码扫描配置接口

    ### GET
    应用场景：获取指定扫描方案的lint配置

    ### PUT
    应用场景：更新指定扫描方案的lint配置
    """


class PTScanSchemeMetricConfAPIView(v3.ScanSchemeMetricConfApiView):
    """扫描方案指定代码度量配置

    ### GET
    应用场景：获取指定扫描方案的metric配置

    ### PUT
    应用场景：更新指定扫描方案的metric配置
    """


class PTScanSchemeDirListAPIView(v3.ScanSchemeDirListApiView):
    """扫描方案指定扫描目录列表管理接口

    ### GET
    应用场景：获取指定扫描方案的扫描目录列表

    ### POST
    应用场景：创建指定扫描方案的扫描目录
    """


class PTScanSchemeDirDetailAPIView(v3.ScanSchemeDirDetailApiView):
    """扫描方案指定扫描目录详情管理接口

    ### GET
    应用场景：获取指定扫描方案的指定扫描目录

    ### PUT
    应用场景：更新指定扫描方案的指定扫描目录

    ### DELETE
    应用场景：删除指定扫描方案的指定扫描目录
    """


class PTAnalyseServerProxyAPIView(v1.AnalyseServerProxyApi):
    """转发到Analyse Server的Api接口，具体文档请查看Analyse Server域名下相同的url文档
    """
    permission_classes = [permissions.RepositoryDefaultPermission]
    authentication_classes = [TCANodeTokenBackend]


class PTProjectScanSchemeDefaultScanPathListAPIView(v1.ProjectScanSchemeDefaultScanPathListApiView):
    """
    使用对象：节点

    ### Get
    应用场景：获取项目的默认过滤路径配置
    """


class PTProjectConfAPIView(v1.ProjectConfApiView, ProjectTeamBaseAPIView):
    """项目扫描配置接口
    使用对象：节点

    ### Get
    应用场景：获取项目的代码功能配置
    """


class PTProjectScanJobConfAPIView(v1.ProjectScanJobConfApiView, ProjectTeamBaseAPIView):
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
    permission_classes = [permissions.RepositoryDefaultPermission]


class PTProjectScanCreateAPIView(v3.ProjectScanCreateApiView, ProjectTeamBaseAPIView):
    """项目创建扫描接口

    ### POST
    应用场景：启动一次项目的扫描任务
    """
    permission_classes = [permissions.RepositoryDefaultPermission]
