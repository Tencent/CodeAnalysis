# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

'''
增量项目资源查看器
基于平台工具组的文件服务器实现云端信息存储
'''

from task.basic.localcache import LocalCache
from task.basic.remotecache import RemoteCache
from util.exceptions import SourceMgrError


class IncSourceMgr(object):

    def __init__(self, scm_url, src_type='normal'):
        '''
        增量资源管理类
        :param scm_url: 项目的url地址
        :param src_type: 增量资源类型
        '''
        self.scm_url = scm_url
        self.type = src_type
        self.local_cache = LocalCache(scm_url, src_type)
        self.remote_cache = RemoteCache(scm_url, src_type)
        pass

    def inc_src_exist(self):
        '''
        判断增量资源是否存在
        :return:
        '''
        if self.local_cache.exist_cache:
            return True
        if self.remote_cache.exist_cache:
            return True
        return False

    def get_src_info(self):
        '''
        获取增量资源信息
        :return:
        '''
        if self.local_cache.exist_cache:
            return self.local_cache.path_dict
        if self.remote_cache.exist_cache:
            return self.remote_cache.path_dict
        raise SourceMgrError('the IncSourceMgr error %s : %s' % (self.scm_url, self.type))

    def insert_src_info(self, path_dict):
        '''
        插入增量资源
        :param path_dict:
        :return:
        '''
        if path_dict:
            self.remote_cache.insert_cache(path_dict)
            self.local_cache.insert_cache(path_dict)

