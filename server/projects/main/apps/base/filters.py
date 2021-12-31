# -*- coding: utf-8 -*-
"""
base - filters
"""

# 第三方 import
from django_filters import rest_framework as filters


class NumberInFilter(filters.NumberFilter, filters.BaseInFilter):
    pass


class CharInFilter(filters.CharFilter, filters.BaseInFilter):
    pass
