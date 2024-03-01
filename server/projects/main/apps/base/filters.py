# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
base - filters
"""

# 第三方 import
from django_filters import rest_framework as filters


class NumberInFilter(filters.NumberFilter, filters.BaseInFilter):
    pass


class CharInFilter(filters.CharFilter, filters.BaseInFilter):
    pass
