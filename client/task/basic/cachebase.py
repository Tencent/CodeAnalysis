# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""增量缓存基类"""


class CacheBase(object):

    def __init__(self, scm_url, src_type='normal'):
        self.path_dict = None  # 本地缓存项目的source_dir
        self.exist_cache = False  # 指定项目是否存在缓存数据
        self.cache_data = None  # 缓存数据结构
        self.scm_url = scm_url
        self.src_type = src_type

    def insert_cache(self, path_dict):
        '''
        插入缓存路径集
        :param path_dict: 格式自拟，反正是工具自己用
        :return:
        '''
        raise NotImplementedError()
