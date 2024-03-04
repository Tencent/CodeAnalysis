# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""远程增量缓存管理类"""

from task.basic.cachebase import CacheBase
from node.app import settings


class RemoteCache(CacheBase):

    file_server = settings.FILE_SERVER

    def __init__(self, scm_url, src_type='normal'):
        '''
        初始化远程缓存数据管理类
        :param scm_url: 项目的url，作为项目区分的唯一主键
        self.exist_cache 该字段比较重要必须要进行处理
        '''
        CacheBase.__init__(self, scm_url, src_type)

    def insert_cache(self, path_dict):
        pass
