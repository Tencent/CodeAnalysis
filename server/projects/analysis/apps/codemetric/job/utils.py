# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codemetric - job utils
"""
import itertools
import json
import logging
import os

from util.filemanager import unzip
from util.fileserver import file_server

logger = logging.getLogger(__name__)


def get_file(file_url):
    """下载文件并加载到内存
    :param file_url: str，文件url
    """
    return file_server.get_file(file_url)


def download_and_load_json_file(file_url):
    """下载并加载json数据
    """
    try:
        return json.loads(get_file(file_url))
    except (json.JSONDecodeError, TypeError) as err:
        logger.error("load json file failed: %s, file url: %s" % (err, file_url))
        raise


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


def yield_issue_from_files(dir_path, files):
    for path in files:
        path = os.path.join(dir_path, path)
        with open(path, 'r') as f:
            while True:
                context = f.readline().strip()
                if not context:
                    break
                yield json.loads(context)


def batch_delete_with_queryset(queryset, permanent=False):
    """批量删除
    先筛选pk字段，再分片删除
    """
    pk_field = queryset.model._meta.pk.attname
    pks = list(queryset.values_list(pk_field, flat=True))
    for pk_chunk in grouper(pks, 1000):
        fields = {"%s__in" % pk_field: pk_chunk}
        if permanent is True:
            queryset.model.everything.filter(**fields).delete(permanent=permanent)
        else:
            queryset.model.objects.filter(**fields).delete()
