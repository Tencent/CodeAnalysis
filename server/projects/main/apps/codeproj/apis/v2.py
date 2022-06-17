# -*- coding: utf-8 -*-
"""项目模块V2版本接口
"""
# python 原生import

# 第三方 import
from django.shortcuts import get_object_or_404
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import generics
from rest_framework.permissions import IsAdminUser

# 项目内 import
from apps.codeproj import models
from apps.codeproj.api_filters import base as filters
from apps.codeproj.serializers import base as serializers


class ProjectTeamListAPIView(generics.ListAPIView):
    """项目组列表

    ### GET
    应用场景：获取项目组列表
    """
    permission_classes = [IsAdminUser]
    serializer_class = serializers.ProjectTeamSerializer
    queryset = models.ProjectTeam.objects.exclude(
        organization__status=models.Organization.StatusEnum.FORBIDEN).order_by('-id')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.ProjectTeamFilter


class OrgProjectTeamListAPIView(generics.ListAPIView):
    """指定团队项目组列表

    ### GET
    应用场景：获取指定团队项目组列表
    """
    permission_classes = [IsAdminUser]
    serializer_class = serializers.ProjectTeamSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.ProjectTeamFilter

    def get_queryset(self):
        org_sid = self.kwargs["org_sid"]
        return models.ProjectTeam.objects.filter(organization__org_sid=org_sid)


class OrgProjectTeamDetailAPIView(generics.RetrieveUpdateAPIView):
    """项目组详情

    ### GET
    应用场景：获取项目组详情

    ### PUT
    应用场景：更新项目组
    """
    permission_classes = [IsAdminUser]
    serializer_class = serializers.ProjectTeamSerializer

    def get_object(self):
        org_sid = self.kwargs["org_sid"]
        team_name = self.kwargs["team_name"]
        return get_object_or_404(models.ProjectTeam.objects, name=team_name, organization__org_sid=org_sid)


class OrgProjectTeamStatusAPIView(generics.RetrieveUpdateAPIView):
    """项目组状态

    ### GET
    应用场景：获取项目组简要信息

    ### PUT
    应用场景：更新项目组状态
    """
    permission_classes = [IsAdminUser]
    serializer_class = serializers.ProjectTeamSimpleSerializer

    def get_object(self):
        org_sid = self.kwargs["org_sid"]
        team_name = self.kwargs["team_name"]
        return get_object_or_404(models.ProjectTeam.objects, name=team_name, organization__org_sid=org_sid)
