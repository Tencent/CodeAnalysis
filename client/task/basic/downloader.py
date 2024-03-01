# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
从文件服务器下载
"""

import os
import logging
import tempfile

from node.app import settings
from util.zipmgr import Zip
from util.exceptions import TransferModuleError
from util.pathlib import PathMgr
from util.api.fileserver import RetryFileServer

logger = logging.getLogger(__name__)


class Downloader(object):
    @staticmethod
    def file_server_download(path_dict):
        '''
        文件服务器下载
        :param path_dict: { '文件服务器上的文件名': '拉取下来后存放的位置' }
        :return:
        '''
        for file_name in path_dict.keys():
            temp_zip_file = tempfile.mktemp(prefix='zip_', dir=settings.DATA_DIR, suffix='.zip')
            file_server = RetryFileServer(retry_times=2).get_server()
            file_server.download_file(f"sourcedir/{file_name}", temp_zip_file)
            if not os.path.exists(temp_zip_file):
                raise TransferModuleError('文件服务器中拉取文件失败...')
            Zip().decompress(temp_zip_file, os.path.join(settings.DATA_DIR, path_dict[file_name]))
            logger.info('decompress done: %s' % os.path.join(settings.DATA_DIR, path_dict[file_name]))
            PathMgr().rmpath(temp_zip_file)
        return True


if __name__ == "__main__":
    pass
