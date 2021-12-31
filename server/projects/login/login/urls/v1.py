# -*- coding: utf-8 -*-
"""
login - v1 urls
"""
# 第三方
from django.urls import path

# 项目内
from login.apis import v1 as apis_v1

urlpatterns = [
    path("users/", apis_v1.UserListApiView.as_view(), name="apiv1_user_list"),
    path("users/<str:uid>/", apis_v1.UserDetailApiView.as_view(), name="apiv1_user_detail"),
]
