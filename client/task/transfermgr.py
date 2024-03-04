# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
中间文件传输
"""

import os
import tempfile
import random
import string
import logging

from task.basic.downloader import Downloader
from node.app import settings
from util.zipmgr import Zip
from util.exceptions import TransferModuleError
from util.api.fileserver import RetryFileServer
from util.pathlib import PathMgr

logger = logging.getLogger(__name__)

DATA_BASE = settings.DATA_DIR


class TransferMgr(object):
    def upload_file(self, path_dict):
        '''
        上传需要传递的资源文件
        :param path_dict:{
            'params_key_name'（params中的字段名）: 绝对路径
        }
        :return: 传输中间数据文件 transfer_info
        '''
        path_list = []
        for param_name in path_dict.keys():
            path_list.append(
                {
                    'params_key_name': param_name,
                    'rel_path': os.path.relpath(path_dict[param_name], DATA_BASE) # 此处要想一想，是有必要这样
                }
            )

        for item in path_list:
            file_path = os.path.join(DATA_BASE, item['rel_path'])
            tmp_zip_file = tempfile.mktemp(prefix='zip_', dir=DATA_BASE, suffix='.zip')
            Zip().compress(file_path, tmp_zip_file)

            # 获取一个八位的随机码作为文件名，防止重名
            file_name = ''.join(random.sample(string.ascii_letters + string.digits, 8))
            file_server = RetryFileServer(retry_times=2).get_server()
            file_server.upload_file(tmp_zip_file, f"sourcedir/{file_name}")
            PathMgr().rmpath(tmp_zip_file)
            item['download_name'] = file_name
        return {
            'isP2P': False,
            'path_list': path_list
        }

    def download_file(self, transfer_info):
        '''
        下载资源文件
        '''
        logger.info('download file: 开始执行中间文件下载。。。')
        logger.info('download file: 传输模式为文件服务器')
        name_list = [path_dict['download_name'] for path_dict in transfer_info['path_list']]
        path_dict = {}
        for item in transfer_info['path_list']:
            path_dict[item['download_name']] = item['rel_path']
        re = Downloader.file_server_download(path_dict=path_dict)
        if re:
            logger.info('download file: 传输完成')
            return True
        logger.info('download file: 传输失败')
        raise TransferModuleError('传输模块，执行文件服务器拉取失败，请检查！')


if __name__ == "__main__":
    pass
