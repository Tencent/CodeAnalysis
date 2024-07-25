# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - v3 apis for scheme
"""

# 原生
import logging

# 第三方
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.response import Response

# 项目内
from apps.codeproj import models, tasks
from apps.codeproj.serializers import v3_scheme as v3_scheme_serializers, v3 as v3_serializers
from apps.codeproj.api_filters import base as base_filters
from apps.codeproj.core import ScanSchemeManager
from apps.codeproj.permissions import GlobalSchemeDefaultPermission
from apps.authen.permissions import OrganizationOperationPermission

from apps.base.apimixins import CustomSerilizerMixin, V3GetModelMixinAPIView

logger = logging.getLogger(__name__)


class ScanSchemeListApiView(CustomSerilizerMixin, generics.ListCreateAPIView, V3GetModelMixinAPIView):
    """分析方案模板列表接口

    ### GET
    应用场景：获取分析方案列表
    筛选项：
    ```python
    name: str, 方案模板名称，包含
    scope: str, 过滤范围，all全部，system系统模板，not_system非系统模板，editable有权限编辑模板
    ```

    ### POST
    创建新的扫描方案
    """
    permission_classes = [OrganizationOperationPermission]
    serializer_class = v3_scheme_serializers.GlobalScanSchemeTemplateSerializer
    post_serializer_class = v3_scheme_serializers.GlobalScanSchemeTemplateCreateSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = base_filters.GlobalScanSchemeTemplateFilter

    def get_queryset(self):
        org = self.get_org()
        return ScanSchemeManager.filter_usable_global_scheme_templates(org.org_sid, self.request.user)


class ScanSchemeDetailApiView(generics.RetrieveUpdateAPIView, V3GetModelMixinAPIView):
    """分析方案模板详情接口

    ### GET
    应用场景：获取分析方案模板详情

    ### PUT
    应用场景：更新分析方案模板详情
    """
    permission_classes = [GlobalSchemeDefaultPermission]
    serializer_class = v3_scheme_serializers.GlobalScanSchemeTemplateSerializer

    def get_object(self):
        return self.get_scheme()


class ScanSchemePermConfApiView(generics.RetrieveUpdateAPIView, V3GetModelMixinAPIView):
    """扫描方案权限配置

    ### GET
    应用场景：获取指定扫描方案的权限信息

    ### PUT
    应用场景：更新指定扫描方案的权限信息
    """
    permission_classes = [GlobalSchemeDefaultPermission]
    serializer_class = v3_scheme_serializers.ScanSchemePermConfSerializer

    def get_object(self):
        scan_scheme = self.get_scheme()
        scan_scheme_perm, _ = models.ScanSchemePerm.objects.get_or_create(scan_scheme=scan_scheme)
        return scan_scheme_perm


class ScanSchemeChildrenListApiView(generics.ListAPIView, V3GetModelMixinAPIView):
    """模板子扫描方案列表

    ### GET
    应用场景：获取指定模板的子扫描方案列表
    """
    permission_classes = [GlobalSchemeDefaultPermission]
    serializer_class = v3_serializers.ScanSchemeRepoInfoSimpleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = base_filters.GlobalScanSchemeTemplateChildrenFilter

    def get_queryset(self):
        scan_scheme = self.get_scheme()
        # 获取活跃的分析方案
        return models.ScanScheme.objects.filter(refer_scheme=scan_scheme, repo__isnull=False,
                                                status=models.ScanScheme.StatusEnum.ACTIVE).exclude(
            repo__deleted_time__isnull=False)


class ScanSchemePushApiView(generics.GenericAPIView, V3GetModelMixinAPIView):
    """模板同步操作
    """

    permission_classes = [GlobalSchemeDefaultPermission]
    serializer_class = v3_scheme_serializers.GlobalScanSchemeTemplatePushSerializer

    def post(self, request, *args, **kwargs):
        scan_scheme = self.get_scheme()
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
