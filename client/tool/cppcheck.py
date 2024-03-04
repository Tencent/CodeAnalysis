# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
cppcheck 分析任务
"""

import json
import os
import re

import psutil
from task.codelintmodel import CodeLintModel
from task.scmmgr import SCMMgr
from util.envset import EnvSet
from util.exceptions import AnalyzeTaskError, ConfigError
from util.logutil import LogPrinter
from util.pathfilter import FilterPathUtil
from util.pathlib import PathMgr
from util.subprocc import SubProcController

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


class Cppcheck(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.sensitive_word_maps = {"cppcheck": "Tool", "Cppcheck": "Tool"}

    def _run_misra_addon_analyze(self, source_dir, params, files_path):
        """cppcheck执行misra规则检查
        """
        rules = params["rules"]
        work_dir = params.work_dir
        misra_rule_prefix = "misra-c2012-"
        CPPCHECK_HOME = os.environ["CPPCHECK_HOME"]
        find_all_rule_version_regex = r'Rule ([\.\d]+) [R|M|A]'
        misra_rule_file = os.path.join(
            CPPCHECK_HOME, "addons", "config", "misra_rules.txt")

        # 获取需要检查的misra规则
        misra_rules = [
            rule for rule in rules if rule.startswith(misra_rule_prefix)]
        LogPrinter.info(f"[misra_rules]: {misra_rules}")
        if not misra_rules:
            return []

        # 其余的规则留给cppcheck进行检查
        other_cppcheck_rules = list(set(rules) - set(misra_rules))
        params["rules"] = other_cppcheck_rules

        # all_rule_versions_set 所有的规则版本号
        all_rule_versions_set = set(re.findall(
            find_all_rule_version_regex, open(misra_rule_file, "r").read()))
        LogPrinter.info(
            f"[misra_rules_all_rule_versions_set]: {all_rule_versions_set}")

        # disable_rule_version_set 需要关闭的规则版本号
        disable_rule_version_set = all_rule_versions_set - \
            set([rule[len(misra_rule_prefix):] for rule in rules])
        LogPrinter.info(
            f"[misra_rules_disable_rule_version_set]: {disable_rule_version_set}")
            
        # 构造misra分析所需的配置文件
        misra_config = {
            "script": os.path.join(CPPCHECK_HOME, "addons", "misra.py"),
            "args": [
                f"--rule-text={misra_rule_file}"
            ]
        }
        disable_rule_version_str = ','.join(list(disable_rule_version_set))
        if disable_rule_version_str:
            # 兼容全部规则启用的情况 ，不再需要 suppress-rules 参数
            misra_config["args"].append(
                f"--suppress-rules {disable_rule_version_str}")
        LogPrinter.info(f"[misra_config] {misra_config}")

        # 将配置写入到 misra.json 文件中，然后使用cppcheck --addon=<json file path> 指定配置
        misra_file = os.path.join(work_dir, "misra.json")
        with open(misra_file, "w") as f:
            f.write(json.dumps(misra_config))

        # 执行cppcheck misra 分析检查命令
        cmd_args = [
            "cppcheck",
            f"--addon={misra_file}",
            "--addon-python=python3",
            '--template="{file}[CODEDOG]{line}[CODEDOG]{id}[CODEDOG]{severity}[CODEDOG]{message}"',
            '--inconclusive',
            '--file-list=%s' % files_path
        ]
        LogPrinter.info(f"[misra_cmd_args]: {cmd_args}")
        scan_misra_result_path = "cppcheck_addon_misra_result.xml"
        return_code = SubProcController(
            cmd_args,
            cwd=CPPCHECK_HOME,
            stderr_filepath=scan_misra_result_path,
            stderr_line_callback=self._error_callback,
            stdout_line_callback=self.print_log,
        ).wait()
        LogPrinter.info(f"[misra_cmd run return code: {return_code}")

        # 如果没有结果文件的写入，直接返回空列表
        if not os.path.exists(scan_misra_result_path):
            LogPrinter.info("scan_misra_result is empty ")
            return []

        # 将列表中的结果格式化标准输出
        result_list = self._format_result(
            source_dir, scan_misra_result_path, misra_rules,
            [misra_rule_prefix +
                rule_version for rule_version in list(all_rule_versions_set)]
        )
        return result_list

    def analyze(self, params):
        """执行cppcheck分析任务

        :param params: 需包含下面键值：
           'rules'： lint分析的规则列表
           'incr_scan' : 是否增量分析

        :return: return a :py:class:`IssueResponse`
        """
        source_dir = params.source_dir
        work_dir = params.work_dir
        incr_scan = params["incr_scan"]
        relpos = len(source_dir) + 1
        files_path = os.path.join(work_dir, "paths.txt")
        path_mgr = PathMgr()

        toscans = []
        want_suffix = [".cpp", ".cxx", ".cc", ".c++", ".c", ".tpp", ".txx"]
        if incr_scan:
            diffs = SCMMgr(params).get_scm_diff()
            toscans = [
                os.path.join(source_dir, diff.path).replace(os.sep, "/")
                for diff in diffs
                if diff.path.endswith(tuple(want_suffix)) and diff.state != "del"
            ]
        else:
            toscans = [path.replace(os.sep, "/") for path in PathMgr().get_dir_files(source_dir, tuple(want_suffix))]

        toscans = FilterPathUtil(params).get_include_files(toscans, relpos)

        if not toscans:
            LogPrinter.debug("To-be-scanned files is empty ")
            return []

        with open(files_path, "w", encoding="UTF-8") as f:
            f.write("\n".join(toscans))

        # 执行cppcheck misra规则分析检查
        addon_misra_result_list = self._run_misra_addon_analyze(
            source_dir, params, files_path)

        # 获取剩余的rules给cppcheck使用
        rules = params["rules"]

        id_severity_map = self._get_id_severity_map()  # 获取当前版本cppcheck的 规则名:严重级别 对应关系
        supported_rules = id_severity_map.keys()  # 获取当前版本cppcheck支持的所有规则名
        # 过滤掉当前版本cppcheck不支持的规则
        filtered_rules = [r for r in rules if r not in supported_rules]
        rules = list(set(rules) - set(filtered_rules))

        # 执行 cppcheck 工具
        scan_result_path = self._run_cppcheck(files_path, rules, id_severity_map)

        if not os.path.exists(scan_result_path):
            LogPrinter.info("result is empty ")
            cppcheck_result_list = []
        else:
            # 格式化cppcheck结果
            cppcheck_result_list = self._format_result(source_dir, scan_result_path, rules, supported_rules)

        # cppcheck + misra结果一起返回
        result_list = cppcheck_result_list + addon_misra_result_list
        return result_list

    def _get_id_severity_map(self):
        """获取cppcheck所有规则和严重级别的对应关系

        :return:
        """
        cmd_args = ["cppcheck", "--errorlist", "--xml-version=2"]
        errorlist_path = "cppcheck_errorlist.xml"
        return_code = SubProcController(
            cmd_args,
            cwd=os.environ["CPPCHECK_HOME"],
            stdout_filepath=errorlist_path,
            stderr_line_callback=self.print_log,
            env=EnvSet().get_origin_env(),
        ).wait()
        if return_code != 0:
            raise ConfigError("当前机器环境可能不支持cppcheck执行，请查阅任务日志，根据实际情况适配。")
        with open(errorlist_path, "r") as rf:
            errorlist = rf.read()

        error_root = ET.fromstring(errorlist).find("errors")
        id_severity_map = {error.get("id"): error.get("severity") for error in error_root}
        return id_severity_map

    def _get_needed_visitors(self, id_severity_map, rule_list):
        """cppcheck不能指定规则分析，只能指定规则级别，这里通过rules获取所属的规则级别"""
        assert rule_list is not None
        # cppcheck默认就是开启error规则（且无法指定enable=error),所以这里取补集
        return {id_severity_map[rule_name] for rule_name in rule_list} - {"error"}

    def _run_cppcheck(self, files_path, rules, id_severity_map):
        """
        执行cppcheck分析工具
        :param files_path:
        :param rules:
        :param id_severity_map:
        :return:
        """
        CPPCHECK_HOME = os.environ["CPPCHECK_HOME"]
        LogPrinter.info("使用 cppcheck 为 %s" % CPPCHECK_HOME)
        path_mgr = PathMgr()
        cmd_args = [
            "cppcheck",
            "--quiet",
            '--template="{file}[CODEDOG]{line}[CODEDOG]{id}[CODEDOG]{severity}[CODEDOG]{message}"',
            "--inconclusive",
        ]
        # LogPrinter.info(f'rules after filtering: {rules}')
        if not rules:
            # cmd_args.append('--enable=all')
            cmd_args.append("--enable=warning,style,information")
            cmd_args.append("-j %s" % str(psutil.cpu_count()))
        else:
            visitors = self._get_needed_visitors(id_severity_map, rules)
            if visitors:
                cmd_args.append("--enable=%s" % ",".join(visitors))
            # rules里出现unusedFunction 才不会开启并行检查
            if "unusedFunction" not in rules:
                cmd_args.append("-j %s" % psutil.cpu_count())

        # 添加自定义正则表达式规则--rule-file
        custom_rules = path_mgr.get_dir_files(os.path.join(CPPCHECK_HOME, "custom_plugins"), ".xml")
        custom_rules = ["--rule-file=" + rule for rule in custom_rules]
        cmd_args.extend(custom_rules)
        # 添加代码补丁配置cfg --library
        custom_cfgs = path_mgr.get_dir_files(os.path.join(CPPCHECK_HOME, "custom_cfg"), ".cfg")
        custom_cfgs = ["--library=" + cfg for cfg in custom_cfgs]
        cmd_args.extend(custom_cfgs)

        # 指定分析文件
        cmd_args.append("--file-list=%s" % files_path)
        scan_result_path = "cppcheck_result.xml"
        self.print_log(f"cmd: {' '.join(cmd_args)}")
        cmd_args = path_mgr.format_cmd_arg_list(cmd_args)
        SubProcController(
            cmd_args,
            cwd=CPPCHECK_HOME,
            stderr_filepath=scan_result_path,
            stderr_line_callback=self._error_callback,
            stdout_line_callback=self.print_log,
        ).wait()
        # if not os.path.exists(scan_result_path):
        #     return scan_result_path
        # try:
        #     if sys.platform == "win32":
        #         result_content = open(scan_result_path, 'r', encoding='gbk').read()
        #         open(scan_result_path, 'w', encoding='utf-8').write(result_content)
        #     with open(scan_result_path, 'r', encoding='utf-8') as rf:
        #         scan_result = rf.read()
        # except UnicodeDecodeError as e:
        #     LogPrinter.warning(e)
        #     with open(scan_result_path, 'rb')
        # if not scan_result:
        #     return scan_result_path

        # 2019-8-28 偶现因为系统编码输出到结果文件，导致解析失败的情况
        # 2022-10-14 解析结果不再使用xml格式而是逐行解析，故不需要在解析前查看该文件
        # error_msg = "/bin/sh: warning: setlocale: LC_ALL: cannot change locale (en_US.UTF-8)\n"
        # if scan_result.startswith(error_msg):
        #     scan_result = scan_result[len(error_msg):]

        # self.print_log("%s's result: \n%s" % (scan_result_path, scan_result))

        return scan_result_path

    def _error_callback(self, line):
        """

        :param line:
        :return:
        """
        if line.find("The command line is too long") != -1:
            raise AnalyzeTaskError("执行命令行过长")
        # self.print_log(line)

    def _format_result(self, source_dir, scan_result_path, rules, supported_rules):
        """格式化工具执行结果"""
        issues = []
        relpos = len(source_dir) + 1
        with open(scan_result_path, "rb") as rf:
            lines = rf.readlines()
            for line in lines:
                try:
                    line = line.decode("utf-8")
                except:
                    line = line.decode("gbk")
                error = line.split("[CODEDOG]")
                if len(error) != 5:
                    LogPrinter.info("该error信息不全或格式有误: %s" % line)
                    continue
                if "" in error:
                    LogPrinter.info("忽略error: %s" % line)
                    continue
                rule = error[2]
                if rule not in supported_rules:  # 没有指定规则时，过滤不在当前版本cppcheck支持的规则中的结果
                    LogPrinter.debug("rule not in supported_rules: %s" % rule)
                    continue
                if rule in ["missingInclude", "MissingIncludeSystem"]:
                    LogPrinter.info("unsupported rule:%s" % rule)
                    continue
                if rule not in rules:
                    continue
                # 格式为{file}[CODEDOG]{line}[CODEDOG]{id}[CODEDOG]{severity}[CODEDOG]{message}
                issue = {}
                issue["path"] = error[0][relpos:]
                issue["line"] = int(error[1])
                issue["column"] = "1"
                issue["msg"] = error[4]
                issue["rule"] = rule
                issues.append(issue)
        return issues

    def check_tool_usable(self, tool_params):
        """
        这里判断机器是否支持运行cppcheck
        1. 支持的话，便在客户机器上分析
        2. 不支持的话，就发布任务到公线机器分析
        :return:
        """
        if SubProcController(["cppcheck", "--version"], stderr_line_callback=self.print_log).wait() != 0:
            return []
        return ["analyze"]


tool = Cppcheck

if __name__ == "__main__":
    pass
