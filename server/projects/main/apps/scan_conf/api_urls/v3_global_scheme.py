# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - v3 api urls for global scheme checkprofile
"""
# 第三方
from django.urls import path, include

# 项目内
from apps.scan_conf.apis import v3 as apis

# 前缀/api/v3/orgs/<str:org_sid>/schemes/<int:scheme_id>/checkprofile/checkpackages/
# 官方规则包的相关接口
checkpackage_urlpatterns = [
    path("",
         apis.ScanSchemePackageListAPIView.as_view()),
    path("<int:checkpackage_id>/",
         apis.ScanSchemePackageDetailAPIView.as_view()),
    path("<int:checkpackage_id>/rules/",
         apis.ScanSchemePackageRuleListAPIView.as_view()),
    path("<int:checkpackage_id>/rules/filter/",
         apis.ScanSchemePackageRuleFilterAPIView.as_view()),
]

# 前缀/api/v3/orgs/<str:org_sid>/schemes/<int:scheme_id>/checkprofile/
# 自定义规则包的相关操作接口
checkprofile_urlpatterns = [
    path("",
         apis.ScanSchemeCheckProfileDetailAPIView.as_view()),
    path("rules/",
         apis.ScanSchemeCheckProfileRuleListAPIView.as_view()),
    path("rules/filter/",
         apis.ScanSchemeCheckProfileRuleFilterAPIView.as_view()),
    path("rules/create/",
         apis.ScanSchemeCheckProfileRuleCreateAPIView.as_view()),
    path("rules/modify/",
         apis.ScanSchemeCheckProfileRuleBatchUpdateAPIView.as_view()),
    path("rules/modifystate/",
         apis.ScanSchemeCheckProfileRuleStateBatchUpdateAPIView.as_view()),
    path("rules/modifyseverity/",
         apis.ScanSchemeCheckProfileRuleSeverityBatchUpdateAPIView.as_view()),
    path("rules/delete/",
         apis.ScanSchemeCheckProfileRuleBatchDeleteAPIView.as_view()),
]

# 前缀/api/v3/orgs/<str:org_sid>/schemes/<int:scheme_id>/
urlpatterns = [
    path("allcheckpackages/",
         apis.CheckPackageListAPIView.as_view()),
    path("allrules/",
         apis.CheckRuleListAPIView.as_view()),
    path("allrules/<int:checkrule_id>/",
         apis.CheckRuleDetailAPIView.as_view()),
    path("allrules/byname/",
         apis.CheckRuleDetailByNameAPIView.as_view()),
    path("checkprofile/", include(checkprofile_urlpatterns)),
    path("checkprofile/checkpackages/", include(checkpackage_urlpatterns)),
]
