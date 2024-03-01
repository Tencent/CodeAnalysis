#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
Stylelint: css style static analyzer
"""

import os
import sys
import json
import codecs
from shutil import copyfile

from task.scmmgr import SCMMgr
from task.codelintmodel import CodeLintModel
from util.exceptions import AnalyzeTaskError
from util.configlib import ConfigReader
from util.subprocc import SubProcController
from util.pathfilter import FilterPathUtil
from util.logutil import LogPrinter
from util.textutil import StringMgr


class Stylelint(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.sensitive_word_maps = {"Stylelint": "Tool", "stylelint": "Tool"}

    def analyze(self, params):
        """

        :param params:
        :return:
        """
        source_dir = params.source_dir
        work_dir = os.getcwd()
        rules = params.rules
        envs = os.environ
        incr_scan = params["incr_scan"]
        path_exclude = params.path_filters.get("exclusion", [])
        error_output = os.path.join(work_dir, "styleliint-output.txt")

        if os.environ.get("STYLELINT_MAX_OLD_SPACE_SIZE", None):
            scan_cmd = ["node", "--max-old-space-size=" + os.environ.get("STYLELINT_MAX_OLD_SPACE_SIZE")]
            if sys.platform == "win32":
                scan_cmd.append(
                    os.path.join(os.environ.get("NODE_HOME"), "node_modules", "stylelint", "bin", "stylelint.js")
                )
            else:
                scan_cmd.append(
                    os.path.join(os.environ.get("NODE_HOME"), "lib", "node_modules", "stylelint", "bin", "stylelint.js")
                )
        else:
            scan_cmd = ["stylelint"]
        scan_cmd.extend(["--allow-empty-input", "--ignore-disables"])

        config_file = self.config(params)
        if config_file:
            scan_cmd.extend(["--config", config_file])

        if "STYLELINT_SYNTAX" in envs:
            # 可以设置非标准的CSS语法结构：Specify a non-standard syntax. Options: "scss", "sass", "less", "sugarss"
            scan_cmd.extend(["--syntax", envs.get("STYLELINT_SYNTAX")])

        if "STYLELINT_CUSTOM_SYNTAX" in envs:
            # Module name or path to a JS file exporting a PostCSS-compatible syntax.
            scan_cmd.extend(["--custom-syntax", envs.get("STYLELINT_CUSTOM_SYNTAX")])

        # 如果是增量扫描，则获得增量代码文件进行扫描
        # 如果是全量扫描，则扫描整个代码目录
        toscans = []
        want_suffix = [".css", ".less", ".scss", "sass", ".sss"]
        global_files = '"**/*.{css, less, scss, sass, sss}"'
        if incr_scan:
            diffs = SCMMgr(params).get_scm_diff()
            toscans = [
                os.path.join(source_dir, diff.path).replace(os.sep, "/")
                for diff in diffs
                if diff.path.endswith(tuple(want_suffix)) and diff.state != "del"
            ]
            relpos = len(source_dir) + 1
            toscans = FilterPathUtil(params).get_include_files(toscans, relpos)

            # windows下增量文件路径总长度超长，改为扫描整个soucedir，否则会执行异常
            # 因为 windows 下执行subprocess.Popen方法且shell=False的情况下，命令长度限制为32768字节
            # 这里文件路径长度限制为32500，因为前面还要预留cppcheck命令的长度
            if sys.platform == "win32" and len(" ".join(toscans)) > 32500:
                toscans = [global_files]
        else:
            toscans = [global_files]

        if not toscans:
            LogPrinter.debug("To-be-scanned files is empty ")
            return []

        scan_cmd.extend(toscans)

        # exclusion
        # 由于node-v12.16.3下stylelint --ignore-pattern在扫描对象前面时候就会执行异常
        exclu_path_arr = []
        if path_exclude:
            for tmp_path in path_exclude:
                exclu_path_arr.append("--ignore-pattern")
                exclu_path_arr.append('"' + tmp_path + '"')
        scan_cmd.extend(exclu_path_arr)

        self.print_log("scan_cmd: %s" % " ".join(scan_cmd))
        SubProcController(
            scan_cmd, stdout_filepath=error_output, cwd=source_dir, stderr_line_callback=self._cmd_callback
        ).wait()

        issues = []
        self._result_handle(issues, error_output, rules)
        LogPrinter.debug(issues)
        return issues

    def _cmd_callback(self, line):
        """
        命令执行log回调
        :param line: log
        :return:
        """
        self.print_log(line)
        if line.find("JavaScript heap out of memory") != -1:
            raise AnalyzeTaskError("Js内存溢出，请设置环境变量STYLELINT_MAX_OLD_SPACE_SIZE")
        elif line.find("RangeError: Invalid string length") != -1:
            raise AnalyzeTaskError("项目太大，扫描结果超过Js的buffer.constants.MAX_STRING_LENGTH最大字符串限制，请设置扫描路径过滤过滤无用文件")

    def config(self, params):
        """
        设置stylelint的配置文件
        :param params:
        :return:
        """
        work_dir = params.work_dir
        envs = os.environ
        rules = params.rules
        config_path = None

        stylelint_config = envs.get("STYLELINT_CONFIG", None)
        stylelint_config_type = envs.get("STYLELINT_CONFIG_TYPE", None)

        if stylelint_config:
            LogPrinter.info("复用项目中指定的配置文件进行扫描")
            config_path = stylelint_config
            return config_path

        # default custom tencent
        if stylelint_config_type not in ("default", "custom", None):
            LogPrinter.info("使用" + stylelint_config_type + "风格配置文件进行扫描")
            config_file = "%s_stylelintrc.json" % (stylelint_config_type)
            config_path = os.path.join(work_dir, config_file)
            copyfile(os.path.join(envs.get("NODE_HOME"), config_file), config_path)
            return config_path

        if stylelint_config_type == "custom":
            self.print_log("发现项目中含有stylelint配置文件，复用该配置文件进行扫描")
            return config_path

        if stylelint_config_type == "default":
            pass

        LogPrinter.info("使用默认的AlloyTeam风格配置文件进行扫描")
        config_path = os.path.join(work_dir, "stylelintrc.json")
        copyfile(os.path.join(envs.get("NODE_HOME"), "stylelintrc.json"), config_path)
        # 设置配置文件
        self._set_stylelint_rule(params, config_path, rules)

        return config_path

    def _set_stylelint_rule(self, params, config_file, rules):
        """
        给配置文件设置规则
        :param params:
        :param config_file:
        :param rules:
        :return:
        """
        rule_list = params["rule_list"]
        with open(config_file, "r") as f:
            configContent = f.read()
            configContentJson = json.loads(configContent)
            configRules = configContentJson["rules"]

        if rules:
            for rule in configRules:
                if rule not in rules:
                    configRules[rule] = None

        # enable rules
        if rule_list:
            for rule in rule_list:
                rule_name = rule["name"]
                if rule_name not in configRules:
                    configRules[rule_name] = True
                # 2020-12-14 支持规则参数设置
                if not rule["params"]:
                    continue
                param = rule["params"]
                try:
                    # 1. 直接拷贝在配置文件Json中的设置
                    configRules[rule_name] = json.loads(param)
                except json.JSONDecodeError as e:
                    # 2. 使用key-value方式
                    # 数组的非字典元素，使用options指定
                    # demo: options=always
                    if "[stylelint]" in param:
                        rule_params = param
                    else:
                        rule_params = "[stylelint]\r\n" + param
                    rule_params_dict = ConfigReader(cfg_string=rule_params).read("stylelint")

                    if rule_params_dict.get("options"):
                        option = StringMgr.trans_type(rule_params_dict["options"])
                        rule_params = option
                        configRules[rule_name] = rule_params

        with codecs.open(config_file, "w", encoding="utf-8") as f:
            json.dump(configContentJson, f, ensure_ascii=False)

    def _result_handle(self, issues, error_output, rules):
        """
        处理扫描结果
        :param issues:
        :param error_output:
        :param rules:
        :return:
        """
        if not os.path.exists(error_output) or os.stat(error_output).st_size == 0:
            LogPrinter.info("result is empty")
            return
        error_file = open(error_output, encoding="utf-8")
        for error in error_file.readlines():
            error = error[0:-1]  # 去掉末尾换行符
            tmp = error.split()
            LogPrinter.info(error)
            LogPrinter.info(tmp)
            path = ""
            # 文件路径 防止文件有空格不再使用旧的区分方式
            if error.endswith(".css") or error.endswith(".scss"):
                path = error
            elif len(tmp) > 1:
                location = tmp[0].split(":")
                line = int(location[0])
                column = int(location[1])
                msg = " ".join(tmp[2:-1])
                rule = tmp[-1]
                if rule not in rules:
                    continue
                if not path:
                    continue
                issues.append({"path": path, "rule": rule, "msg": msg, "line": line, "column": column})


tool = Stylelint

if __name__ == "__main__":
    pass
