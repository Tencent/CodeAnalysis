# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - v3 api urls for checktool
"""
# 第三方
from django.urls import path, include

# 项目内
from apps.scan_conf.apis import v3 as apis

# 前缀/api/v3/orgs/<str:org_sid>/checktools/<int:checktool_id>/rules/
rule_urlpatterns = [
    path("",
         apis.CheckToolRuleListAPIView.as_view()),
    path("<int:checkrule_id>/",
         apis.CheckToolRuleDetailAPIView.as_view()),
    path("filter/",
         apis.CheckToolRuleFilterAPIView.as_view()),
    path("custom/",
         apis.CheckToolRuleCustomListAPIView.as_view()),
    path("custom/<int:checkrule_id>/",
         apis.CheckToolRuleCustomDetailAPIView.as_view()),
    path("custom/filter/",
         apis.CheckToolRuleCustomFilterAPIView.as_view()),
]

# 前缀/api/v3/orgs/<str:org_sid>/checktools/<int:checktool_id>/schemes/
scheme_urlpatterns = [
    path("",
        apis.CheckToolSchemeListAPIView.as_view()),
    path("<int:libscheme_id>/",
        apis.CheckToolSchemeDetailAPIView.as_view()),
    path("<int:libscheme_id>/libs/",
        apis.CheckToolSchemeLibListAPIView.as_view()),
    path("<int:libscheme_id>/libs/<int:libmap_id>/",
        apis.CheckToolSchemeLibDetailAPIView.as_view()),
    path("<int:libscheme_id>/libs/<int:libmap_id>/dragsort/<int:target_libmap_id>/",
        apis.CheckToolSchemeLibDragSortAPIView.as_view()),
]

# 前缀/api/v3/orgs/<str:org_sid>/checktools/
urlpatterns = [
    path("",
         apis.CheckToolListAPIView.as_view()),
    path("<int:checktool_id>/",
         apis.CheckToolDetailAPIView.as_view()),
    path("<int:checktool_id>/whitelist/",
         apis.CheckToolWhiteListAPIView.as_view()),
    path("<int:checktool_id>/whitelist/create/",
         apis.CheckToolWhiteBatchCreateAPIView.as_view()),
    path("<int:checktool_id>/whitelist/delete/",
         apis.CheckToolWhiteBatchDeleteAPIView.as_view()),
    path("<int:checktool_id>/whitelist/<int:whitelist_id>/",
         apis.CheckToolWhiteDetailAPIView.as_view()),
    path("<int:checktool_id>/status/",
         apis.CheckToolStatusAPIView.as_view()),
    path("<int:checktool_id>/rules/", include(rule_urlpatterns)),
    path("<int:checktool_id>/schemes/", include(scheme_urlpatterns)),
    # path("<int:checktool_id>/operationrecords/",
    #      apis.CheckToolOperationRecordListAPIView.as_view()),
]
