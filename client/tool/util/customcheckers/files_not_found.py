# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
检查项目中是否包含必备的文件或目录
"""


import os
import logging

logger = logging.getLogger(__name__)


class FilesNotFound(object):
    """
    检查项目中是否包含必备的文件或目录
    比如：检查开源项目下必备文件readme.md
    """

    required_files = ["readme.md", "contributing.md", "license.txt", "license"]

    def get_dir_files(self, root_dir):
        """
        在指定的目录下,递归获取所有文件
        :param root_dir:
        :return: list, 文件路径列表，相对路径
        """
        files = list()
        pos = len(root_dir) + 1
        # cwd: 遍历到的当前目录，此处是绝对路径
        # dirs: 当前目录下的所有目录名
        # filenames: 当前目录下的所有文件名
        for cwd, dirs, filenames in os.walk(root_dir):
            # files.extend([os.path.join(cwd[pos:], dir) for dir in dirs])
            files.extend([os.path.join(cwd[pos:], filename) for filename in filenames])
        return files

    def run(self, params, scan_files, rule_name):
        """
        :param params: 任务参数
        :param scan_files: 需要分析的文件列表
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
        source_dir = params["source_dir"].replace(os.sep, "/").rstrip("\\/")

        required_files = self.required_files
        # 补充式的，逗号分隔，基于sourcedir的相对路径
        ADD_FILES = os.environ.get("CUSTOMFILECHECK_ADD_FILES", None)
        if ADD_FILES:
            for file in ADD_FILES.replace("\\", "/").split(","):
                if file in [""] or file in required_files:
                    continue
                required_files.append(file)
        # 覆盖式的
        ONLY_FILES = os.environ.get("CUSTOMFILECHECK_ONLY_FILES", None)
        if ONLY_FILES:
            required_files = list()
            for file in ONLY_FILES.replace("\\", "/").split(","):
                if file in [""] or file in required_files:
                    continue
                required_files.append(file)

        # 获取项目根目录的文件
        files = self.get_dir_files(source_dir)
        # 不区分大小写，统一匹配小写
        files = [f.lower() for f in files]
        issues = []
        for file in required_files:
            if file in files:
                continue
            issues.append(
                {
                    "path": os.path.join(source_dir, file),
                    "line": 1,
                    "column": 1,
                    "msg": "项目中没有找到必备文件：%s" % file,
                    "rule": rule_name,
                }
            )
        return issues


checker = FilesNotFound

if __name__ == "__main__":
    pass
