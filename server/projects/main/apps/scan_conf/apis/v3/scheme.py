# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - v3 scheme checkpackage,checkprofile apis
"""
import logging

# 第三方
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError, NotFound

# 项目内
from apps.scan_conf import models
from apps.scan_conf.serializers import v3 as serializers
from apps.scan_conf.api_filters import v3 as filters
from apps.scan_conf.core import FilterManger, CheckToolManager, CheckRuleManager, \
                                CheckProfileManager, CheckPackageManager
from apps.base.apimixins import CustomSerilizerMixin, V3GetModelMixinAPIView
from apps.codeproj.permissions import SchemeDefaultPermission

logger = logging.getLogger(__name__)


class ScanSchemeCheckProfileDetailAPIView(generics.RetrieveAPIView, V3GetModelMixinAPIView):
    """分析方案-规则配置详情接口

    ### get
    应用场景：获取分析方案规则配置详情，包含自定义规则包详情
    """
    permission_classes = [SchemeDefaultPermission]
    serializer_class = serializers.ScanSchemeCheckProfileSimpleSerializer

    def get_object(self):
        return self.get_checkprofile()


class ScanSchemePackageListAPIView(CustomSerilizerMixin, generics.ListCreateAPIView, V3GetModelMixinAPIView):
    """分析方案-规则配置-官方规则包列表接口

    ### get
    应用场景：获取当前分析方案已配置的官方规则包列表

    ### post
    应用场景：给当前分析方案添加官方规则包

    - 参数说明：（以此为准）
    ```python
    {
      "checkpackages": [x] # int, 官方规则包id
    }
    ```
    """
    permission_classes = [SchemeDefaultPermission]
    serializer_class = serializers.ScanSchemeCheckPackageSerializer
    post_serializer_class = serializers.CheckProfilePackageAddSerializer

    def create(self, request, *args, **kwargs):
        checkprofile = self.get_checkprofile()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        checkpackages = serializer.validated_data.pop("checkpackages")
        CheckProfileManager.add_official_pkgs(checkprofile, checkpackages, request.user)
        return Response({"detail": "已批量添加官方规则包"}, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        checkprofile = self.get_checkprofile()
        return checkprofile.checkpackages.order_by("-id")


class ScanSchemePackageDetailAPIView(generics.RetrieveDestroyAPIView, V3GetModelMixinAPIView):
    """分析方案-规则配置-规则包详情接口

    ### get
    应用场景：获取规则包详情，官方规则包或该规则配置的自定义规则包详情

    ### DELETE
    应用场景：移除指定规则包，仅能移除官方规则包
    """
    permission_classes = [SchemeDefaultPermission]
    serializer_class = serializers.ScanSchemeCheckPackageSerializer

    def get_object(self):
        checkpackage, _ = self.get_checkprofile_checkpackage()
        return checkpackage

    def delete(self, request, *args, **kwargs):
        checkpackage, checkprofile = self.get_checkprofile_checkpackage()
        CheckProfileManager.rm_official_pkgs(checkprofile, [checkpackage], request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ScanSchemePackageRuleListAPIView(generics.ListAPIView, V3GetModelMixinAPIView):
    """分析方案-规则配置-规则包规则列表接口

    ### get
    应用场景：获取规则配置的官方规则包下的规则列表

    注：如果该规则已在自定义规则包中定义，则存在custom_packagemap，否则为[]。前端显示时根据需要看取哪种packagemap
    """
    permission_classes = [SchemeDefaultPermission]
    serializer_class = serializers.ScanSchemePackageMapSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.PackageMapFilter

    def get_queryset(self):
        checkpackage, _ = self.get_checkprofile_checkpackage()
        return models.PackageMap.objects.filter(checkpackage=checkpackage).order_by("-id")

    def get_paginated_response(self, data):
        checkpackage, checkprofile = self.get_checkprofile_checkpackage()
        if checkpackage.id != checkprofile.custom_checkpackage_id:
            checkprofile = self.get_checkprofile()
            # 自定义的规则列表
            custom_pms = models.PackageMap.objects.filter(checkpackage_id=checkprofile.custom_checkpackage_id)
            custom_pm_dict = {pm.checkrule_id: pm for pm in custom_pms}
            new_data = []
            for pm in data:
                rule_id = pm.get("checkrule").get("id")
                pm["custom_packagemap"] = [self.serializer_class(custom_pm_dict[rule_id]).data] \
                    if rule_id in custom_pm_dict else []
                new_data.append(pm)
            return super().get_paginated_response(new_data)
        return super().get_paginated_response(data)


class ScanSchemePackageRuleFilterAPIView(APIView, V3GetModelMixinAPIView):
    """分析方案-规则配置-规则包规则筛选项接口

    ### get
    应用场景：获取规则包下所有规则的筛选项options
    """
    permission_classes = [SchemeDefaultPermission]

    def get(self, request, *args, **kwargs):
        checkpackage, _ = self.get_checkprofile_checkpackage()
        queryset = models.PackageMap.objects.filter(checkpackage=checkpackage)
        filter_map = FilterManger.get_checkpackage_rules_filter(queryset, filters.PackageMapFilter, user=request.user)
        return Response(data=filter_map)


class ScanSchemeCheckProfileRuleListAPIView(generics.ListAPIView, V3GetModelMixinAPIView):
    """分析方案-规则配置-自定义规则包规则列表接口

    ### get
    应用场景：获取自定义规则包的规则列表
    """
    permission_classes = [SchemeDefaultPermission]
    serializer_class = serializers.ScanSchemePackageMapSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.PackageMapFilter

    def get_queryset(self):
        checkprofile = self.get_checkprofile()
        return models.PackageMap.objects.filter(checkpackage=checkprofile.custom_checkpackage).order_by("-id")


class ScanSchemeCheckProfileRuleFilterAPIView(APIView, V3GetModelMixinAPIView):
    """分析方案-规则配置-自定义规则包规则筛选项接口

    ### get
    应用场景：获取规则配置下规则filter项
    """
    permission_classes = [SchemeDefaultPermission]

    def get(self, request, *args, **kwargs):
        checkprofile = self.get_checkprofile()
        queryset = models.PackageMap.objects.filter(checkpackage=checkprofile.custom_checkpackage)
        filter_map = FilterManger.get_checkpackage_rules_filter(queryset, filters.PackageMapFilter, user=request.user)
        return Response(data=filter_map)


class ScanSchemeCheckProfileRuleBatch(generics.GenericAPIView, V3GetModelMixinAPIView):
    """分析方案-规则配置-规则批量操作，用作其他BatchAPIView基类
    """
    permission_classes = [SchemeDefaultPermission]
    serializer_class = None

    def get_and_check_batch_data(self, request):
        """校验并获取批量数据
        :return: serializer, checkpackage, tool_key
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        checkprofile = self.get_checkprofile()
        checkpackage = checkprofile.custom_checkpackage
        tool_key = CheckToolManager.get_tool_key(org=self.get_org())
        return serializer, checkpackage, tool_key


