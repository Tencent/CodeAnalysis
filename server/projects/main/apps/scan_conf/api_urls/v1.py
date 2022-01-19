# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - v1 api urls
"""
# 第三方
from django.urls import path

# 项目内 import
from apps.scan_conf.apis import base
from apps.scan_conf.apis import v1

# 前缀：api/conf/
urlpatterns = [
    path("languages/", 
         base.LanguageListAPIView.as_view()),
    path("toolnames/", 
         v1.CheckToolDisplayNameListAPIView.as_view()),
    path("checkpackages/<int:package_id>/checkruleids/", 
         v1.CheckPackageRuleIDListAPIView.as_view()),
]
