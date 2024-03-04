# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""export资源
在djang-import-export基础上增加一个CSV资源生成器
"""

import tablib
from django.db.models.query import QuerySet


class CSVResourceGeneratorMiXin:
    """CSV资源生成器
    """

    def csv_generator_export(self, queryset=None, *args, **kwargs):
        """csv生成器导出
        """
        self.before_export(queryset, *args, **kwargs)

        if queryset is None:
            queryset = self.get_queryset()
        headers = self.get_export_headers()
        data = tablib.Dataset(headers=headers)
        # Return headers
        yield "\ufeff"  # 调整csv打开乱码问题
        yield data.csv

        if isinstance(queryset, QuerySet):
            # Iterate without the queryset cache, to avoid wasting memory when
            # exporting large datasets.
            iterable = queryset.iterator()
        else:
            iterable = queryset
        for obj in iterable:
            # Return subset of the data (one row)
            # This is a simple implementation to fix the tablib library which is missing returning the data as
            # generator
            data = tablib.Dataset()
            data.append(self.export_resource(obj))
            yield data.csv
        yield
