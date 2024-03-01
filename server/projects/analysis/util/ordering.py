# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""自定义ordering
"""
import logging

from rest_framework.filters import OrderingFilter


logger = logging.getLogger(__name__)


class OrderingWithPKFilter(OrderingFilter):

    def get_ordering(self, request, queryset, view):
        params = request.query_params.get(self.ordering_param)
        if params:
            fields = [param.strip() for param in params.split(',')]
            if queryset.model._meta.pk.attname in fields or "-%s" % queryset.model._meta.pk.attname in fields:
                fields = fields
            else:
                fields.append(queryset.model._meta.pk.attname)
            ordering = self.remove_invalid_fields(queryset, fields, view, request)
            if ordering:
                return ordering

        return self.get_default_ordering(view)
