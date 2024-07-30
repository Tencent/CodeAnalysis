# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

# -*- coding: utf-8 -*-
"""
codeproj - v3 apis
"""
# python 原生import
import logging
import os

# 第三方 import
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ParseError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

# 项目内 import
from apps.authen.core import UserManager
from apps.authen.permissions import OrganizationDefaultPermission, OrganizationOperationPermission
from apps.authen.serializers.base import UserSimpleSerializer
from apps.base.apimixins import CustomSerilizerMixin, V3GetModelMixinAPIView
from apps.codeproj import models
from apps.codeproj.api_filters import base as base_filters, v3 as v3_filters
from apps.codeproj.core import LabelManager, ProjectManager, ProjectTeamManager, ScmClientManager
from apps.codeproj.core import RepositoryManager, ScanSchemeManager, ScanSchemePermManager
from apps.codeproj.core import create_server_scan
from apps.codeproj.permissions import ProjectTeamDefaultPermission, ProjectTeamOperationPermission, \
    RepositoryDefaultPermission, RepositoryProjectDefaultPermission, RepositorySchemeDefaultPermission, \
    SchemeDefaultPermission
from apps.codeproj.serializers import base as base_serializers
from apps.codeproj.serializers import base_scheme as base_scheme_serializers
from apps.codeproj.serializers import v3 as v3_serializers
from apps.job.apis import base as job_base
from apps.job.models import Job, Task
from util.errcode import E_SERVER_JOB_CREATE_ERROR
from util.exceptions import CDErrorBase, ProjectScanCreateError
from util.operationrecord import OperationRecordHandler
from util.puppy import configlib

logger = logging.getLogger(__name__)


class ProjectTeamListApiView(generics.ListCreateAPIView, V3GetModelMixinAPIView):
    """项目组列表

    ### GET
    应用场景：获取项目列表
    ```bash
    筛选参数：
    status: 团队状态，1，活跃，2，失活
    query: 项目名称/项目显示名称，包含
    scope: 1 为我管理的
    ```

    ### POST
    应用场景：创建项目组
    """
    permission_classes = [OrganizationOperationPermission]
    serializer_class = v3_serializers.ProjectTeamSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = base_filters.ProjectTeamFilter
    pagination_class = None

    def get_queryset(self):
        org = self.get_org()
        try:
            scope = int(self.request.query_params.get("scope"))
        except (ValueError, TypeError):
            scope = None
        if scope == models.ProjectTeam.PermissionEnum.ADMIN:
            # 获取我管理的项目
            return ProjectTeamManager.get_user_teams(org, self.request.user, scope)
        # 默认获取有权限的项目
        return ProjectTeamManager.get_user_teams(org, self.request.user)


class ProjectTeamDetailApiView(generics.RetrieveUpdateAPIView, V3GetModelMixinAPIView):
    """项目组详情

    ### GET
    应用场景：获取项目详情

    ### PUT
    应用场景：更新项目详情
    """
    permission_classes = [ProjectTeamDefaultPermission]
    serializer_class = v3_serializers.ProjectTeamSerializer

    def get_object(self):
        return self.get_project_team()


class ProjectTeamStatusApiView(generics.RetrieveUpdateAPIView, V3GetModelMixinAPIView):
    """项目组状态更新

    ### GET
    应用场景：获取项目详情

    ### PUT
    应用场景：更新项目状态
    """
    permission_classes = [ProjectTeamDefaultPermission]
    serializer_class = base_serializers.ProjectTeamSimpleSerializer

    def get_object(self):
        return self.get_project_team()


class ProjectTeamMemberConfApiView(generics.GenericAPIView, V3GetModelMixinAPIView):
    """项目成员权限管理

    ### GET
    应用场景：获取项目成员

    ### POST
    应用场景：新增不同权限成员
    注： 为兼容OA，users中需传递username
    """
    permission_classes = [ProjectTeamDefaultPermission]
    serializer_class = base_serializers.MemberConfAddSerializer

    def get(self, request, *args, **kwargs):
        project_team = self.get_project_team()
        admins = project_team.get_members(models.ProjectTeam.PermissionEnum.ADMIN)
        users = project_team.get_members(models.ProjectTeam.PermissionEnum.USER)
        return Response({
            "admins": [UserSimpleSerializer(instance=user).data for user in admins],
            "users": [UserSimpleSerializer(instance=user).data for user in users],
        })

    def post(self, request, *args, **kwargs):
        project_team = self.get_project_team()
        slz = self.get_serializer(data=request.data)
        if slz.is_valid(raise_exception=True):
            users = slz.validated_data["users"]
            role = slz.validated_data["role"]
            ProjectTeamManager.add_team_members(project_team, users, role)
            return Response(slz.data)


