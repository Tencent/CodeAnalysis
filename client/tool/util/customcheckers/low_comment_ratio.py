# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
检查文件的注释占比
"""


import os
import io
import logging

from util.configlib import ConfigReader
from util.textutil import CommentsManager, CodecClient, OTHER_EXT

logger = logging.getLogger(__name__)


class LowCommentRatio(object):
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
        # 支持规则参数设置
        COMMENT_RATIO = "0.1"
        REMOVE_EXT = None

        # 获取规则参数
        rule_list = params["rule_list"]
        for rule in rule_list:
            if rule["name"] != rule_name:
                continue
            if not rule["params"]:
                rule["params"] = ""
            rule_params = "[block_name]\r\n" + rule["params"]
            rule_params_dict = ConfigReader(cfg_string=rule_params).read("block_name")
            COMMENT_RATIO = rule_params_dict.get("min") if "min" in rule_params_dict else COMMENT_RATIO
            REMOVE_EXT = rule_params_dict.get("remove_ext")
            break

        COMMENT_RATIO = os.environ.get("CUSTOMFILECHECK_COMMENT_RADIO", COMMENT_RATIO)

        logger.info(f"当前文件注释率最小阈值是: {COMMENT_RATIO}")

        # 适配百分数
        if "%" in COMMENT_RATIO:
            COMMENT_RATIO = float(COMMENT_RATIO[:-1]) / 100
        else:
            COMMENT_RATIO = float(COMMENT_RATIO)
        remove_ext = list(OTHER_EXT)
        remove_ext.extend([".json", ".xml", ".yml", ".yaml", ".html", ".htm", ".sh", ".bat", ".vcproj", ".vcxproj"])
        # 支持指定过滤文件后缀，以英文逗号分割
        if REMOVE_EXT:
            remove_ext.extend(REMOVE_EXT.split(","))
        remove_ext = tuple(remove_ext)
        issues = []
        for file_path in scan_files:
            if file_path.endswith(remove_ext):
                continue
            with io.open(file_path, "rb") as fp:
                # 读取文件内容并解码为字符串
                file_text = CodecClient().decode(fp.read())
                if not file_text:
                    continue
                # 获取文件中的注释
                comments = CommentsManager(file_path, file_text).get_comments()
                # logger.debug(comments)
                comment_line = list()
                for comment in comments:
                    comment_line.extend(comment.splitlines())
                len_comment = len(comment_line)
                len_file = len(file_text.splitlines())
                ratio = len_comment / len_file
                if ratio < COMMENT_RATIO:
                    issues.append(
                        {
                            "path": file_path,
                            "line": 1,
                            "column": 1,
                            "msg": "该文件总行数为%d行, 注释行数为%d行, 注释占比为%.1f%%, 小于阈值%.1f%%, 要求注释占比大于等于阈值"
                            % (len_file, len_comment, ratio * 100, COMMENT_RATIO * 100),
                            "rule": rule_name,
                        }
                    )

        return issues


checker = LowCommentRatio

if __name__ == "__main__":
    pass
