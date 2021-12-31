# -*- coding: utf-8 -*-
"""
v2 api 接口url定义，v2系列接口均供前端页面调用
"""

# 第三方 import
from django.urls import path

# 项目内 import
from apps.authen.apis import v2

# 前缀/api/v2/authen/
urlpatterns = [
    path("allusers/", v2.UserListApiView.as_view(), name="apiv2_all_users"),
    path("allusers/<str:username>/", v2.UserDetailApiView.as_view(), name="apiv2_all_user_detail"),
]