class ProjectTeamMemberConfDeleteApiView(APIView, V3GetModelMixinAPIView):
    """删除项目成员

    ### DELETE
    应用场景：删除项目成员
    """
    permission_classes = [ProjectTeamDefaultPermission]

    def delete(self, request, *args, **kwargs):
        project_team = self.get_project_team()
        role = kwargs["role"]
        username = kwargs["username"]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise ValidationError("成员不存在")
        if role == models.Organization.PermissionEnum.ADMIN or role == models.Organization.PermissionEnum.USER:
            project_team.remove_perm(user, role)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError("角色类型错误")


class ProjectTeamLabelListApiView(generics.ListCreateAPIView, V3GetModelMixinAPIView):
    """项目组标签

    ### GET
    应用场景：获取项目组全部标签列表

    ### POST
    应用场景：创建项目组标签
    """
    permission_classes = [ProjectTeamDefaultPermission]
    serializer_class = v3_serializers.ProjectTeamLabelSerializer
    pagination_class = None

    def get_queryset(self):
        project_team = self.get_project_team()
        return models.Label.objects.filter(project_team=project_team)


class ProjectTeamLabelTreeApiView(APIView, V3GetModelMixinAPIView):
    """项目组标签树结构

    ### GET
    应用场景：获取项目组树结构标签
    """
    permission_classes = [ProjectTeamDefaultPermission]

    def get(self, request, *args, **kwargs):
        project_team = self.get_project_team()
        tree_label = LabelManager.get_pt_label_tree(project_team)
        return Response(tree_label)


class ProjectTeamLabelDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    """项目组标签详情

    ### GET
    应用场景：获取项目组标签详情

    ### PUT
    应用场景：更新项目组标签

    ### DELETE
    应用场景： 移除项目组标签
    """
    permission_classes = [ProjectTeamDefaultPermission]
    serializer_class = v3_serializers.ProjectTeamLabelSerializer

    def get_object(self):
        org_sid = self.kwargs["org_sid"]
        team_name = self.kwargs["team_name"]
        label_id = self.kwargs["label_id"]
        label = get_object_or_404(models.Label, id=label_id, project_team__name=team_name,
                                  project_team__organization__org_sid=org_sid)
        return label

    def perform_destroy(self, instance):
        LabelManager.delete_label(instance)


class OrgRepositoryListApiView(generics.ListAPIView, V3GetModelMixinAPIView):
    """团队代码库列表

    ### GET
    应用场景：获取团队代码库列表
    """
    permission_classes = [OrganizationDefaultPermission]
    serializer_class = v3_serializers.RepositoryListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = v3_filters.RepositoryFilter

    def get_queryset(self):
        org = self.get_org()
        # 用户是团队管理员则直接获取当前团队全部代码库
        if self.request.user.has_perm(org.PermissionNameEnum.CHANGE_ORG_PERM, org):
            return models.Repository.objects.filter(organization=org)
        # 否则获取当前团队该用户有权限的项目组的代码库
        pt_ids = list(ProjectTeamManager.get_user_teams(org, self.request.user).values_list('id', flat=True))
        return models.Repository.objects.filter(organization=org, project_team_id__in=pt_ids)


class RepositoryListApiView(CustomSerilizerMixin, generics.ListCreateAPIView, V3GetModelMixinAPIView):
    """项目内代码库列表

    ### GET
    应用场景：获取项目内的代码库列表
    ```python
    筛选参数:
    scm_url_or_name: str, 代码库地址或代码库名称, 模糊匹配
    scm_url: str, 代码库地址
    scope: str, 过滤范围, all 全部, my 我创建的, subscribed 我关注的
    ```

    ### POST
    应用场景：创建代码库
    """
    permission_classes = [ProjectTeamOperationPermission]
    serializer_class = v3_serializers.RepositoryListSerializer
    post_serializer_class = v3_serializers.RepositoryCreateSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = v3_filters.RepositoryFilter

    def get_queryset(self):
        project_team = self.get_project_team()
        return models.Repository.objects.filter(project_team=project_team)


