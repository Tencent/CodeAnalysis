# -*- coding: utf-8 -*-
"""基础接口
"""
from django.urls import path

from . import apis

# 前缀：/
urlpatterns = [
    path('', apis.BaseApiView.as_view(), name="index_view"),
]
