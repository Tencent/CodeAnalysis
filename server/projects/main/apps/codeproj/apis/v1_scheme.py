# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - api v1 for scheme templates
"""
# 原生
import logging

# 第三方
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics

# 项目内
from apps.authen.permissions import OrganizationOperationPermission
from apps.base.apimixins import V3GetModelMixinAPIView
from apps.codeproj.api_filters import base as base_filters
from apps.codeproj.apis import v1
from apps.codeproj.core import ScanSchemeManager
from apps.codeproj.permissions import GlobalSchemeDefaultPermission
from apps.codeproj.serializers import v3_scheme as v3_scheme_serializers

logger = logging.getLogger(__name__)


class OrgScanSchemeListAPIView(generics.ListAPIView, V3GetModelMixinAPIView):
    """分析方案模板列表接口

    ### GET
    应用场景：获取分析方案列表
    筛选项：
    ```python
    name: str, 方案模板名称，包含
    scope: str, 过滤范围，all全部，system系统模板，not_system非系统模板，editable有权限编辑模板
    ```
    """
    permission_classes = [OrganizationOperationPermission]
    serializer_class = v3_scheme_serializers.GlobalScanSchemeTemplateSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = base_filters.GlobalScanSchemeTemplateFilter

    def get_queryset(self):
        org = self.get_org()
        return ScanSchemeManager.filter_usable_global_scheme_templates(org.org_sid, self.request.user)


class OrgScanSchemeDetailAPIView(generics.RetrieveAPIView, V3GetModelMixinAPIView):
    """分析方案模板详情接口

    ### GET
    应用场景：获取分析方案模板详情
    """
    permission_classes = [GlobalSchemeDefaultPermission]
    serializer_class = v3_scheme_serializers.GlobalScanSchemeTemplateSerializer

    def get_object(self):
        return self.get_scheme()


class OrgScanSchemeScanJobConfAPIView(v1.ScanSchemeScanJobConfApiView):
    """获取指定扫描方案模板的扫描配置

    ### GET
    应用场景：获取指定扫描方案模板配置的api，供节点端离线扫描使用
    """
    permission_classes = [GlobalSchemeDefaultPermission]