class ScanSchemeCheckProfileRuleCreateAPIView(ScanSchemeCheckProfileRuleBatch):
    """分析方案-规则配置-自定义规则包-批量添加规则接口

    ### post
    应用场景：自定义规则包批量添加规则
    ```python
    {
      "checkrules": [x], # int, 规则id
      "checktool": xx # int, 工具id，可选，如果存在checktool, 则一键添加该工具所有规则，忽略 checkrules
    }
    ```
    """
    serializer_class = serializers.CheckPackageRuleAddSerializer

    def post(self, request, *args, **kwargs):
        serializer, checkpackage, tool_key = self.get_and_check_batch_data(request)
        checktool = serializer.validated_data.get("checktool")
        checkrules = serializer.validated_data.get("checkrules")
        if checktool:
            CheckPackageManager.add_checktool_rules(checkpackage, checktool, request.user, tool_key=tool_key)
            err_message = []
            message = "已成功添加工具规则"
        else:
            err_message = CheckPackageManager.add_rules(checkpackage, checkrules, request.user, tool_key=tool_key)
            message = "已成功添加规则"
        return Response({
            "detail": message,
            "err_message": err_message
        })


class ScanSchemeCheckProfileRuleBatchUpdateAPIView(ScanSchemeCheckProfileRuleBatch):
    """分析方案-规则配置-自定义规则包-批量修改规则信息接口

    ### put
    应用场景：自定义规则包批量修改规则

    > 参数格式:
      ```python
      {
          # int, 规则包规则编号列表（采用packagemap的id，而不是checkrule的id）
          "packagemaps": [x,x,x]
          "severity":  x,          #  严重级别【1为致命，2为错误，3为警告，4为提示】
          "rule_params":  "xxx",
          "state": 1, # int, 1 生效、2屏蔽
      }
      ```
      注：对规则集下的官方规则包中的规则进行修改，实际上是反馈到自定义规则包中到规则上，
      如果自定义规则包中不存在该规则，默认会先生成该规则再更新其内容
    """
    serializer_class = serializers.CheckPackageRuleUpdateSerializer

    def put(self, request, *args, **kwargs):
        serializer, checkpackage, tool_key = self.get_and_check_batch_data(request)
        packagemaps = serializer.validated_data["packagemaps"]
        severity = serializer.validated_data["severity"]
        rule_params = serializer.validated_data["rule_params"]
        state = serializer.validated_data["state"]
        CheckPackageManager.update_pms(checkpackage, packagemaps, severity, rule_params, state,
                                       request.user, tool_key=tool_key)
        return Response(serializer.data)


