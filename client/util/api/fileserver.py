# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

""" 文件服务器接口
"""


import logging
import hashlib
import os
import ssl

from urllib.parse import urljoin
from util import wrapper
from node.app import settings
from util.api.httpclient import HttpClient
from urllib.request import urlopen

logger = logging.getLogger(__name__)


class FlieHash(object):
    @staticmethod
    def get_md5(file_path):
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(4096)
                if not data:
                    break
                md5.update(data)
        return md5.hexdigest()

    @staticmethod
    def get_sha256(file_path):
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(4096)
                if not data:
                    break
                sha256.update(data)
        return sha256.hexdigest()


class FileServer(object):
    def __init__(self, server_url=None, headers=None):
        """
        构造函数
        :return:
        """
        if server_url:
            self._server_url = server_url
            self._headers = headers if headers else {}
        else:
            # 优先从环境变量读取文件服务器url和token，没有再使用默认值
            self._server_url = os.getenv("FILE_SERVER_URL", settings.FILE_SERVER['URL'])
            file_server_token = os.getenv("FILE_SERVER_TOKEN", settings.FILE_SERVER['TOKEN'])
            self._headers = {'Authorization': 'Token %s' % file_server_token}

        self._proxies = None

    def modify_save_time(self, rel_dir, days):
        """
        修改文件服务器的保存时间
        :param rel_dir: 修改的目录相对路径
        :param days: 修改保存时间天数
        :return:
        """
        data = {"retention": days}
        file_url = urljoin(self._server_url, rel_dir)
        HttpClient(self._server_url, rel_dir, headers=self._headers, data=data, proxies=self._proxies).put()
        logger.info('成功修改目录(%s)保存时间为 %s 天.' % (rel_dir, days))
        return file_url

    def __upload_data(self, data, rel_url, headers):
        """
        上传数据到文件服务器
        :param data: 要上传的数据, 可以是 Dictionary, bytes, or file-like object
        :param rel_url: 上传到服务器的相对url
        :return: 上传到服务器后的完整url, 如果上传失败, 返回 None
        """
        file_url = urljoin(self._server_url, rel_url)
        HttpClient(self._server_url, rel_url, headers=headers, data=data, proxies=self._proxies).put()
        return file_url

    def upload_file(self, filepath, rel_url):
        """
        上传文件到文件服务器
        :param filepath: 要上传的文件路径
        :param rel_url: 上传到服务器的相对url
        :return: 上传到服务器后的完整url, 如果上传失败, 返回 None
        """
        with open(filepath, 'rb') as fp:
            headers = {
                "Content-SHA256": FlieHash.get_sha256(filepath),
                "Content-MD5": FlieHash.get_md5(filepath)
            }
            headers.update(self._headers)
            return self.__upload_data(fp, rel_url, headers)

    def load_data(self, rel_url):
        """

        :param rel_url:
        :return:
        """
        rsp = HttpClient(self._server_url, rel_url, headers=self._headers, proxies=self._proxies).get()
        return rsp.read()

    def download_file(self, rel_url, filepath):
        """
        从文件服务器下载文件到指定地址
        :param rel_url: 需要下载的文件的相对url
        :param filepath: 下载后的文件路径
        :return: 下载成功,返回filepath;否则返回None
        """
        data = self.load_data(rel_url)
        with open(filepath, 'wb') as wf:
            wf.write(data)
        return filepath

    def download_big_file(self, rel_url, filepath):
        """大文件下载"""
        context = ssl._create_unverified_context()
        download_url = urljoin(self._server_url, rel_url)
        resp = urlopen(download_url, context=context)
        chunk_size = 16 * 1024
        with open(filepath, 'wb') as wf:
            while True:
                trunk = resp.read(chunk_size)
                if not trunk:
                    break
                wf.write(trunk)
        return filepath


class RetryFileServer(object):
    def __init__(self, retry_times=-1):
        """
        构造函数
        :param retry_times: 重试次数,默认-1,即一直重试直到成功
        :return:
        """
        self._retry_times = retry_times

    def retry_on_error(self, error, method_name):
        """
        失败重试函数
        :param error:
        :param method_name:
        :return:
        """
        return

    def get_server(self, server_url=None):
        """
        获取一个server实例
        :return:
        """
        file_server = FileServer(server_url=server_url)
        return wrapper.Retry(server=file_server, on_error=self.retry_on_error, total=self._retry_times)
