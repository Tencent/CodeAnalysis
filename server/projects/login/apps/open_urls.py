#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================
"""
Login - root urls
"""
from django.urls import include, path

urlpatterns = [
    path('api/v1/login/', include('login.urls.v1')),
    path('api/v3/login/', include('login.urls.v3')),
]
