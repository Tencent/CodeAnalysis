#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
检查项目中行数过长的函数
"""


import os
import logging

from tool.lizard import tool as Lizard
from util.configlib import ConfigReader

logger = logging.getLogger(__name__)


class FunctionTooLong(object):
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
        # 默认函数长度阈值
        default_func_lines = 80
        # 获取规则参数
        rule_list = params["rule_list"]
        for rule in rule_list:
            if rule["name"] != rule_name:
                continue
            if not rule["params"]:
                rule["params"] = ""
            rule_params = "[block_name]\r\n" + rule["params"]
            rule_params_dict = ConfigReader(cfg_string=rule_params).read("block_name")
            default_func_lines = int(rule_params_dict.get("max")) if "max" in rule_params_dict else default_func_lines
            break

        tool = Lizard(params)
        # 获取最大行数
        default_func_lines = (
            int(os.environ.get("CUSTOMSCAN_FUNCLINES"))
            if os.environ.get("CUSTOMSCAN_FUNCLINES")
            else default_func_lines
        )
        logger.info("当前函数长度阈值：%d" % default_func_lines)

        # 分为函数提取工具和lizard两个工具分别使用的语言列表
        scan_languages = params["scan_languages"]
        # 设置csv字段长度限制为尽可能最大
        tool.set_csv_field_size_limit()

        issues = list()
        total_func_cnt = 0

        func_detect_langs = []
        other_langs = [lang for lang in scan_languages if lang not in func_detect_langs]

        # Lizard工具执行阶段
        # logger.info(f"other_langs: {other_langs}")
        ccn_outputs = tool.ccn_scan(
            params, min_ccn=1, scan_languages=other_langs, force_incr=True, is_metric=False
        )

        for row in tool.get_all_ccn(params, ccn_outputs):
            (
                code_line_num,
                ccn,
                token,
                func_param_num,
                line_num,
                path,
                func_name,
                long_name,
                start_line_no,
                end_line_no,
            ) = row
            if func_name in tool.EXCLUSION_FUNC:
                continue

            total_func_cnt += 1
            span_lines = int(code_line_num) if int(code_line_num) > 0 else int(line_num)
            if span_lines <= default_func_lines:
                continue
            issues.append(
                {
                    "path": path,
                    "line": start_line_no,
                    "end_line": end_line_no,
                    "column": 0,
                    "msg": '函数"{}"行数超标({}/{})'.format(func_name, span_lines, default_func_lines),
                    "rule": rule_name,
                }
            )

        incr_scan = params["incr_scan"]
        if not incr_scan:
            if "summary" not in params:
                params["summary"] = dict()
            params["summary"]["funclength"] = {
                "total": len(issues),
                "rate": len(issues) / total_func_cnt if total_func_cnt != 0 else 0,
            }

        return issues
       
    def is_test_function(self, function_name):
        """判断是否为测试函数
        """
        if function_name.lower().startswith("test_"):
            return True
        elif function_name.lower().endswith("_test"):
            return True
        return False


checker = FunctionTooLong

if __name__ == "__main__":
    pass