class ScanSchemeCheckProfileRuleStateBatchUpdateAPIView(ScanSchemeCheckProfileRuleBatch):
    """分析方案-规则配置-自定义规则包-批量修改规则的状态接口

    ### put
    应用场景：批量修改规则包规则状态
    > 参数格式:
    ```python
    {
        # int, 规则包规则编号列表（采用packagemap的id，而不是checkrule的id）
        "packagemaps": [x,x,x]
        "state":  1          #  状态【1为生效中，2为已屏蔽】
    }
    ```
    """
    serializer_class = serializers.CheckPackageRuleStateUpdateSerializer

    def put(self, request, *args, **kwargs):
        serializer, checkpackage, tool_key = self.get_and_check_batch_data(request)
        packagemaps = serializer.validated_data["packagemaps"]
        state = serializer.validated_data["state"]
        remark = serializer.validated_data.get("remark")
        CheckPackageManager.update_pms_state(checkpackage, packagemaps, state,
                                             request.user, remark=remark, tool_key=tool_key)
        return Response(serializer.data)


class ScanSchemeCheckProfileRuleSeverityBatchUpdateAPIView(ScanSchemeCheckProfileRuleBatch):
    """分析方案-规则配置-自定义规则包-批量修改规则的严重级别接口

    ### put
    应用场景：批量修改规则包规则严重级别
    > 参数格式:
        ```python
        {
            # int, 规则包规则编号列表（采用packagemap的id，而不是checkrule的id）
            "packagemaps": [x,x,x]
            "severity":  x          #  严重级别，1为致命，2为错误，3为警告，4为提示
        }
        ```
    """
    serializer_class = serializers.CheckPackageRuleSeverityUpdateSerializer

    def put(self, request, *args, **kwargs):
        serializer, checkpackage, tool_key = self.get_and_check_batch_data(request)
        packagemaps = serializer.validated_data["packagemaps"]
        severity = serializer.validated_data["severity"]
        CheckPackageManager.update_pms_severity(checkpackage, packagemaps, severity,
                                                request.user, tool_key=tool_key)
        return Response(serializer.data)


