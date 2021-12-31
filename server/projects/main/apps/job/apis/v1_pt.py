# -*- coding: utf-8 -*-
"""
job - v1 apis for project team
"""

# 项目内 import
from apps.authen.backends import TCANodeTokenBackend
from apps.codeproj.apimixins import ProjectTeamBaseAPIView
from apps.codeproj.permissions import RepositoryProjectDefaultPermission
from apps.job.api_filters import v3 as v3_filters
from apps.job.apis import v1
from apps.job.serializers import v3 as v3_serializers


class ProjectJobListAPIView(v1.ProjectJobListApiView, ProjectTeamBaseAPIView):
    """项目任务列表接口

    ### GET
    应用场景：获取指定项目任务列表详情
    """
    filterset_class = v3_filters.JobFilterSetV3
    permission_classes = [RepositoryProjectDefaultPermission]


class ProjectJobDetailAPIView(v1.ProjectJobDetailApiView, ProjectTeamBaseAPIView):
    """项目任务详情接口

    ### GET
    应用场景：获取指定项目指定任务详情
    """
    serializer_class = v3_serializers.JobSerializerV3
    permission_classes = [RepositoryProjectDefaultPermission]


class ProjectScanJobInitAPIView(v1.ProjectScanJobInitApiView, ProjectTeamBaseAPIView):
    """项目扫描初始化
    使用对象：节点

    ### GET
    应用场景：获取项目扫描配置的api，供节点端离线扫描使用

    ### POST
    应用场景：创建新的扫描任务，仅做初始化
    """
    permission_classes = [RepositoryProjectDefaultPermission]


class ProjectJobFinishAPIView(v1.ProjectJobFinishApiView, ProjectTeamBaseAPIView):
    """项目本地扫描完成，上报结果
    使用对象：节点

    ### POST
    应用场景：上报本地扫描的任务结果
    """
    schema = None
    permission_classes = [RepositoryProjectDefaultPermission]
    authentication_classes = [TCANodeTokenBackend]