class RepositoryDetailApiView(generics.RetrieveUpdateDestroyAPIView, V3GetModelMixinAPIView):
    """代码库详情接口

    ### GET
    应用场景：获取代码库详情

    ### POST
    应用场景：更新代码库详情
    """
    permission_classes = [RepositoryDefaultPermission]
    serializer_class = v3_serializers.RepositoryListSerializer

    def get_object(self):
        return self.get_repo()

    def perform_destroy(self, instance):
        user = self.request.user
        RepositoryManager.delete_repo(instance.id, user)


class RepositoryAuthDetailApiView(generics.RetrieveUpdateAPIView, V3GetModelMixinAPIView):
    """代码库鉴权详情接口

    ### GET
    应用场景：获取代码库鉴权详情

    ### PUT
    应用场景：更新代码库鉴权
    > 创建参数：

    ```json
    {
       "scm_auth": {
            "auth_type": "鉴权类型，类型为str",
            "scm_ssh": "SSH授权编号，类型为int，数据源：/api/v3/authen/scmsshinfos/",
            "scm_account": "账号密码授权编号，类型为int，数据源：/api/v3/authen/scmaccounts/",
        }
    }
    ```
    """
    permission_classes = [RepositoryDefaultPermission]
    serializer_class = v3_serializers.RepositoryAuthSerializer
    update_serializer_class = v3_serializers.RepositoryAuthUpdateSerializer

    def get_object(self):
        return self.get_repo()

    def get_serializer_class(self):
        if self.request and self.request.method == 'PUT':
            if hasattr(self, 'update_serializer_class'):
                return self.update_serializer_class
        return generics.GenericAPIView.get_serializer_class(self)


class RepositoryMemberConfApiView(generics.GenericAPIView, V3GetModelMixinAPIView):
    """代码库成员管理

    ### GET
    获取代码库成员列表
    注：体验版中代码库仅有admins成员，无普通成员，普通成员复用项目组内

    ### POST
    新增代码库成员
    """
    permission_classes = [RepositoryDefaultPermission]
    serializer_class = base_serializers.MemberConfAddSerializer

    def get(self, request, *args, **kwargs):
        repo = self.get_repo()
        admins = repo.get_members(models.Repository.PermissionEnum.ADMIN)
        return Response({
            "admins": [UserSimpleSerializer(instance=user).data for user in admins],
        })

    def post(self, request, *args, **kwargs):
        slz = self.get_serializer(data=request.data)
        slz.is_valid(raise_exception=True)
        users = slz.validated_data["users"]
        role = slz.validated_data["role"]
        # 由于代码库的权限是0和1，为兼容做的处理
        role = models.Repository.PermissionEnum.ADMIN if role == models.BasePerm.PermissionEnum.ADMIN else role
        repo = self.get_repo()
        add_nicknames = RepositoryManager.add_repo_members(repo, users, role)
        if add_nicknames:
            OperationRecordHandler.add_repo_operation_record(
                repo, "添加代码库成员", request.user, "; ".join(add_nicknames))
        return Response(slz.data)


class RepositoryMemberConfDeleteApiView(APIView, V3GetModelMixinAPIView):
    """删除代码库成员

    ### DELETE
    应用场景：删除代码库成员
    """
    permission_classes = [RepositoryDefaultPermission]

    def delete(self, request, *args, **kwargs):
        repo = self.get_repo()
        role = kwargs["role"]
        username = kwargs["username"]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise ValidationError("成员不存在")
        if role == models.Organization.PermissionEnum.ADMIN or role == models.Organization.PermissionEnum.USER:
            repo.remove_perm(user, role)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError("角色类型错误")