class ScanSchemeCheckProfileRuleBatchDeleteAPIView(ScanSchemeCheckProfileRuleBatch):
    """分析方案-规则配置-自定义规则包-批量移除规则接口

    ### del
    应用场景：规则包批量删除规则
    > 参数格式:
    ```python
    {
        # int, 规则包规则编号列表（采用packagemap的id，而不是checkrule的id）
        "packagemaps": [x,x,x]
        "reason": "xxx" #  删除理由
    }
    ```
    """
    serializer_class = serializers.CheckPackageRuleDeleteSerializer

    def delete(self, request, *args, **kwargs):
        serializer, checkpackage, _ = self.get_and_check_batch_data(request)
        packagemaps = serializer.validated_data["packagemaps"]
        reason = serializer.validated_data["reason"]
        CheckPackageManager.delete_pms(checkpackage, packagemaps, reason, request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CheckPackageListAPIView(generics.ListAPIView):
    """分析方案-规则配置-全部官方规则包列表接口

    ### get
    应用场景：获取全部有效的官方规则包列表，按修改时间排序

    ```python
    # 筛选条件:
    name: str, 规则包名称, 包含
    label: str, 规则包标签名称
    language: str, 规则包语言, universal代表通用规则包
    ```
    """
    permission_classes = [SchemeDefaultPermission]
    serializer_class = serializers.ScanSchemeCheckPackageSerializer
    queryset = CheckPackageManager.filter_usable()
    filter_backends = (DjangoFilterBackend, )
    filterset_class = filters.CheckPackageFilter
    pagination_class = None


class CheckRuleListAPIView(generics.ListAPIView, V3GetModelMixinAPIView):
    """分析方案-规则配置-有权限使用规则列表接口

    ### get
    应用场景：在规则配置添加规则时，获取所有公开工具(正常运营、体验运营)、团队有权限工具且未失效的规则列表
    """
    permission_classes = [SchemeDefaultPermission]
    serializer_class = serializers.CheckRuleSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = filters.CheckRuleFilter

    def get_queryset(self):
        tool_key = CheckToolManager.get_tool_key(org=self.get_org())
        return CheckRuleManager.filter_pkg_usable(tool_keys=[tool_key])

    def get_paginated_response(self, data):
        """将分页后得到的数据进行校验，判断自定义规则包中的规则是否存在被选中的
        """
        # 获取自定义规则包的规则
        checkprofile = self.get_checkprofile()
        custom_rule_ids = models.PackageMap.objects.filter(checkpackage=checkprofile.custom_checkpackage) \
                                                   .values_list("checkrule_id", flat=True).distinct()
        new_data = []
        for rule in data:
            rule["select_state"] = models.CheckRule.SelectStateTypeEnum.UNSELECT
            if rule.get("id") in custom_rule_ids:
                rule["select_state"] = models.CheckRule.SelectStateTypeEnum.CUSTOMSELECT
            new_data.append(rule)
        return super().get_paginated_response(new_data)


class CheckRuleDetailAPIView(generics.RetrieveAPIView, V3GetModelMixinAPIView):
    """分析方案-规则配置-有权限使用的规则详情接口

    ### get
    应用场景： 获取规则详情
    """
    permission_classes = [SchemeDefaultPermission]
    serializer_class = serializers.CheckRuleSerializer
    lookup_url_kwarg = "checkrule_id"

    def get_queryset(self):
        tool_key = CheckToolManager.get_tool_key(org=self.get_org())
        return CheckRuleManager.filter_pkg_usable(tool_keys=[tool_key])


class CheckRuleDetailByNameAPIView(generics.RetrieveAPIView, V3GetModelMixinAPIView):
    """分析方案-规则配置-有权限使用的规则详情接口，根据工具、规则名称获取规则详情

    ### get
    应用场景：根据工具name和规则real_name获取规则详情

    ```python
    {
      checktool_name: '工具真实名称',
      checkrule_real_name: '规则真实名称
    }
    ```
    """
    permission_classes = [SchemeDefaultPermission]
    serializer_class = serializers.CheckRuleSerializer

    def get_object(self):
        query_params = self.request.query_params
        checktool_name = query_params.get("checktool_name")
        checkrule_real_name = query_params.get("checkrule_real_name")
        if not checktool_name or not checkrule_real_name:
            raise ParseError("checktool_name、checkrule_real_name参数必填")
        tool_key = CheckToolManager.get_tool_key(org=self.get_org())
        checkrule = CheckRuleManager.filter_pkg_usable(tool_keys=[tool_key]) \
                                    .filter(checktool__name=checktool_name, real_name=checkrule_real_name).first()
        if checkrule:
            return checkrule
        raise NotFound("没有找到该规则")
