# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
CopyrightChecker: 检查开源项目中每个代码文件中是否包含Copyroght信息
"""


import re
import logging

logger = logging.getLogger(__name__)


class CopyrightChecker(object):
    """
    检查开源项目中每个代码文件中是否包含Copyroght信息
    """

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
        issues = []
        for file_path in scan_files:
            if file_path.endswith((".md", ".json", ".yml", ".xml")):
                continue
            if self.check_copyright(file_path):
                continue
            issues.append({"path": file_path, "line": 1, "column": 1, "msg": "该文件没有发现copyright信息", "rule": rule_name})
        return issues

    def check_copyright(self, filename):
        """
        检查文件头部是否有Copyright信息
        :param filename: 文件路径
        :return:
        """
        try:
            lines = open(filename, "r").readlines()
            for line in range(0, min(len(lines), 31)):
                if re.search(r"Copyright.*\s*All\s*rights\s*reserved", lines[line], re.I):
                    return True
            else:
                return False
        except UnicodeDecodeError:
            logger.error(filename + " 编码异常！")
            return True


checker = CopyrightChecker

if __name__ == "__main__":
    pass
