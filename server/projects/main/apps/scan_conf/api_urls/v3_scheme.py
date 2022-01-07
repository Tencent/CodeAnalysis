# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - v3 api urls for scheme
"""
# 第三方
from django.urls import path, include

# 项目内
from apps.scan_conf.apis import v3

# 前缀/api/v3/orgs/<str:org_sid>/teams/<str:team_name>/repo/<repo_id>/schemes/<scheme_id>/checkprofile/checkpackages/
# 官方规则包的相关接口
checkpackage_urlpatterns = [
    path("",
         v3.ScanSchemePackageListAPIView.as_view()),
    path("<int:checkpackage_id>/",
         v3.ScanSchemePackageDetailAPIView.as_view()),
    path("<int:checkpackage_id>/rules/",
         v3.ScanSchemePackageRuleListAPIView.as_view()),
    path("<int:checkpackage_id>/rules/filter/",
         v3.ScanSchemePackageRuleFilterAPIView.as_view()),
]

# 前缀/api/v3/orgs/<str:org_sid>/teams/<str:team_name>/repo/<int:repo_id>/schemes/<int:scheme_id>/checkprofile/
# 自定义规则包的相关操作接口
checkprofile_urlpatterns = [
    path("",
         v3.ScanSchemeCheckProfileDetailAPIView.as_view()),
    path("rules/",
         v3.ScanSchemeCheckProfileRuleListAPIView.as_view()),
    path("rules/filter/",
         v3.ScanSchemeCheckProfileRuleFilterAPIView.as_view()),
    path("rules/create/",
         v3.ScanSchemeCheckProfileRuleCreateAPIView.as_view()),
    path("rules/modify/",
         v3.ScanSchemeCheckProfilRuleBatchUpdateAPIView.as_view()),
    path("rules/modifystate/",
         v3.ScanSchemeCheckProfilRuleStateBatchUpdateAPIView.as_view()),
    path("rules/modifyseverity/",
         v3.ScanSchemeCheckProfilRuleSeverityBatchUpdateAPIView.as_view()),
    path("rules/delete/",
         v3.ScanSchemeCheckProfilRuleBatchDeleteAPIView.as_view()),
]

# 前缀/api/v3/orgs/<str:org_sid>/teams/<str:team_name>/repo/<int:repo_id>/schemes/<int:scheme_id>/
urlpatterns = [
    path("allcheckpackages/",
         v3.CheckPackageListApiView.as_view()),
    path("allrules/",
         v3.CheckRuleListApiView.as_view()),
    path("allrules/<int:checkrule_id>/",
         v3.CheckRuleDetailApiView.as_view()),
    path("checkprofile/", include(checkprofile_urlpatterns)),
    path("checkprofile/checkpackages/", include(checkpackage_urlpatterns)),
]
