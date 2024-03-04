# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
swiftlint 扫描任务
"""


import json
import os
import sys
import yaml

from task.codelintmodel import CodeLintModel
from task.scmmgr import SCMMgr
from tool.util.xcodeswitch import XcodeSwitch
from util.envset import EnvSet
from util.exceptions import AnalyzeTaskError
from util.pathlib import PathMgr
from util.pathfilter import FilterPathUtil
from util.subprocc import SubProcController
from util.logutil import LogPrinter

# from util.codestandard import TencentCodeStandard 后续代码规范使用

logger = LogPrinter


class Swiftlint(CodeLintModel):
    """
    Swift lint工具
    """

    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.sensitive_word_maps = {"Swiftlint": "Tool", "swiftlint": "Tool", "SwiftLint": "Tool"}
        pass

    def analyze(self, params):
        """
        分析函数
        :param params: 需要的资源 1.项目地址 2.工作地址 3.分析函数
        :return:
        """

        # 选择xcode 10.2以上版本
        if sys.platform == "darwin":
            XcodeSwitch.set_xcodebuild_version()
        source_dir = params["source_dir"]
        self.relpos = len(source_dir) + 1
        work_dir = os.getcwd()
        rules = params["rules"]
        rule_list = params["rule_list"]
        logger.info(source_dir)
        logger.info(work_dir)
        incr_scan = params["incr_scan"]
        nested = bool(os.environ.get("USE_NESTED")) if os.environ.get("USE_NESTED") else False
        logger.info("nested: %s" % nested)
        path_exclude = params["path_filters"].get("exclusion", [])
        path_include = params["path_filters"].get("inclusion", [])
        logger.info("扫描文件路径为: %s" % path_include if path_include else source_dir)
        logger.info("扫描屏蔽路径为: %s" % path_exclude)
        # 获取swiftlint扫描路径
        want_suffix = [".swift"]
        # 增量扫描
        if incr_scan:
            diffs = SCMMgr(params).get_scm_diff()
            toscans = [
                diff.path.replace(os.sep, "/")
                for diff in diffs
                if diff.path.endswith(tuple(want_suffix)) and diff.state != "del"
            ]
        else:
            toscans = [
                path.replace(os.sep, "/")[self.relpos :]
                for path in PathMgr().get_dir_files(source_dir, tuple(want_suffix))
            ]
        toscans = [os.path.join(source_dir, path) for path in toscans]
        toscans = FilterPathUtil(params).get_include_files(toscans, self.relpos)
        logger.info("扫描文件为: %s" % toscans)
        self._setting_swiftlint_yml(work_dir, toscans, rules, nested, rule_list)
        cmd_args = ["swiftlint"]
        error_output = os.path.join(work_dir, "Tool_error.json")
        self.print_log("cmd: %s" % " ".join(cmd_args))
        self.print_log("开始SwiftLint扫描")
        sp = SubProcController(
            command=cmd_args,
            cwd=work_dir,
            stdout_filepath=error_output,
            stdout_line_callback=self.print_log,
            stderr_line_callback=self.stderr_callback,
            env=EnvSet().get_origin_env(),
        )
        sp.wait()
        logger.info(sp.returncode)
        if not os.path.exists(error_output):
            logger.info("Tool_result.json is empty")
            return list()
        with open(error_output, "r") as f:
            fc = f.read()
            lintResult = json.loads(fc)
            issues = self._format_issue(lintResult)
        return issues

    def _format_issue(self, lintResult):
        """
        用于格式化swiftlint输出结果
        :param lintResult: swiftlint输出结果
        :return issues: 格式化后的issues
        """
        issues = []
        for i in lintResult:
            issues.append(
                {
                    "column": i["character"],
                    "line": i["line"],
                    "msg": i["reason"],
                    "rule": i["rule_id"],
                    "path": i["file"][self.relpos :],
                    "refs": [],
                }
            )
        return issues

    def _setting_swiftlint_yml(self, work_dir, toscans, rules, nested: bool, rule_list):
        """
        用于配置swiftlint的yml配置文件
        :param work_dir: 执行路径
        :param toscan: 要扫描的所有文件
        :param rules: 扫描规则
        :param nested: 是否使用项目自置yml
        # TODO: 后续考虑规则参数等配置
        :return :
        """
        filepath = os.path.join(work_dir, ".swiftlint.yml")

        rules = list(set(rules))  # 规则去重不然可能导致扫描失败
        rule_params = self._setting_rule_param(rule_list)
        with open(filepath, "w") as f:
            config = {
                "whitelist_rules": rules,
                "included": toscans,
                "reporter": "json",
                # 设置使用代码库自己的 .swiftlint.yml文件
                "use_nested_configs": nested,
            }
            config.update(rule_params)
            yaml.dump(config, f, indent=2)

    def _setting_rule_param(self, rule_list):
        """
        解析规则的参数
        :param rule_list: 规则详细信息
        :return ruleParams: 各参数配置信息
        """
        ruleParams = {}
        for rule in rule_list:
            if rule.get("params") != "":
                try:
                    ruleParam = json.loads(rule.get("params"))
                except json.decoder.JSONDecodeError:
                    logger.error("规则%s参数,请使用Json格式" % rule["display_name"])
                    raise AnalyzeTaskError("规则参数解析错误")
                ruleParams[rule["name"]] = ruleParam
        return ruleParams

    def stderr_callback(self, line):
        """
        报错回调处理
        :param line:
        :return:
        """
        self.print_log(line)
        if line.find("fatal error: Loading sourcekitd.framework/Versions/A/sourcekitd failed") != -1:
            logger.error("请选择10.2以上版本xcode,codedog机器支持10.0，10.1，10.3，11.3版本xcode")
            raise AnalyzeTaskError("请选择更高版本xcode")


tool = Swiftlint

if __name__ == "__main__":
    pass
