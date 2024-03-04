# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codelint - job utils
"""

import itertools
import json
import logging

from util.filemanager import unzip
from util.fileserver import file_server
from util.retrylib import RetryDecor

logger = logging.getLogger(__name__)


def get_file(file_url):
    """下载文件并加载到内存
    :param file_url: str，文件url
    """
    return file_server.get_file(file_url)


@RetryDecor()
def download_and_load_json_file(file_url):
    """下载并加载json数据
    """
    try:
        return json.loads(get_file(file_url))
    except (json.JSONDecodeError, TypeError) as err:
        logger.error("load json file failed: %s, file url: %s" % (err, file_url))
        raise


@RetryDecor()
def download_and_unzip_file(file_url):
    """下载并解压文件
    :param file_url: str，文件url
    :return: str, list 路径和文件列表
    """
    return unzip(file_server.download_file(file_url))


def grouper(iterable, size):
    """分批次生成列表
    """
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, size))
        if not chunk:
            return
        yield chunk


def queryset_to_dict(queryset, f1_choices, f2_choices):
    """
    queryset(list): (f1, f2, count)
    return: {choices(f1,f1):{f2:count}}
    """
    result = {}
    for f1, f2, count in queryset:
        f1 = f1_choices.get(f1, f1)
        f2 = f2_choices.get(f2, f2)
        f1_value = result.get(f1, {})
        f1_value.update({f2: count})
        result.update({f1: f1_value})
    return result


def batch_delete_with_queryset(queryset, permanent=True):
    """批量删除
    先筛选pk字段，再分片删除
    """
    pk_field = queryset.model._meta.pk.attname
    pks = list(queryset.values_list(pk_field, flat=True))
    for pk_chunk in grouper(pks, 1000):
        fields = {"%s__in" % pk_field: pk_chunk}
        queryset.model.objects.filter(**fields).delete(permanent=permanent)
