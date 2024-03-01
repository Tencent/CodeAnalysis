# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - v1 api urls
"""
# 第三方
from django.urls import path

# 项目内
from apps.scan_conf.apis import base as base_apis
from apps.scan_conf.apis import v1 as apis

# 前缀：api/conf/
urlpatterns = [
    path("languages/",
         base_apis.LanguageListAPIView.as_view(),
         name="apiv1_language_list"),
    path("toolnames/",
         apis.CheckToolDisplayNameListAPIView.as_view(),
         name="apiv1_checktool_name_list"),
    path("checkpackages/<int:package_id>/checkruleids/",
         apis.CheckPackageRuleIDListAPIView.as_view(),
         name="apiv1_checkpackage_ruleid_list"),
    path("checkrules/ruletypemap/",
         apis.CheckRuleTypeMapAPIView.as_view(),
         name="apiv1_checkrules_ruletype_map"),
]
