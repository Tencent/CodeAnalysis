# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - v3 checktool, toollib apis
"""
import logging

# 第三方
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError

# 项目内
from apps.scan_conf import models, tasks
from apps.scan_conf.serializers import v3 as serializers
from apps.scan_conf.api_filters import v3 as filters
from apps.scan_conf.permissions import CheckToolDefaultPermission, CheckToolMaintainPermission, \
                                       CheckToolAdminPermission, CheckToolRuleDetaultPermission, \
                                       ToolLibDefaultPermission
from apps.scan_conf.core import FilterManger, ToolLibMapManager, ToolLibSchemeManager, \
                                ToolLibManager, CheckToolManager, CheckRuleManager
from apps.base.models import OperationRecord
from apps.base.serializers import OperationRecordSerializer
from apps.base.apimixins import CustomSerilizerMixin, V3GetModelMixinAPIView
from apps.authen.permissions import OrganizationDefaultPermission

logger = logging.getLogger(__name__)


class CheckToolListAPIView(CustomSerilizerMixin, generics.ListCreateAPIView, V3GetModelMixinAPIView):
    """工具列表接口

    ### get
    应用场景：获取团队内可用的工具列表

    ### post
    应用场景：创建工具，当前团队作为工具负责团队
    """
    permission_classes = [OrganizationDefaultPermission]
    serializer_class = serializers.CheckToolSerializer
    post_serializer_class = serializers.CheckToolEditSeriaizer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = filters.CheckToolFilter

    def get_queryset(self):
        org = self.get_org()
        queryset = CheckToolManager.filter_usable(org=org)
        try:
            scope = int(self.request.query_params.get("scope"))
        except (ValueError, TypeError):
            scope = None
        if scope == models.CheckTool.ScopeEnum.CUSTOM:
            tool_key = CheckToolManager.get_tool_key(org=org)
            queryset = queryset.filter(tool_key=tool_key)
        return queryset


class CheckToolDetailAPIView(CustomSerilizerMixin, generics.RetrieveUpdateAPIView, V3GetModelMixinAPIView):
    """工具详情接口

    ### get
    应用场景：获取工具详情，工具负责团队的管理员能够看到工具详细信息

    ### put
    应用场景：更新工具，工具负责团队的管理员能够更新工具
    """
    permission_classes = [CheckToolDefaultPermission]
    serializer_class = serializers.CheckToolSerializer
    detail_serializer_class = serializers.CheckToolDetailSeriaizer
    put_serializer_class = serializers.CheckToolEditSeriaizer
    lookup_url_kwarg = "checktool_id"

    def get_queryset(self):
        # 暂时加上is_superuser判断
        if self.request.user.is_superuser:
            return models.CheckTool.objects.all().order_by('-modified_time')
        return CheckToolManager.filter_usable(org=self.get_org())

    def get_serializer_class(self):
        if self.request.method == 'GET':
            org = self.get_org()
            checktool = self.get_checktool()
            # 可编辑权限能查看到更多的规则信息，暂时加上is_superuser判断
            if self.request.user.is_superuser or CheckToolManager.check_edit_perm(org, checktool, self.request.user):
                return self.detail_serializer_class
        return super().get_serializer_class()


class CheckToolWhiteListAPIView(generics.ListCreateAPIView, V3GetModelMixinAPIView):
    """工具白名单列表接口

    ### get
    应用场景：获取工具白名单团队列表

    ### post
    应用场景：添加工具白名单团队
    """
    permission_classes = [CheckToolAdminPermission]
    serializer_class = serializers.CheckToolWhiteKeySerializer
    pagination_class = None

    def get_queryset(self):
        checktool = self.get_checktool()
        return models.CheckToolWhiteKey.objects.filter(tool_id=checktool.id)


class CheckToolWhiteDetailAPIView(generics.DestroyAPIView, V3GetModelMixinAPIView):
    """工具白名单详情接口

    ### del
    应用场景：删除工具白名单团队
    """
    permission_classes = [CheckToolAdminPermission]

    def get_object(self):
        whitelist_id = self.kwargs["whitelist_id"]
        checktool = self.get_checktool()
        return get_object_or_404(models.CheckToolWhiteKey, id=whitelist_id, tool_id=checktool.id)


class CheckToolWhiteBatchCreateAPIView(generics.GenericAPIView, V3GetModelMixinAPIView):
    """批量创建工具白名单接口

    ### post
    应用场景：批量创建工具白名单接口
    """
    permission_classes = [CheckToolAdminPermission]
    serializer_class = serializers.CheckToolWhiteKeyAddSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        checktool = self.get_checktool()
        orgs = serializer.validated_data.get("organizations")
        for org in orgs:
            tool_key = CheckToolManager.get_tool_key(org=org)
            CheckToolManager.add_white_key(tool_key=tool_key, tool_id=checktool.id)
        return Response("已成功批量添加工具白名单")


class CheckToolWhiteBatchDeleteAPIView(generics.GenericAPIView, V3GetModelMixinAPIView):
    """批量删除工具白名单接口

    ### del
    应用场景：批量删除工具白名单
    """
    permission_classes = [CheckToolAdminPermission]
    serializer_class = serializers.CheckToolWhiteKeyDeleteSerializer

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        checktool = self.get_checktool()
        whitelist = serializer.validated_data.get("whitelist")
        models.CheckToolWhiteKey.objects.filter(tool_id=checktool.id, id__in=whitelist).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CheckToolStatusAPIView(generics.UpdateAPIView, V3GetModelMixinAPIView):
    """修改工具状态接口

    ### put
    应用场景：修改工具运营状态
    """
    permission_classes = [CheckToolDefaultPermission]
    serializer_class = serializers.CheckToolStatusUpdateSerializer

    def get_object(self):
        return self.get_checktool()


class CheckToolOperationRecordListAPIView(generics.ListAPIView, V3GetModelMixinAPIView):
    """工具操作记录列表接口

    ### get
    应用场景：获取工具操作记录
    """

    permission_classes = [CheckToolAdminPermission]
    serializer_class = OperationRecordSerializer

    def get_queryset(self):
        checktool = self.get_checktool()
        return OperationRecord.objects.filter(scenario_key="checktool_%d" % checktool.id).order_by("-id")


class CheckToolRuleListAPIView(CustomSerilizerMixin, generics.ListCreateAPIView, V3GetModelMixinAPIView):
    """工具规则列表接口

    ### get
    应用场景：获取工具规则列表

    ### post
    应用场景：创建工具规则
    """
    permission_classes = [CheckToolDefaultPermission]
    serializer_class = serializers.CheckRuleSerializer
    post_serializer_class = serializers.CheckToolRuleSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = filters.CheckRuleFilter

    def get_queryset(self):
        checktool = self.get_checktool()
        return CheckRuleManager.filter_tool_all(checktool)

    def get_serializer_class(self):
        if self.request and self.request.method == 'GET':
            org = self.get_org()
            checktool = self.get_checktool()
            # 可编辑权限能查看到更多的规则信息，暂时加上is_superuser判断
            if self.request.user.is_superuser or CheckToolManager.check_edit_perm(org, checktool, self.request.user):
                return self.post_serializer_class
        return super().get_serializer_class()


class CheckToolRuleDetailAPIView(CustomSerilizerMixin, generics.RetrieveUpdateDestroyAPIView, V3GetModelMixinAPIView):
    """工具规则详情接口

    ### GET
    应用场景：获取工具规则详情

    ### PUT
    应用场景：更新工具规则

    ### DELETE
    应用场景：移除工具规则
    """
    permission_classes = [CheckToolRuleDetaultPermission]
    serializer_class = serializers.CheckRuleSerializer
    put_serializer_class = serializers.CheckToolRuleSerializer

    def get_object(self):
        return self.get_checktool_rule()

    def perform_destroy(self, instance):
        """
        移除规则
        """
        user = self.request.user
        checktool = instance.checktool
        instance.deleter = user
        instance.deleted_time = timezone.now()
        instance.save(user=user)
        tasks.checktool_to_delrule.delay(checktool.id, [instance.id], user.username)


class CheckToolRuleFilterAPIView(APIView, V3GetModelMixinAPIView):
    """获取工具规则的筛选项

    ### get
    应用场景：获取工具规则列表filter
    """
    permission_classes = [CheckToolDefaultPermission]

    def get(self, request, *args, **kwargs):
        checktool = self.get_checktool()
        queryset = CheckRuleManager.filter_tool_all(checktool)
        filter_map = FilterManger.get_checktool_rules_filter(queryset)
        return Response(data=filter_map)


class CheckToolRuleCustomListAPIView(CheckToolRuleListAPIView):
    """工具自定义规则列表接口

    ### get
    应用场景：获取团队该工具下的自定义规则列表

    ### post
    应用场景：添加工具自定义规则
    """
    permission_classes = [CheckToolMaintainPermission]
    post_serializer_class = serializers.CheckToolCustomRuleSerializer

    def get_queryset(self):
        org = self.get_org()
        checktool = self.get_checktool()
        tool_key = CheckToolManager.get_tool_key(org=org)
        return models.CheckRule.objects.filter(checktool=checktool, tool_key=tool_key).order_by("-id")


class CheckToolRuleCustomDetailAPIView(CheckToolRuleDetailAPIView):
    """工具自定义规则详情接口

    ### GET
    应用场景：获取自定义规则详情

    ### PUT
    应用场景：更新自定义规则

    ### DELETE
    应用场景：删除自定义规则
    """
    permission_classes = [CheckToolMaintainPermission]


class CheckToolRuleCustomFilterAPIView(APIView, V3GetModelMixinAPIView):
    """工具自定义规则的筛选项

    ### get
    应用场景：获取工具自定义规则筛选项
    """
    permission_classes = [CheckToolMaintainPermission]

    def get(self, request, *args, **kwargs):
        org = self.get_org()
        checktool = self.get_checktool()
        tool_key = CheckToolManager.get_tool_key(org=org)
        queryset = models.CheckRule.objects.filter(checktool=checktool, tool_key=tool_key)
        filter_map = FilterManger.get_checktool_rules_filter(queryset)
        return Response(data=filter_map)


class ToolLibListAPIView(CustomSerilizerMixin, generics.ListCreateAPIView, V3GetModelMixinAPIView):
    """工具依赖列表接口

    ### get
    应用场景：获取团队内可用工具列表

    ### post
    应用场景：创建工具依赖
    """
    permission_classes = [OrganizationDefaultPermission]
    serializer_class = serializers.ToolLibSerializer
    post_serializer_class = serializers.ToolLibEditSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = filters.ToolLibFilter

    def get_queryset(self):
        org = self.get_org()
        return ToolLibManager.filter_usable(org=org)


class ToolLibDetailAPIView(CustomSerilizerMixin, generics.RetrieveUpdateAPIView, V3GetModelMixinAPIView):
    """工具依赖详情接口

    ### get
    应用场景：获取工具依赖详情，工具依赖负责团队的管理员能够看到工具依赖详细信息

    ### put
    应用场景：更新工具依赖，工具依赖负责团队管理员能够更新工具依赖
    """
    permission_classes = [ToolLibDefaultPermission]
    serializer_class = serializers.ToolLibSerializer
    detail_serializer_class = serializers.ToolLibDetailSeriaizer
    put_serializer_class = serializers.ToolLibEditSerializer
    lookup_url_kwarg = "toollib_id"

    def get_queryset(self):
        return ToolLibManager.filter_usable(org=self.get_org())

    def get_serializer_class(self):
        if self.request and self.request.method == 'GET':
            org = self.get_org()
            toollib = self.get_toollib()
            # 可编辑权限能查看到更多的规则信息，暂时加上is_superuser判断
            if self.request.user.is_superuser or ToolLibManager.check_edit_perm(org, toollib, self.request.user):
                return self.detail_serializer_class
        return super().get_serializer_class()


class CheckToolSchemeListAPIView(generics.ListCreateAPIView, V3GetModelMixinAPIView):
    """工具-依赖方案列表接口

    ### get
    应用场景：获取工具依赖方案列表

    ### post
    应用场景：创建工具依赖方案列表
    """
    permission_classes = [CheckToolDefaultPermission]
    serializer_class = serializers.ToolLibSchemeSerializer
    pagination_class = None

    def get_queryset(self):
        checktool = self.get_checktool()
        return models.ToolLibScheme.objects.filter(checktool=checktool)


class CheckToolSchemeDetailAPIView(generics.RetrieveUpdateDestroyAPIView, V3GetModelMixinAPIView):
    """工具-依赖方案详情接口

    ### get
    应用场景：获取工具依赖方案详情

    ### put
    应用场景：更新工具依赖方案信息

    ### delete
    应用场景：移除工具依赖方案
    """
    permission_classes = [CheckToolDefaultPermission]
    serializer_class = serializers.ToolLibSchemeSerializer
    lookup_url_kwarg = "libscheme_id"

    def get_queryset(self):
        checktool = self.get_checktool()
        return models.ToolLibScheme.objects.filter(checktool=checktool)

    def perform_destroy(self, instance):
        ToolLibSchemeManager.delete(instance, self.request.user)


class CheckToolSchemeLibListAPIView(CustomSerilizerMixin, generics.ListCreateAPIView, V3GetModelMixinAPIView):
    """工具-依赖方案-依赖映射列表接口

    ### get
    应用场景：获取工具依赖列表

    ### post
    应用场景：关联工具依赖
    """
    permission_classes = [CheckToolDefaultPermission]
    serializer_class = serializers.ToolLibMapDetailSerializer
    post_serializer_class = serializers.ToolLibMapSerializer
    pagination_class = None

    def get_queryset(self):
        libscheme = self.get_libscheme()
        return models.ToolLibMap.objects.filter(libscheme=libscheme)


class CheckToolSchemeLibDetailAPIView(generics.RetrieveDestroyAPIView, V3GetModelMixinAPIView):
    """工具-依赖方案-依赖映射详情接口

    ### get
    应用场景：获取工具依赖映射详情

    ### delete
    应用场景：移除工具依赖映射
    """
    permission_classes = [CheckToolDefaultPermission]
    serializer_class = serializers.ToolLibMapDetailSerializer
    lookup_url_kwarg = "libmap_id"

    def get_queryset(self):
        libscheme = self.get_libscheme()
        return models.ToolLibMap.objects.filter(libscheme=libscheme)

    def perform_destroy(self, instance):
        ToolLibMapManager.delete(instance, self.request.user)


class CheckToolSchemeLibDragSortAPIView(APIView, V3GetModelMixinAPIView):
    """工具-依赖方案-依赖映射-拖拽排序接口

    ### post
    应用场景：工具内进行依赖的拖拽排序
    必传data：
    drag_type: 拖拽类型，before、after
    """
    permission_classes = [CheckToolDefaultPermission]

    def post(self, request, *args, **kwargs):
        libmap_id = kwargs['libmap_id']
        target_libmap_id = kwargs['target_libmap_id']
        libscheme = self.get_libscheme()
        source_lib_map = get_object_or_404(models.ToolLibMap, libscheme=libscheme, id=libmap_id)
        target_lib_map = models.ToolLibMap.objects.filter(libscheme=libscheme, id=target_libmap_id).first()
        if not target_lib_map:
            raise ParseError('该工具依赖方案内目标依赖不存在')
        drag_type = request.data.get('drag_type')
        if drag_type not in dict(ToolLibMapManager.DRAG_CHOICES):
            raise ParseError('请传入合法的拖拽类型')
        ToolLibMapManager.drag_sort(source_lib_map, target_lib_map, drag_type)
        return Response({'detail': '拖拽排序完成'})