class RepositorySubscribedApiView(APIView, V3GetModelMixinAPIView):
    """代码库关注

    ### POST
    应用场景：关注指定代码库

    ### DELETE
    应用场景：取消关注代码库
    """
    permission_classes = [ProjectTeamOperationPermission]

    def post(self, request):
        repo = self.get_repo()
        repo.subscribers.add(request.user)
        return Response("关注成功")

    def delete(self, request):
        repo = self.get_repo()
        repo.subscribers.remove(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RepositoryInitApiView(generics.CreateAPIView, V3GetModelMixinAPIView):
    """代码库初始化创建接口

    ### POST
    应用场景：创建默认的扫描方案和分支项目
    """
    permission_classes = [ProjectTeamOperationPermission]
    serializer_class = v3_serializers.RepoProjectInitialSerializer

    def get_queryset(self):
        project_team = self.get_project_team()
        return models.Repository.objects.filter(project_team=project_team)


class RepositorySchemeInitApiView(generics.CreateAPIView, V3GetModelMixinAPIView):
    """代码库初始化扫描方案

    ### POST
    应用场景：仅用于初始化页面创建扫描方案
    """
    permission_classes = [ProjectTeamOperationPermission]
    serializer_class = v3_serializers.ScanSchemeInitialSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        repo = self.get_repo()
        # 创建扫描方案
        scan_scheme = ScanSchemeManager.create_init_scheme(repo.id, user=request.user, **serializer.validated_data)
        # 设置默认扫描方案，如果同时有多个方案正在初始化，可能会失败
        ScanSchemeManager.set_default_scanscheme(scan_scheme)
        return Response({"scan_scheme": scan_scheme.id}, status=status.HTTP_201_CREATED)


class RepositorySchemeCopyApiView(generics.CreateAPIView, V3GetModelMixinAPIView):
    """拷贝方案模板

    ### POST
    应用场景：仅用于拷贝方案模板
    """
    permission_classes = [ProjectTeamOperationPermission]
    serializer_class = v3_serializers.ScanSchemeCopySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        repo = self.get_repo()
        ref_scheme = serializer.validated_data.pop('ref_scheme')
        # 拷贝方案模板
        scan_scheme = ScanSchemeManager.create_scheme_with_ref_scheme(repo.id,
                                                                      ref_scheme, user=request.user,
                                                                      **serializer.validated_data)
        action = "拷贝分析方案" if ref_scheme.repo else "拷贝方案模板"
        OperationRecordHandler.add_scanscheme_operation_record(scan_scheme,
                                                               action, request.user, "ref_scheme: %s" % ref_scheme)
        return Response({"scan_scheme": scan_scheme.id}, status=status.HTTP_201_CREATED)


class ScanSchemeListApiView(generics.ListAPIView, V3GetModelMixinAPIView):
    """代码库扫描方案列表

    ### GET
    应用场景：获取指定代码库的扫描方案

    ### POST 已无效，体验版采用了initscheme接口
    应用场景：创建指定代码库的扫描方案
    """
    permission_classes = [ProjectTeamOperationPermission]
    serializer_class = v3_serializers.ScanSchemeBasicConfSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = base_filters.ScanSchemeFilter

    def get_queryset(self):
        repo = self.get_repo()
        return models.ScanScheme.objects.filter(repo=repo).order_by("-id")


class ScanSchemeBasicConfApiView(generics.RetrieveUpdateAPIView, V3GetModelMixinAPIView):
    """扫描方案详情，仅基础性详情

    ### GET
    应用场景：获取指定的扫描方案

    ### PUT
    应用场景：更新指定扫描方案
    """
    permission_classes = [RepositorySchemeDefaultPermission]
    serializer_class = v3_serializers.ScanSchemeBasicConfSerializer

    def get_object(self):
        return self.get_scheme()


class ScanSchemeLintConfApiView(generics.RetrieveUpdateAPIView, V3GetModelMixinAPIView):
    """扫描方案代码扫描配置详情

    ### GET
    应用场景：获取指定扫描方案的lint配置

    ### PUT
    应用场景：更新指定扫描方案的lint配置
    """
    permission_classes = [SchemeDefaultPermission]
    serializer_class = v3_serializers.ScanSchemeLintConfSerializer

    def get_object(self):
        scan_scheme = self.get_scheme()
        return get_object_or_404(models.LintBaseSetting, scan_scheme=scan_scheme)


class ScanSchemeMetricConfApiView(generics.RetrieveUpdateAPIView, V3GetModelMixinAPIView):
    """扫描方案指定代码度量配置

    ### GET
    应用场景：获取指定扫描方案的metric配置

    ### PUT
    应用场景：更新指定扫描方案的metric配置
    """
    permission_classes = [SchemeDefaultPermission]
    serializer_class = v3_serializers.ScanSchemeMetricConfSerializer

    def get_object(self):
        scan_scheme = self.get_scheme()
        return get_object_or_404(models.MetricSetting, scan_scheme=scan_scheme)


class ScanSchemeDirListApiView(generics.ListCreateAPIView, V3GetModelMixinAPIView):
    """扫描方案指定扫描目录列表管理接口

    ### GET
    应用场景：获取指定扫描方案的扫描目录列表

    ### POST
    应用场景：创建指定扫描方案的扫描目录
    """
    permission_classes = [SchemeDefaultPermission]
    serializer_class = v3_serializers.ScanSchemDirConfSerializer

    def get_queryset(self):
        scan_scheme = self.get_scheme()
        return models.ScanDir.objects.filter(scan_scheme=scan_scheme).order_by("-id")


class ScanSchemeDirDetailApiView(generics.RetrieveUpdateDestroyAPIView, V3GetModelMixinAPIView):
    """扫描方案指定扫描目录详情管理接口

    ### GET
    应用场景：获取指定扫描方案的指定扫描目录

    ### PUT
    应用场景：更新指定扫描方案的指定扫描目录

    ### DELETE
    应用场景：删除指定扫描方案的指定扫描目录
    """
    permission_classes = [SchemeDefaultPermission]
    serializer_class = v3_serializers.ScanSchemDirConfSerializer

    def get_object(self):
        dir_id = self.kwargs["dir_id"]
        scan_scheme = self.get_scheme()
        return get_object_or_404(models.ScanDir, scan_scheme=scan_scheme, id=dir_id)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        OperationRecordHandler.add_scanscheme_operation_record(instance.scan_scheme, "删除过滤目录",
                                                               request.user,
                                                               "dir_path:%s, path_type: %s, scan_type:%s" % (
                                                                   instance.dir_path, instance.path_type,
                                                                   instance.scan_type))
        return generics.RetrieveUpdateDestroyAPIView.destroy(self, request, *args, **kwargs)


class ScanSchemeDirBulkCreateApiView(generics.GenericAPIView, V3GetModelMixinAPIView):
    """扫描方案过滤路径，批量增加路径配置

    ### POST
    应用场景：批量创建过滤路径
    """
    permission_classes = [SchemeDefaultPermission]
    serializer_class = v3_serializers.ScanSchemeDirConfBulkCreateSerialzier

    def post(self, request, *args, **kwargs):
        slz = self.get_serializer(data=request.data)
        slz.is_valid(raise_exception=True)
        scan_scheme = self.get_scheme()
        scandirs = slz.validated_data.get("scandirs", [])
        new_scandirs = []
        ignore_num = 0
        for scandir in scandirs:
            dir_path = scandir.get('dir_path')
            # 忽略已存在的路径
            if models.ScanDir.objects.filter(scan_scheme=scan_scheme, dir_path=dir_path).exists():
                ignore_num += 1
            else:
                models.ScanDir.objects.create(scan_scheme=scan_scheme, **scandir)
                new_scandirs.append(scandir)
        new_num = len(new_scandirs)
        if new_num > 0:
            OperationRecordHandler.add_scanscheme_operation_record(
                scan_scheme, "批量新增过滤目录", request.user, new_scandirs)
        detail = '批量创建%s条路径' % new_num
        if ignore_num > 0:
            detail = '%s，忽略%s条路径（已存在）' % (detail, ignore_num)
        return Response({'detail': detail})


class ScanSchemeDirClearApiView(APIView, V3GetModelMixinAPIView):
    """移除所有过滤路径配置

    ### DELETE
    应用场景：批量移除扫描方案过滤路径
    """
    permission_classes = [SchemeDefaultPermission]

    def delete(self, request, *args, **kwargs):
        scan_scheme = self.get_scheme()
        scandirs = models.ScanDir.objects.filter(scan_scheme=scan_scheme)
        if scandirs:
            scandirs.delete()
            OperationRecordHandler.add_scanscheme_operation_record(
                scan_scheme, "清空过滤目录", request.user, '一键清空该分析方案的过滤路径')
        return Response(status=status.HTTP_204_NO_CONTENT)


class ScanSchemeBranchListApiView(generics.ListAPIView, V3GetModelMixinAPIView):
    """扫描方案关联分支列表

    ### GET:
    应用场景：获取扫描方案关联的分支项目列表
    """
    permission_classes = [RepositoryDefaultPermission]
    serializer_class = base_serializers.ProjectSimpleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = base_filters.ProjectFilter

    def get_queryset(self):
        scheme_id = self.kwargs["scheme_id"]
        repo = self.get_repo()
        return models.Project.objects.filter(repo_id=repo.id, scan_scheme_id=scheme_id).order_by("-id")


class ScanSchemePullApiView(generics.GenericAPIView, V3GetModelMixinAPIView):
    """扫描方案拉取模板同步操作

    ### POST
    应用场景：用户主动同步模板内容
    """
    permission_classes = [RepositorySchemeDefaultPermission]
    serializer_class = base_scheme_serializers.ScanSchemeSyncConfSerializer

    def post(self, request, *args, **kwargs):
        user = request.user if request else None
        org_sid = kwargs["org_sid"]
        scan_scheme = self.get_scheme()
        if not scan_scheme.refer_scheme:
            raise ParseError("无方案模板或父扫描方案，不可同步")
        if not ScanSchemePermManager.check_user_view_perm(scan_scheme.refer_scheme, user, org_sid):
            raise ParseError("无方案模板权限，不可同步")
        slz = self.get_serializer(data=request.data)
        slz.is_valid(raise_exception=True)
        ScanSchemeManager.sync_with_ref_scheme(scan_scheme, scan_scheme.refer_scheme, user, **slz.data)
        message = ScanSchemeManager.get_sync_message(scan_scheme.refer_scheme, **slz.data)
        OperationRecordHandler.add_scanscheme_operation_record(scan_scheme, "主动同步拉取", user, message)
        return Response(slz.data)


class ScanSchemeDefaultScanPathListApiView(CustomSerilizerMixin, generics.ListCreateAPIView, V3GetModelMixinAPIView):
    """

    ### GET
    获取指定扫描方案的默认过滤路径
    > exclude=1表示筛选被屏蔽了的路径列表

    ### POST
    在指定扫描方案屏蔽指定默认路径
    """

    permission_classes = [RepositorySchemeDefaultPermission]
    serializer_class = base_serializers.DefaultScanPathSerializer
    post_serializer_class = base_serializers.SchemeDefaultScanPathExcludeMapSerializer

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
        scan_scheme = self.get_scheme()
        if self.get_exclude_paths():
            # 筛选屏蔽的默认路径
            default_scan_paths = models.DefaultScanPath.objects.filter(
                schemedefaultscanpathexcludemap__scan_scheme=scan_scheme)
        else:
            # 筛选未屏蔽的默认路径
            default_scan_paths = models.DefaultScanPath.objects.exclude(
                schemedefaultscanpathexcludemap__scan_scheme=scan_scheme)
        return default_scan_paths


class ScanSchemeDefaultScanPathDetailApiView(generics.RetrieveDestroyAPIView, V3GetModelMixinAPIView):
    """
    ### GET
    获取指定扫描方案指定屏蔽的过滤路径

    ### DELETE
    在指定扫描方案取消屏蔽指定过滤路径
    """
    permission_classes = [RepositorySchemeDefaultPermission]
    serializer_class = base_serializers.SchemeDefaultScanPathExcludeMapSerializer

    def get_object(self):
        """获取指定对象
        """
        scan_scheme = self.get_scheme()
        scanscheme_path_map = get_object_or_404(
            models.SchemeDefaultScanPathExcludeMap, scan_scheme_id=scan_scheme.id,
            scan_scheme__repo_id=self.kwargs["repo_id"], default_scan_path_id=self.kwargs["path_id"])
        return scanscheme_path_map

    def destroy(self, request, *args, **kwargs):
        """删除指定对象
        """
        instance = self.get_object()
        OperationRecordHandler.add_scanscheme_operation_record(
            instance.scan_scheme, "修改过滤路径", request.user,
            "取消屏蔽默认过滤路径:%s " % instance.default_scan_path.dir_path)
        return super().destroy(request, *args, **kwargs)


class ProjectListApiView(CustomSerilizerMixin, generics.ListCreateAPIView, V3GetModelMixinAPIView):
    """扫描项目列表

    ### GET
    应用场景：获取已接入的项目列表

    ### POST
    应用场景：创建新的扫描项目
    """
    permission_classes = [ProjectTeamOperationPermission]
    serializer_class = v3_serializers.ProjectSimpleSerializerV3
    post_serializer_class = v3_serializers.ProjectSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = base_filters.ProjectFilter

    def get_queryset(self):
        repo = self.get_repo()
        return models.Project.objects.filter(repo_id=repo.id)


class ProjectDetailApiView(CustomSerilizerMixin, generics.RetrieveUpdateDestroyAPIView, V3GetModelMixinAPIView):
    """项目详情

    ### GET
    应用场景：获取已接入的项目详情

    ### PUT
    应用场景：更新项目状态
    """
    permission_classes = [RepositoryProjectDefaultPermission]
    serializer_class = v3_serializers.ProjectSerializer
    put_serializer_class = v3_serializers.ProjectUpdatetSerializer

    def get_object(self):
        return self.get_project()

    def perform_destroy(self, instance):
        user = self.request.user
        ProjectManager.delete_project(instance.repo_id, instance.id, user)


class ProjectJobDetailApiView(generics.RetrieveAPIView, V3GetModelMixinAPIView):
    """分支项目任务详情接口

    ### GET:
    应用场景：获取项目指定扫描job的详情


    """
    permission_classes = [ProjectTeamOperationPermission]
    serializer_class = base_serializers.ProjectJobDetailSerializer

    def get_object(self):
        job_id = self.kwargs["job_id"]
        project = self.get_project()
        return get_object_or_404(Job, id=job_id, project=project)


class ProjectJobTaskDetailApiView(generics.RetrieveAPIView, V3GetModelMixinAPIView):
    """分支项目任务指定的task详情

    ### GET
    应用场景：获取项目指定扫描task的详情
    """
    permission_classes = [ProjectTeamOperationPermission]
    serializer_class = base_serializers.TaskDetailSerializer

    def get_object(self):
        job_id = self.kwargs["job_id"]
        task_id = self.kwargs["task_id"]
        project = self.get_project()
        return get_object_or_404(Task, id=task_id, job_id=job_id, job__project=project)


class ProjectJobCancelApiView(job_base.JobCancelApiView, V3GetModelMixinAPIView):
    """分支项目任务取消接口

    ### POST
    应用场景：分支项目任务取消
    """
    permission_classes = [ProjectTeamOperationPermission]

    def post(self, request, *args, **kwargs):
        job_id = kwargs["job_id"]
        project = self.get_project()
        get_object_or_404(Job, id=job_id, project=project)
        return super().post(request, **kwargs)


class ScanBranchNameListApiView(generics.ListAPIView, V3GetModelMixinAPIView):
    """代码库分支列表接口

    ### GET
    应用场景：获取指定代码库下所有的分支
    """
    permission_classes = [RepositoryDefaultPermission]
    serializer_class = base_serializers.ProjectBranchNameSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = base_filters.ProjectBranchNameFilter

    def get_queryset(self):
        repo = self.get_repo()
        return models.Project.objects.filter(repo_id=repo.id).values("branch").distinct()


class ScanBranchProjectListApiView(APIView, V3GetModelMixinAPIView):
    """分支项目列表接口

    ### GET
    应用场景：获取代码库某个分支下的分支项目列表
    > * 查询参数：
    >    * branch：分支名称，必填项
    >    * scheme_status：1表示活跃，2表示废弃，默认为1
    """
    permission_classes = [RepositoryDefaultPermission]

    def get(self, request, *args, **kwargs):
        repo = self.get_repo()
        branch = request.query_params.get("branch", None)
        if branch is None:
            raise ValidationError({"branch": "分支名称筛选项必填"})
        scheme_status = request.query_params.get("scheme_status", 1)
        params = {"repo_id": repo.id, "scan_scheme__status": scheme_status, "branch": branch}
        project_list = models.Project.objects.select_related("scan_scheme") \
            .filter(**params).values("id", "branch", "scan_scheme__name")
        return Response(project_list)


class ProjectCodeFileApiView(APIView, V3GetModelMixinAPIView):
    """获取指定文件代码内容
    """
    permission_classes = [RepositoryDefaultPermission]

    def get_code_content(self, content_info, project, path, start_line, end_line, scm_url, revision):
        """获取代码内容

        :param project: Project，项目
        :param path: str，指定路径
        :param start_line: int，开始行号
        :param end_line: int，结束行号
        :param scm_url: str，代码库url
        :param revision: str，代码库版本号
        :return: dict
        """
        scm_client = ScmClientManager.get_scm_client_with_project(project, scm_url=scm_url)
        content = scm_client.cat(path, revision or scm_client.latest_revision)
        code_result = []
        index = 0
        code_lines = content.splitlines()
        for line in code_lines:
            index += 1
            if start_line and index < start_line:
                continue
            if end_line and index > end_line:
                break
            code_result.append({"lineNum": index,
                                "content": line})
        result = {
            "file_path": path,
            "scm_revision": revision or scm_client.latest_revision,
            "codeContents": code_result,
        }
        content_info.update(**result)

    def get(self, request, **kwargs):
        """
        ### GET
        应用场景：获取指定文件指定版本的代码信息
        > 参数说明:

        ```Python
         # path:     str, 代码文件路径，必填
         # revision: str, 版本号
         # start:    int，起始行号
         # end:      int，结束行号
         # scm_url:  str, 代码库url
        ```
        """
        project = self.get_project()
        path = request.query_params.get("path")
        if not path:
            raise ParseError("文件路径不能为空")
        revision = request.query_params.get("revision")
        start_line = request.query_params.get("start")
        end_line = request.query_params.get("end")
        scm_url = request.query_params.get("scm_url")
        start_line = int(start_line) if start_line else None
        end_line = int(end_line) if start_line else None
        suffix = os.path.splitext(path)[1]
        content_info = {"suffix": suffix, "language": ""}
        try:
            self.get_code_content(content_info, project, path, start_line, end_line, scm_url, revision)
        except Exception as e:
            raise ParseError(str(e))
        return Response(content_info)


class ProjectScanPuppyiniApiView(generics.GenericAPIView, V3GetModelMixinAPIView):
    """获取puppyini文件
    """
    permission_classes = [RepositoryDefaultPermission]
    serializer_class = base_serializers.ProjectScanPuppyIniSerializer

    def post(self, request, **kwargs):
        slz = self.get_serializer(data=request.data)
        if slz.is_valid(raise_exception=True):
            project = self.get_project()
            config_dict = configlib.ConfigReader().read("config")
            comment_lines = configlib.ConfigReader().get_comments()
            token, _ = Token.objects.get_or_create(user=request.user)
            config_dict.update({
                'org_sid': project.repo.organization.org_sid,
                'team_name': project.repo.project_team.name,
                'token': token.key,
                'source_dir': slz.validated_data["source_dir"],
                'branch': project.branch,
                'scan_plan': project.scan_scheme.name,
                'total_scan': str(slz.validated_data["total_scan"])
            })
            content = configlib.ConfigWriter().write(section_name="config",
                                                     section_dict=config_dict,
                                                     comment_str="".join(comment_lines))
            response = HttpResponse(content, content_type='APPLICATION/OCTET-STREAM')
            response['Content-Disposition'] = 'attachment; filename=codedog.ini'
            return response


class ProjectScanCreateApiView(generics.CreateAPIView, V3GetModelMixinAPIView):
    """项目创建扫描接口

    ### POST
    应用场景：启动一次项目的扫描任务
    """
    throttle_scope = "create_scan"
    permission_classes = [RepositoryDefaultPermission]
    serializer_class = base_serializers.ServerScanCreateSerializer

    def post(self, request, *args, **kwargs):
        project = self.get_project()
        slz = self.get_serializer(data=request.data)
        slz.is_valid(raise_exception=True)
        try:
            job_id, scan_id = create_server_scan(
                project, creator=UserManager.get_username(request.user), scan_data=slz.validated_data)
            return Response({"job": {"id": job_id}, "scan": {"id": scan_id}})
        except CDErrorBase as err:
            logger.exception(err)
            raise ProjectScanCreateError(code=err.code, msg=err.msg)
        except Exception as err:
            err_msg = "启动任务异常: %s" % err
            logger.exception(err_msg)
            raise ProjectScanCreateError(code=E_SERVER_JOB_CREATE_ERROR, msg=err_msg)
