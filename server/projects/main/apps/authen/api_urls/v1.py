# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
v1 接口定义，供节点端/ 外界调用

URL前缀：/api/authen/
"""
# 第三方 import
from django.urls import path

# 项目内 import
from apps.authen.apis import v1, v3

# 前缀/api/authen/
urlpatterns = [
    path("urlauth/", v1.ProxyServerAuthenticationAPIView.as_view(), name="apiv1_authen_urlauth"),
    path("scmallaccounts/", v3.ScmAllAcountListApiView.as_view(), name="apiv1_all_scm_accounts"),
]
