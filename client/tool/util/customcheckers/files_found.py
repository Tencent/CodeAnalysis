# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
检查项目中是否包含不该存在的的文件或目录
默认检查的文件路径: *.a, *.framework
支持项目通过 CHECKED_PATH 环境变量设置: 使用相对路径,多个路径用英文逗号(,)分隔,路径格式遵循python fnmatch语法
"""


import os
import logging

from util.pathlib import PathMgr
from util.pathfilter import WildcardPathFilter
from util.textutil import StringMgr

logger = logging.getLogger(__name__)

class FilesFound(object):
    """
    检查项目中是否包含不该存在的的文件或目录
    比如：检查开源项目下是否有未开源的.a,.framework文件
    """
    # 默认检查路径,路径格式遵循python fnmatch语法
    Default_Checked_Paths = ["*.a", "*.framework"]

    def run(self, params, scan_files, rule_name):
        """
        :param params: 任务参数
        :param scan_files: 需要扫描的文件列表
        :param rule_name: 规则名,通过外部传递
        :return: [
                   {'path':...,
                    'line':...,
                    'column':...,
                    'msg':...,
                    'rule':...
                   },
                   ...
                ]
        """


        # 从环境变量获取用户设置的文件路径
        # 环境变量格式: 相对路径,多个路径用英文逗号(,)分隔,路径格式遵循python fnmatch语法
        CHECKED_PATH = os.environ.get("CHECKED_PATH", None)
        if CHECKED_PATH:
            checked_paths = StringMgr.str_to_list(CHECKED_PATH)
        else:
            checked_paths = self.Default_Checked_Paths

        logger.info("在代码目录下扫描以下文件: %s" % checked_paths)

        # 获取所有文件路径
        pathmgr = PathMgr()
        source_dir = pathmgr.format_path(params['source_dir'])
        rel_pos = len(source_dir) + 1
        file_paths = pathmgr.get_dir_files(source_dir)

        issues = []
        filter_mgr = WildcardPathFilter(path_include=None, path_exclude=checked_paths)
        for path in file_paths:
            rel_path = path[rel_pos:]
            if filter_mgr.should_filter_path(rel_path):
                issues.append({
                    'path': path,
                    'line': 0,
                    'column': 0,
                    'msg': "发现需要检查的文件,请确认",
                    'rule': rule_name
            })
        return issues


checker = FilesFound

if __name__ == '__main__':
    pass
