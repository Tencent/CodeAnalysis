# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
util - file manager
文件相关的操作方法
"""
import os
import logging
import zipfile

logger = logging.getLogger(__name__)


def unzip(file_path, to_dir_path=None):
    """
    把文件解压到指定目录，否则解压到当前目录
    :return: to_dir_path, file_list
    """
    if not to_dir_path:
        to_dir_path = os.path.dirname(file_path)
    if not os.path.isdir(to_dir_path):
        os.makedirs(to_dir_path)
    try:
        zip_file = zipfile.ZipFile(file_path)
        file_list = zip_file.namelist()
        for names in file_list:
            zip_file.extract(names, to_dir_path)
        return to_dir_path, file_list
    except Exception as err:
        logger.error("unzip file exception: %s, file stat: %s" % (err, str(os.stat(file_path))))
        raise
