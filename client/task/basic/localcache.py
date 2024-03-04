# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""本地增量数据管理类"""

import json
import os

from task.basic.cachebase import CacheBase
from node.app import settings
from util.logutil import LogPrinter


class LocalCache(CacheBase):
    """本地增量扫描缓存数据管理类"""

    cache_file = settings.CACHE_FILE  # 缓存文本路径
    exist_file = False

    def __init__(self, scm_url, src_type='normal'):
        '''
        初始化本地缓存数据管理类
        :param scm_url: 项目的url，作为项目区分的唯一主键
        '''
        CacheBase.__init__(self, scm_url, src_type)
        if os.path.exists(self.cache_file):
            self.exist_file = True
            with open(self.cache_file, 'r') as cache_file:
                cache_text = cache_file.read()
                try:
                    self.cache_data = json.loads(cache_text)
                except Exception as err:
                    LogPrinter.warning(f"load {self.cache_file} error: {str(err)}")
                    LogPrinter.warning(f"cache file text: {cache_text}")
                    self.cache_data = []
                for issue in self.cache_data:
                    if issue['scm_url'] == self.scm_url and issue['src_type'] == self.src_type:
                        self.path_dict = issue['path_dict']
                        self.exist_cache = True
                        for path in self.path_dict.values():
                            if not os.path.exists(path):
                                self.exist_cache = False
                                break

    def insert_cache(self, path_dict):
        """
        向缓存文本中插入新的项目缓存数据
        :param path_dict: 不同工具所需要的路径数量与内容不同，因此这里用json来存，运行数组和字典
        path_dict的方式不在这里限制，使用处需要判断工具需要保存哪些增量数据
        """
        if not self.exist_file:
            self.cache_data = []
        if self.exist_cache:
            for item in self.cache_data:
                if item['scm_url'] == self.scm_url:
                    item['path_dict'] = path_dict
                    item['src_type'] = self.src_type
                    break
        else:
            self.cache_data.append(
                {
                    'scm_url': self.scm_url,
                    'path_dict': path_dict,
                    'src_type': self.src_type
                }
            )
        # cache中存在部分已经删除的缓存信息，需要进行清理
        temp_set = []
        for item in self.cache_data:
            is_exists = True
            for path in item['path_dict'].values():
                if not os.path.exists(path):
                    is_exists = False
                    break
            if is_exists:
                temp_set.append(item)
        self.cache_data = temp_set

        text = json.dumps(self.cache_data, indent=2)
        with open(self.cache_file, 'w') as cache_file:
            cache_file.write(text)
            cache_file.close()
