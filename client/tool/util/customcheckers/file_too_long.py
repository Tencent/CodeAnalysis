# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
检查项目中行数过长的文件
"""


import os
import logging

from util.configlib import ConfigReader
from util.textutil import EncodingErrorLevel
from tool.util.language_maps import CODEDOG_LANGUAGE_MAPS


logger = logging.getLogger(__name__)


class FileTooLong(object):
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
        # 默认文件长度阈值
        default_file_lines = 800
        # 默认扫描勾选的语言对应的文件后缀
        scan_languages = params.get("scan_languages", [])
        default_exts = list()
        for lang in scan_languages:
            default_exts.extend(CODEDOG_LANGUAGE_MAPS.get(lang))

        file_lines = default_file_lines
        exts = default_exts
        # 获取规则参数
        rule_list = params["rule_list"]
        for rule in rule_list:
            if rule["name"] != rule_name:
                continue
            if not rule["params"]:
                rule["params"] = ""
            rule_params = "[block_name]\r\n" + rule["params"]
            rule_params_dict = ConfigReader(cfg_string=rule_params).read("block_name")
            file_lines = int(rule_params_dict.get("max", default_file_lines))
            exts = rule_params_dict.get("only_exts", ",".join(default_exts)).split(",")
            add_exts = rule_params_dict.get("add_exts")
            if add_exts:
                exts.extend(add_exts.split(","))
            break

        file_lines = int(os.environ.get("CUSTOMFILESCAN_FILELINES", file_lines))
        logger.info("当前文件长度阈值：%d" % file_lines)
        logger.info(f"待扫描文件后缀: {','.join(exts)}")

        issues = []
        for path in scan_files:
            if not path.endswith(tuple(exts)):
                continue
            logger.info("正在处理文件: %s" % path)
            # 处理编码问题
            try:
                with open(path, "r", encoding="UTF-8") as f:
                    lines = f.readlines()
            except UnicodeDecodeError as e:
                with open(path, "r", encoding="GBK", errors=EncodingErrorLevel.Surrogateescape) as f:
                    lines = f.readlines()
            if len(lines) <= file_lines:
                continue
            issues.append(
                {
                    "path": path,
                    "line": 0,
                    "column": 0,
                    "msg": "行数超标({}/{})".format(len(lines), file_lines),
                    "rule": rule_name,
                }
            )

        # 计算项目级数据指标
        # 目前只在全量扫描时候计算
        incr_scan = params["incr_scan"]
        if not incr_scan:
            if "summary" not in params:
                params["summary"] = dict()
            params["summary"]["filelength"] = {
                "total": len(issues),
                "rate": len(issues) / len(scan_files) if len(scan_files) != 0 else 0,
            }

        return issues


checker = FileTooLong

if __name__ == "__main__":
    pass
