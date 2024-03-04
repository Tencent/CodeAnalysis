# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
apps.base.apimixins 基础接口类
"""

import logging

from django.http import HttpResponse
from django.http import StreamingHttpResponse

logger = logging.getLogger(__name__)


def attachment_response(export_data, filename='download.xls', content_type='application/vnd.ms-excel', stream=False):
    """附件响应

    :param export_data: dict，导出的数据
    :param filename: str，导出的文件名
    :param content_type: str，导出的响应类型
    :param stream: boolean，是否采用stream类型
    :return: HttpResponse
    """
    try:
        if stream:
            response = StreamingHttpResponse(export_data, content_type=content_type)
        else:
            response = HttpResponse(export_data, content_type=content_type)
    except TypeError:
        response = HttpResponse(export_data, mimetype=content_type)
    response['Content-Disposition'] = 'attachment; filename={}'.format(filename)
    return response


class ExportMixin(object):
    """数据导出类
    """

    def get(self, request, format='xlsx', filename='codedog_download', empty=False, **kwargs):
        """导出数据
        """
        queryset = None
        if request.query_params.get("export") == "csv":
            format = "csv"
        if not empty:
            queryset = self.filter_queryset(self.get_queryset())
        filename = "%s.%s" % (self.get_export_filename() or filename, format)
        logger.info("export_filename: %s" % filename)

        resourse = self.resource_class()
        if format == "csv":
            export_data = resourse.csv_generator_export(queryset)
            return attachment_response(export_data, filename=filename, content_type="text/csv", stream=True)
        else:
            export_data = resourse.export(queryset)
            return attachment_response(getattr(export_data, format), filename=filename)

    def get_export_filename(self):
        """定义导出文件名
        :return str, 文件名
        """
        return ""
