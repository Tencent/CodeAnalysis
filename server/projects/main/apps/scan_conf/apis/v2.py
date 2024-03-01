# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - v2 apis
"""
import logging

# 第三方
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend

# 项目内
from apps.scan_conf import models
from apps.scan_conf.serializers import v2 as serializers
from apps.scan_conf.api_filters import v2 as filters
from apps.authen.core import OrganizationManager, Organization

logger = logging.getLogger(__name__)


class CheckToolListAPIView(generics.ListAPIView):
    """工具列表

    ### GET
    应用场景：获取平台内全部工具列表，仅superuser
    """
    permission_classes = [IsAdminUser]
    serializer_class = serializers.CheckToolSerializer
    filterset_class = filters.CheckToolFilter
    filter_backends = (DjangoFilterBackend, )
    queryset = models.CheckTool.objects.all().order_by("-id")

    def get_paginated_response(self, data):
        org = OrganizationManager.get_user_orgs(self.request.user).first()
        if not org:
            org = Organization.objects.filter(status=Organization.StatusEnum.ACTIVE).first()
        for checktool in data:
            # 系统工具
            if checktool.get("tool_key") == "default" and org and "org_detail" in checktool.keys():
                checktool["org_detail"]["org_sid"] = org.org_sid
        return super().get_paginated_response(data)


class CheckToolOpenUpdateAPIView(generics.RetrieveUpdateAPIView):
    """修改工具公有/私有

    ### put
    应用场景：修改工具公有/私有

    仅能由superuser修改
    """
    permission_classes = [IsAdminUser]
    serializer_class = serializers.CheckToolOpenUpdateSerializer
    queryset = models.CheckTool.objects.all()
    lookup_url_kwarg = "checktool_id"
