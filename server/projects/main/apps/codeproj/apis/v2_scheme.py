# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - v2 apis for scheme
"""

# python 原生import
import logging

# 第三方 import
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# 项目内import
from apps.base.apimixins import CustomSerilizerMixin
from apps.base.models import OperationRecord
from apps.base.serializers import OperationRecordSerializer
from apps.codeproj import models
from apps.codeproj import tasks
from apps.codeproj.api_filters import base as base_filters
from apps.codeproj.core import ScanSchemeManager
from apps.codeproj.serializers import base as base_serializers
from apps.codeproj.serializers import base_scheme
from util.operationrecord import OperationRecordHandler
from util.permissions import ScanSchemePermission

logger = logging.getLogger(__name__)


class ScanSchemeListApiView(CustomSerilizerMixin, generics.ListCreateAPIView):
    """扫描方案列表接口
    1. 支持用户筛选平台通用的、当前组织内的、自己创建的或有权限的扫描方案
    2. 支持用户创建扫描方案

    ### GET
    获取扫描方案列表

    ### POST
    创建新的扫描方案
    """
    serializer_class = base_scheme.GlobalScanSchemeTemplateSerializer
    post_serializer_class = base_scheme.GlobalScanSchemeTemplateCreateSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = base_filters.GlobalScanSchemeTemplateFilter

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return models.ScanScheme.objects.filter(repo__isnull=True)
        return ScanSchemeManager.filter_usable_global_scheme_templates('default', user)


class ScanSchemeDetailApiView(generics.RetrieveUpdateAPIView):
    """扫描方案详情接口
    1. 支持用户查阅平台通用的、自己创建的或有权限的扫描方案详情
    2. 支持用户编辑自己创建的或有权限的扫描方案详情

    ### GET
    获取指定的扫描方案

    ### PUT
    更新指定的扫描方案
    """
    permission_classes = [ScanSchemePermission]
    serializer_class = base_scheme.GlobalScanSchemeTemplateSerializer

    def get_object(self):
        scan_scheme_id = self.kwargs["scheme_id"]
        return get_object_or_404(models.ScanScheme, id=scan_scheme_id, repo=None)


class ScanSchemeLintConfApiView(generics.RetrieveUpdateAPIView):
    """扫描方案代码扫描配置接口
    1. 支持用户查阅平台通用的、自己创建的或有权限的扫描方案详情
    2. 支持用户编辑自己创建的或有权限的扫描方案详情

    ### GET
    应用场景：获取指定扫描方案的lint配置

    ### PUT
    应用场景：更新指定扫描方案的lint配置
    """
    permission_classes = [ScanSchemePermission]
    serializer_class = base_serializers.LintBaseSettingConfSerializer

    def get_object(self):
        scan_scheme_id = self.kwargs["scheme_id"]
        scan_scheme = get_object_or_404(models.ScanScheme, id=scan_scheme_id, repo=None)
        return get_object_or_404(models.LintBaseSetting, scan_scheme=scan_scheme)


class ScanSchemeMetricConfApiView(generics.RetrieveUpdateAPIView):
    """扫描方案指定代码度量配置
    1. 支持用户查阅平台通用的、自己创建的或有权限的扫描方案详情
    2. 支持用户编辑自己创建的或有权限的扫描方案详情

    ### GET
    应用场景：获取指定扫描方案的metric配置

    ### PUT
    应用场景：更新指定扫描方案的metric配置
    """
    permission_classes = [ScanSchemePermission]
    serializer_class = base_serializers.MetricSettingConfSerializer

    def get_object(self):
        scan_scheme_id = self.kwargs["scheme_id"]
        scan_scheme = get_object_or_404(models.ScanScheme, id=scan_scheme_id, repo=None)
        return get_object_or_404(models.MetricSetting, scan_scheme=scan_scheme)


class ScanSchemeDirListApiView(generics.ListCreateAPIView):
    """扫描方案指定扫描目录列表管理接口
    1. 支持用户查阅平台通用的、自己创建的或有权限的扫描方案详情
    2. 支持用户编辑自己创建的或有权限的扫描方案详情

    ### GET
    应用场景：获取指定扫描方案的扫描目录列表

    ### POST
    应用场景：创建指定扫描方案的扫描目录
    """
    serializer_class = base_serializers.ScanDirConfSerializer
    permission_classes = [ScanSchemePermission]

    def get_queryset(self):
        scan_scheme_id = self.kwargs["scheme_id"]
        scan_scheme = get_object_or_404(models.ScanScheme, id=scan_scheme_id, repo=None)
        return models.ScanDir.objects.filter(scan_scheme=scan_scheme).order_by("-id")


class ScanSchemeDirBulkCreateApiView(generics.GenericAPIView):
    """扫描方案过滤路径，批量增加扫描目录
    ### POST
    批量创建过滤路径
    """
    serializer_class = base_serializers.ScanDirConfBulkCreateSerialzier
    permission_classes = [ScanSchemePermission]

    def post(self, request, scheme_id):
        scan_scheme = get_object_or_404(models.ScanScheme, id=scheme_id, repo=None)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            scandirs = serializer.validated_data["scandirs"]
            new_scandirs = []
            ignore_num = 0
            for scandir in scandirs:
                dir_path = scandir.get("dir_path")
                # 忽略已存在的路径
                scandir_model = models.ScanDir.objects.filter(
                    scan_scheme=scan_scheme, dir_path=dir_path).first()
                if not scandir_model:
                    models.ScanDir.objects.create(
                        scan_scheme=scan_scheme, **scandir)
                    new_scandirs.append(scandir)
                else:
                    ignore_num += 1
            new_num = len(new_scandirs)
            if new_num > 0:
                OperationRecordHandler.add_scanscheme_operation_record(
                    scan_scheme, "批量新增过滤目录", request.user, new_scandirs)
            detail = "批量创建%s条路径" % new_num
            if ignore_num > 0:
                detail = "%s，忽略%s条路径（已存在）" % (detail, ignore_num)
            return Response({"detail": detail})


class ScanSchemeDirClearApiView(APIView):
    """移除所有过滤路径配置
    """
    permission_classes = [ScanSchemePermission]

    def delete(self, request, scheme_id):
        scan_scheme = get_object_or_404(models.ScanScheme, id=scheme_id, repo=None)
        scandirs = models.ScanDir.objects.filter(scan_scheme=scan_scheme)
        if scandirs:
            scandirs.delete()
            OperationRecordHandler.add_scanscheme_operation_record(
                scan_scheme, "清空过滤目录", request.user, "一键清空[扫描方案：%s]的过滤路径" % scan_scheme.name)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ScanSchemeDirDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    """扫描方案指定扫描目录详情管理接口

    ### GET
    应用场景：获取指定扫描方案的指定扫描目录

    ### PUT
    应用场景：更新指定扫描方案的指定扫描目录

    ### DELETE
    应用场景：删除指定扫描方案的指定扫描目录
    """
    permission_classes = [ScanSchemePermission]
    serializer_class = base_serializers.ScanDirConfSerializer
    lookup_url_kwarg = "dir_id"

    def get_queryset(self):
        return models.ScanDir.objects.filter(scan_scheme_id=self.kwargs["scheme_id"]).order_by("dir_path")

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        response = generics.RetrieveUpdateDestroyAPIView.update(self, request, *args, **kwargs)
        OperationRecordHandler.add_scanscheme_operation_record(instance.scan_scheme, "修改过滤目录", request.user,
                                                               request.data)
        return response

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        OperationRecordHandler.add_scanscheme_operation_record(
            instance.scan_scheme, "删除过滤目录", request.user, "dir_path:%s scan_type:%s" % (
                instance.dir_path, instance.scan_type))
        return generics.RetrieveUpdateDestroyAPIView.destroy(self, request, *args, **kwargs)


class ScanSchemePermConfApiView(generics.RetrieveUpdateAPIView):
    """扫描方案权限配置

    ### GET
    应用场景：获取指定扫描方案的权限信息

    ### PUT
    应用场景：更新指定扫描方案的权限信息
    """

    serializer_class = base_serializers.ScanSchemePermConfSerializer
    permission_classes = [ScanSchemePermission]

    def get_object(self):
        scan_scheme_id = self.kwargs["scheme_id"]
        scan_scheme = get_object_or_404(models.ScanScheme, id=scan_scheme_id, repo=None)
        scan_scheme_perm, created = models.ScanSchemePerm.objects.get_or_create(scan_scheme=scan_scheme)
        return scan_scheme_perm


class ScanSchemeChildrenListApiView(generics.ListAPIView):
    """模板子扫描方案列表

    ### GET
    应用场景：获取指定模板的子扫描方案列表
    """
    serializer_class = base_serializers.ScanSchemeRepoInfoSimpleSerializer
    permission_classes = [ScanSchemePermission]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = base_filters.GlobalScanSchemeTemplateChildrenFilter

    def get_queryset(self):
        scan_scheme_id = self.kwargs["scheme_id"]
        scan_scheme = get_object_or_404(models.ScanScheme, id=scan_scheme_id, repo=None)
        # 获取活跃的分析方案
        return models.ScanScheme.objects.filter(refer_scheme=scan_scheme, repo__isnull=False,
                                                status=models.ScanScheme.StatusEnum.ACTIVE)


class ScanSchemePushApiView(generics.GenericAPIView):
    """模板同步操作
    """

    permission_classes = [ScanSchemePermission]
    serializer_class = base_scheme.GlobalScanSchemeTemplatePushSerializer

    def post(self, request, scheme_id):
        scan_scheme = get_object_or_404(models.ScanScheme, id=scheme_id, repo=None)
        slz = self.get_serializer(data=request.data)
        if slz.is_valid(raise_exception=True):
            data = slz.data
            scheme_ids = data.pop('schemes', [])
            if data.pop("all_schemes", False):
                # 选择全部分析方案
                scheme_ids = models.ScanScheme.objects.filter(refer_scheme=scan_scheme, repo__isnull=False) \
                    .values_list('id', flat=True)
            tasks.push_scanscheme_template.delay(scheme_ids, scan_scheme.id, username=request.user.username, **data)
            return Response(slz.data)


class ScanSchemeDefaultScanPathListApiView(CustomSerilizerMixin, generics.ListCreateAPIView):
    """

    ### GET
    获取指定扫描方案的默认过滤路径
    > exclude=1表示筛选被屏蔽了的路径列表

    ### POST
    在指定扫描方案屏蔽指定默认路径
    """

    permission_classes = [ScanSchemePermission]
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
        scan_scheme = get_object_or_404(
            models.ScanScheme, id=self.kwargs["scheme_id"], repo__isnull=True)
        if self.get_exclude_paths():
            # 筛选屏蔽的默认路径
            default_scan_paths = models.DefaultScanPath.objects.filter(
                schemedefaultscanpathexcludemap__scan_scheme=scan_scheme)
        else:
            # 筛选未屏蔽的默认路径
            default_scan_paths = models.DefaultScanPath.objects.exclude(
                schemedefaultscanpathexcludemap__scan_scheme=scan_scheme)
        return default_scan_paths


class ScanSchemeDefaultScanPathDetailApiView(generics.RetrieveDestroyAPIView):
    """
    ### GET
    获取指定扫描方案指定屏蔽的过滤路径

    ### DELETE
    在指定扫描方案取消屏蔽指定过滤路径
    """
    permission_classes = [ScanSchemePermission]
    serializer_class = base_serializers.SchemeDefaultScanPathExcludeMapSerializer

    def get_object(self):
        """获取指定对象
        """
        scanscheme_path_map = get_object_or_404(
            models.SchemeDefaultScanPathExcludeMap, scan_scheme_id=self.kwargs["scheme_id"],
            scan_scheme__repo__isnull=True, default_scan_path_id=self.kwargs["path_id"])
        return scanscheme_path_map

    def destroy(self, request, *args, **kwargs):
        """删除指定对象
        """
        instance = self.get_object()
        OperationRecordHandler.add_scanscheme_operation_record(
            instance.scan_scheme, "修改过滤路径", request.user,
            "取消屏蔽默认过滤路径:%s " % instance.default_scan_path.dir_path)
        return super().destroy(request, *args, **kwargs)


class ScanSchemeOperationRecordListApiView(generics.ListAPIView):
    """方案模板操作记录

    ### GET
    应用场景：获取方案模板的操作历史记录（默认倒序）
    """
    serializer_class = OperationRecordSerializer
    permission_classes = [ScanSchemePermission]

    def get_queryset(self):
        scheme_id = self.kwargs["scheme_id"]
        return OperationRecord.objects.filter(scenario_key="scanscheme_%s" % scheme_id).order_by("-id")
