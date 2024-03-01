# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
检查文件的换行符，需要统一为Windows下的CRLF换行符\r\n，否则便报出问题
"""


import re
import os
import logging

logger = logging.getLogger(__name__)


class NewlineChecker(object):
    def run(self, params, scan_files, rule_name):
        """

        :param params:
        :param scan_files:
        :param rule_name:
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
        # 获取NEWLINE_SETTING环境变量, 判断项目中使用统一的换行符，默认是\n
        newline = os.environ.get("CUSTOMSCAN_NEWLINE_SETTING", "\n")
        if newline == "win" or newline == "\r\n":
            # 也可以"\\r\\n"
            newline = r"\r\n"
        elif newline == "unix" or newline == "linux" or newline == "\n":
            newline = r"\n"
        elif newline == "mac" or newline == "\r":
            newline = r"\r"

        issues = []
        for file_path in scan_files:
            issues.extend(self.__newline_scan(file_path, rule_name, newline))

        return issues

    def __newline_scan(self, file_path, rule_name, newline=r"\n"):
        """
        判断换行符是否为统一的newline，默认为CRLF，\r\n
        windows下
        \r表示回车，光标移动到左边界
        \n表示换行，光标移动到下一行
        :param file_path:
        :param rule_name:
        :return:
        """
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return []

        # 依据换行符的不同进行不同的正则匹配
        if newline == r"\r\n":
            not_newline_fun = self.__not_crlf
        elif newline == r"\n":
            not_newline_fun = self.__not_lf
        else:
            not_newline_fun = self.__not_cr

        issues = []
        try:
            with open(file_path, "r", newline="") as f:
                line_no = 0
                for line in f.readlines():
                    line_no += 1
                    # 或者判断line[-1]和line[-2]
                    if not_newline_fun(line):
                        # print(repr(line))
                        issues.append(
                            {
                                "path": file_path,
                                "line": line_no,
                                "column": 1,
                                "msg": "发现不规范的换行符，请统一使用" + newline + "格式换行符！",
                                "rule": rule_name,
                            }
                        )
                        break
        except UnicodeDecodeError:
            logger.error(file_path + " 编码异常！")
        return issues

    def __not_crlf(self, line):
        """
        匹配行末换行符不是CRLF的情况
        1. 先判断不是\r\n结尾
        2. 判断是否是\n结尾，是的话，则当前换行符为\n
        3. 判断一行是否含有\r，此时readlines()会将整个文件当成一行
        :param line:
        :return:
        """
        return not re.search(r"\r\n$", line) and re.search(r"\r$|\n$", line)

    def __not_lf(self, line):
        """
        匹配行末换行符不是LF的情况
        :param line:
        :return:
        """
        return re.search(r"\r\n$|\r$", line)

    def __not_cr(self, line):
        """
        匹配行末换行符不是CR的情况
        :param line:
        :return:
        """
        return re.search(r"\r\n$|\n$", line)


checker = NewlineChecker

if __name__ == "__main__":
    pass
