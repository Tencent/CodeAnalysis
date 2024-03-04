# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
login - v3 urls
"""
from django.urls import path

from login.apis import v3 as apis_v3

urlpatterns = [
    # 用户信息
    path("users/", apis_v3.UserListAPIView.as_view(), name="apiv3_user_list"),
    path("user/", apis_v3.TokenUserDetailAPIView.as_view(), name="apiv3_user_token_detail"),
    path("users/<uid>/", apis_v3.UserDetailAPIView.as_view(), name="apiv3_user_detail"),
    path("get_oapassword_info/", apis_v3.OAInfoAPIView.as_view(), name="apiv3_oapssword_info"),
    # 账号关联，解绑
    path("account/", apis_v3.AccountInfoAPIView.as_view(), name="apiv3_account_info"),
]
