# -*- coding: utf-8 -*-
"""
base - api urls
"""

from django.urls import path

from apps.base import apis


# 前缀：/
urlpatterns = [
    path("", apis.BaseApiView.as_view(), name="index_view"),
]
