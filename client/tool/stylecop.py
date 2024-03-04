#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
StyleCop:  style static analyzer
"""

import os
import sys

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from shutil import copyfile

from task.scmmgr import SCMMgr
from util.pathlib import PathMgr
from util.pathfilter import FilterPathUtil
from task.codelintmodel import CodeLintModel
from util.subprocc import SubProcController
from util.exceptions import AnalyzeTaskError
from util.logutil import LogPrinter


class StyleCop(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.sensitive_word_maps = {
            "StyleCop": "Tool",
            "stylecop": "Tool",
            "StyleCopCLI": "Tool",
            "stylecopcli": "Tool"
        }

    def analyze(self, params):
        """

        :param params:
        :return:
        """
        source_dir = params.source_dir
        work_dir = params.work_dir
        enabled_rules = params.rules
        LogPrinter.info("开启规则 %s " % len(enabled_rules))

        envs = os.environ
        error_output = os.path.join(work_dir, "stylecop_output.xml")
        stylecop_home = envs.get("STYLECOP_HOME")
        stylecop_config = "STYLECOP_CONFIG"
        # stylecop_proj = "STYLECOP_PROJ"
        # stylecop_sln = "STYLECOP_SLN"
        filter_mgr = FilterPathUtil(params)
        pos = len(source_dir) + 1

        # 指定配置文件
        if stylecop_config in envs:
            settingfile = os.path.join(source_dir, envs.get(stylecop_config))
        else:
            settingfile = os.path.join(work_dir, "stylecop_config.xml")
            copyfile(os.path.join(stylecop_home, "stylecop_config.xml"), settingfile)
            self.set_config_file(settingfile, enabled_rules)

        scan_cmd = [
            "mono",
            os.path.join(stylecop_home, "StyleCopCLI.exe"),
            "--settingsFile",
            settingfile,
            "--recursiveSearch",
            "--outputFile",
            error_output,
        ]
        # mac和linux下根目录下有cs文件时候，工具执行异常，这里做下适配
        toscans = self.get_target_files(params)
        if not toscans:
            LogPrinter.info("没有待扫描文件")
            return list()
        scan_cmd.append("--sourceFiles")
        # scan_cmd.extend(toscans)
        # 由于命令行长度限制，需要对被扫描文件分批次进行扫描
        # 获取命令行最长限制
        CMD_ARG_MAX = PathMgr().get_cmd_arg_max()
        LogPrinter.info("命令行长度限制：%d" % CMD_ARG_MAX)
        cmd_args_list = PathMgr().get_cmd_args_list(scan_cmd, toscans, CMD_ARG_MAX)

        issues = list()
        for i in range(len(cmd_args_list)):
            self.print_log("cmd: %s" % " ".join(cmd_args_list[i]))
            LogPrinter.info("cmd_len: %d" % len(" ".join(cmd_args_list[i])))
            sp = SubProcController(
                cmd_args_list[i],
                cwd=source_dir,
                stdout_line_callback=self.print_log,
                stderr_line_callback=self.print_log
            )
            sp.wait()

            # 执行成功，返回值不一定为0，可能为2
            LogPrinter.error("命令执行返回码为: %d" % sp.returncode)
            err_log = self.__get_stdout_log(os.path.join(work_dir, "subprocc_stdout.log"))
            if err_log.find("No source code files to analyze.") != -1:
                LogPrinter.error("代码库中没有C#代码文件，扫描结果为空。")
                return []

            # 处理扫描结果
            raw_warning = ET.ElementTree(file=error_output)
            # issues = list()
            for vio in raw_warning.iter(tag="Violation"):
                path = vio.attrib.get("Source")
                # 工具解析异常，建议到winodws下执行
                """
                <Violation LineNumber="1" RuleNamespace="StyleCop.CoreParser" Rule="ExceptionOccurred" RuleId="SA0001">
                An exception occurred while parsing the file: System.ArgumentException, The string must not be empty 
                    or null Parameter name: location.
                </Violation>
                """
                if (
                    path is None
                    and vio.attrib.get("Rule") == "ExceptionOccurred"
                    and vio.attrib.get("RuleId") == "SA0001"
                ):
                    raise AnalyzeTaskError(f"工具解析异常, 建议切换为windows机器下执行: {vio.attrib} msg: {vio.text}")

                path = path[pos:]
                if filter_mgr.should_filter_path(path):
                    continue
                line = int(vio.attrib.get("LineNumber"))
                # analyzer= vio.attrib.get("RuleNamespace")
                # rule_id= vio.attrib.get("RuleId")
                namespace = vio.attrib.get("RuleNamespace")
                rule_name = vio.attrib.get("Rule")
                
                rule = "%s/%s" % (namespace, rule_name)
                # 项目使用自己的规则配置文件，这里当项目指定了配置文件时候不做规则过滤
                if stylecop_config not in envs and rule not in enabled_rules:
                    continue
                msg = vio.text
                issues.append({"path": path, "rule": rule, "msg": msg, "line": line})
            LogPrinter.debug(issues)

        return issues

    def get_target_files(self, params):
        """
        获取目标待扫描的文件
        :param params:
        :return:
        """
        source_dir = params.source_dir
        incr_scan = params.incr_scan
        pos = len(source_dir) + 1

        want_suffix = [".cs"]
        if incr_scan:
            diffs = SCMMgr(params).get_scm_diff()
            toscans = [
                diff.path.replace(os.sep, "/")
                for diff in diffs
                if diff.path.endswith(tuple(want_suffix)) and diff.state != "del"
            ]
        else:
            toscans = [
                path.replace(os.sep, "/")[pos:] for path in PathMgr().get_dir_files(source_dir, tuple(want_suffix))
            ]
        toscans = [os.path.join(source_dir, path) for path in toscans]
        toscans = FilterPathUtil(params).get_include_files(toscans, pos)
        # 不能直接使用相对路径，mac和linux下需要在前面加个./
        toscans = [f'"./{path[pos:]}"' for path in toscans]
        LogPrinter.info(f"待扫描文件数: {len(toscans)}")
        return toscans

    def get_rule_tree(self, rules):
        """

        :param rules:
        :return:
        """
        tree = dict()
        for rule in rules:
            info = rule.split("/")
            namespace = info[0]
            name = info[1]
            if namespace in tree:
                tree[namespace].append(name)
            else:
                tree[namespace] = [name]
        return tree

    def set_config_file(self, settingfile, enabled_rules):
        """

        :param settingfile:
        :param enabled_rules:
        :return:
        """
        LogPrinter.info("setting is %s" % settingfile)
        config = ET.ElementTree(file=settingfile)
        rule_tree = self.get_rule_tree(enabled_rules)
        # 这里逻辑是遍历规则配置，选用了就设为True, 修改配置文件应为tool_config_files目录下的，而不是工具根目录下
        for analyzer in config.iter(tag="Analyzer"):
            analyzer_id = analyzer.attrib.get("AnalyzerId")
            if analyzer_id not in rule_tree:
                continue
            for rule in analyzer.iter(tag="Rule"):
                rule_name = rule.attrib.get("Name")
                if rule_name not in rule_tree[analyzer_id]:
                    continue
                # Rule/RuleSettings/BooleanProperty
                rule[0][0].text = "True"
        config.write(settingfile)

    def __get_stdout_log(self, stdout_file):
        """
        获取执行stdout的log
        :param stdout_file:
        :return: stdout中的log
        """
        if sys.platform == "win32":
            f = open(stdout_file, encoding="gbk")
        else:
            f = open(stdout_file, encoding="utf-8")
        log = f.read()
        f.close()
        return log

    def check_tool_usable(self, tool_params):
        """
        这里判断机器是否支持运行stylecop
        1. 支持的话，便在客户机器上扫描
        2. 不支持的话，就发布任务到公线机器扫描
        :return:
        """
        if SubProcController(["mono", "--version"]).wait() != 0:
            return []
        return ["analyze"]


tool = StyleCop

if __name__ == "__main__":
    pass
