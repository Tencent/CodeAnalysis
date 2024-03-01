#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
ESLint: A fully pluggable tool for identifying and reporting on patterns in JavaScript.
"""

import json
import os
import shlex
import re
import sys
import codecs
from shutil import copyfile

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from node.app import settings
from task.scmmgr import SCMMgr
from util.pathlib import PathMgr
from util.pathfilter import FilterPathUtil
from task.codelintmodel import CodeLintModel
from util.configlib import ConfigReader
from util.subprocc import SubProcController
from util.logutil import LogPrinter
from util.textutil import StringMgr
from util.tooldisplay import ToolDisplay
from util.exceptions import ConfigError


class Eslint(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.sensitive_word_maps = {"eslint": "Tool", "Eslint": "Tool", "node": "tool", "Node": "tool"}

    def print_log(self, message):
        """
        将日志中的敏感词替换掉，再打印日志
        :param message:
        :return:
        """
        if "rules Loading rule" not in message and "Configuration was determined" not in message:
            ToolDisplay.print_log(self.sensitive, self.sensitive_word_maps, message)

    def analyze(self, params):
        """
        扫描分析源码
        :param params:
        :return:
        """
        envs = os.environ
        work_dir = os.getcwd()

        # 表示Eslint扫描Js以及React框架
        eslint_type = "JAVASCRIPT"
        eslint_ext = ".js,.jsx"
        if "ESLINT_%s_EXT" % eslint_type in envs:
            eslint_ext = envs.get("ESLINT_%s_EXT" % eslint_type)
        # 扫描html内嵌js
        if envs.get("ESLINT_EXT_HTML"):
            eslint_ext = eslint_ext + ",.html"

        error_output = os.path.join(work_dir, "%s_eslint_result.xml" % eslint_type.lower())

        config_path, rule_filte_flag = self.config(params, eslint_type, True)

        self.scan(params, config_path, error_output, eslint_ext)

        return self.data_handle(params, error_output, rule_filte_flag)

    def config(self, params, eslint_type, use_custom_prority=False):
        """
        设置eslint的配置文件
        :param params:
        :param eslint_type:
        :param use_custom_prority: REACT默认使用代码库下的配置文件，VUE和TYPESCRIPT默认使用CodeDog的配置文件
        :return:
        """
        source_dir = params.source_dir
        work_dir = params.work_dir
        envs = os.environ

        # 不使用CodeDog维护的配置文件时候，不对扫描结果规则过滤
        rule_filte_flag = False

        # 设置配置文件
        config_path = None
        # 兼容之前的ESLINT_CONFIG和ESLINT_CONFIG_TYPE
        eslint_config = envs.get("ESLINT_CONFIG", None)
        eslint_type_config = envs.get("ESLINT_%s_CONFIG" % eslint_type, None)
        eslint_config_type = envs.get("ESLINT_CONFIG_TYPE", None)
        eslint_type_config_type = envs.get("ESLINT_%s_CONFIG_TYPE" % eslint_type, None)

        if eslint_type == "JAVASCRIPT" and eslint_config:
            eslint_type_config = eslint_config

        if eslint_type_config:
            LogPrinter.info("复用项目中指定的配置文件进行扫描")
            config_path = eslint_type_config
            return config_path, rule_filte_flag

        if eslint_type == "JAVASCRIPT" and eslint_config_type:
            eslint_type_config_type = eslint_config_type

        # default custom google
        if eslint_type_config_type not in ("default", "custom", None):
            LogPrinter.info("使用" + eslint_type_config_type + "风格配置文件进行扫描")
            config_file = "%s_%s_eslintrc.json" % (eslint_type_config_type, eslint_type.lower())
            config_path = os.path.join(work_dir, config_file)
            copyfile(os.path.join(envs.get("NODE_HOME"), config_file), config_path)

            # 支持设置配置文件
            self._set_eslint_config(params, config_path, eslint_type, set_rule_flag=False)
            return config_path, rule_filte_flag

        if eslint_type_config_type == "custom":
            self.print_log("发现项目中含有eslint配置文件，复用该配置文件进行扫描")
            return config_path, rule_filte_flag

        if eslint_type_config_type == "default":
            pass
        elif use_custom_prority and self._find_eslintrc(source_dir):
            self.print_log("发现项目中含有eslint配置文件，复用该配置文件进行扫描")
            return config_path, rule_filte_flag

        LogPrinter.info("使用默认的AlloyTeam风格配置文件进行扫描")
        config_path = os.path.join(work_dir, os.path.join(work_dir, "%s_eslintrc.json" % eslint_type.lower()))
        copyfile(os.path.join(envs.get("NODE_HOME"), "%s_eslintrc.json" % eslint_type.lower()), config_path)
        # 设置配置
        self._set_eslint_config(params, config_path, eslint_type)
        rule_filte_flag = True

        return config_path, rule_filte_flag

    def _set_eslint_config(self, params, config_file, eslint_type, set_rule_flag=True):
        """
        给配置文件设置规则，将之置为warn级别
        注意：
        1. react扫描，即babel-eslint解析时候，no-unused-vars规则可能会解析失败，导致eslint执行失败
        :param params:
        :param config_file:
        :param eslint_type:
        :param set_rule_flag: True时候，设置配置文件的规则，对应not rule_filte_flag
        :return:
        """
        source_dir = params.source_dir
        work_dir = params.work_dir
        rule_list = params["rule_list"]
        envs = os.environ

        # 判断是否为ts,如果是配置tsconfig参数
        parserOptions = {}
        if "typescript" == eslint_type.lower():
            tsconfig = self._find_tsconfig(source_dir)
            LogPrinter.info("读取tsconfig文件配置: {}".format(tsconfig))
            parserOptions["project"] = tsconfig if tsconfig else self._set_tsconfig_file(work_dir)
            # 不存在配置文件 指定绝对路径空tsconfig.json文件

        # 设置eslint的global配置，以分号分隔，比如：ESLINT_GLOBALS=_:readonly;jtest:readonly
        # 对于每个全局变量键，将对应的值设置为 "writable" 以允许重写变量，或 "readonly" 不允许重写变量, "off" 禁用全局变量
        # 由于历史原因，布尔值 false 和字符串值 "readable" 等价于 "readonly"。类似地，布尔值 true 和字符串值 "writeable" 等价于 "writable"
        eslint_globals = envs.get("ESLINT_%s_GLOBALS" % eslint_type, "")

        # 设置eslint的环境，一个环境定义了一组预定义的全局变量。以分号分隔
        eslint_env = envs.get("ESLINT_%s_ENV" % eslint_type, "")

        # Eslint配置文件，添加在现有维护的配置文件中
        eslint_options = os.path.join(source_dir, envs.get("ESLINT_%s_OPTIONS" % eslint_type, ""))

        with open(config_file, "r") as f:
            configContent = f.read()
            configContentJson = json.loads(configContent)
            confi_env = configContentJson["env"]
            confi_globals = configContentJson["globals"]
            config_rules = configContentJson["rules"]
            config_plugins = configContentJson["plugins"]

        # enable rules
        if set_rule_flag and rule_list:
            self._set_rule_config(config_rules, rule_list, config_plugins)

        # 设置env
        for e in eslint_env.split(";"):
            if not e:
                continue
            confi_env[e] = True

        # 设置globals配置
        for g in eslint_globals.split(";"):
            tem = g.split(":")
            if len(tem) != 2 or tem[1] == "":
                continue
            confi_globals[tem[0]] = tem[1]

        # 设置HTML插件
        if envs.get("ESLINT_EXT_HTML"):
            if "plugins" in configContentJson.keys():
                configContentJson["plugins"].append("html")
            else:
                configContentJson["plugins"] = ["html"]

        # 使用文件设置
        if eslint_options and os.path.isfile(eslint_options):
            self.print_log("eslint_options: %s" % eslint_options)
            with open(eslint_options, "r") as f:
                add = json.load(f)
            self._recursive_merge(configContentJson, add)
        # 配置 tsconfig 配置
        if parserOptions:
            if "parserOptions" in configContentJson.keys():
                configContentJson["parserOptions"]["project"] = parserOptions["project"]
            else:
                configContentJson["parserOptions"] = parserOptions
        with codecs.open(config_file, "w", encoding="utf-8") as f:
            json.dump(configContentJson, f, ensure_ascii=False, indent=2)

    def _set_rule_config(self, config_rules, rule_list, config_plugins):
        """
        规则的配置
        """
        # 设置eslint插件，根据所选规则添加对应插件
        jsx_a11y_plugin = False
        vuejs_accessibility_plugin = False

        for rule in rule_list:
            rule_name = rule["name"]
            # 根据规则名判断插件
            if rule_name == "parse-error":
                continue
            if rule_name.startswith("jsx-a11y/"):
                jsx_a11y_plugin = True
            if rule_name.startswith("vuejs-accessibility/"):
                vuejs_accessibility_plugin = True
            # 兼容旧版typescript的规则
            if rule_name.startswith("typescript/"):
                rule_name = rule_name.replace("typescript/", "@typescript-eslint/")
            config_rules[rule_name] = "warn"
            # 支持规则参数设置
            if not rule["params"]:
                continue
            param = rule["params"]
            # 1. 直接拷贝在配置文件Json中的设置
            try:
                # demo: [\"error\", \"tab\", { \"SwitchCase\": 60 }]
                config_rules[rule_name] = json.loads(param)
            except json.JSONDecodeError as e:
                # 2. 使用key-value方式
                # 数组的非字典元素，使用options指定
                # 数组的字典元素，就使用key/value的方式
                # 若十分复杂，就直接传参json字符串
                # demo: options=tab\nSwitchCase=1
                if "[block]" in param:
                    rule_params = param
                else:
                    rule_params = "[block]\r\n" + param
                rule_params_dict = ConfigReader(cfg_string=rule_params).read("block")
                rule_params = ["warn"]
                if rule_params_dict.get("options"):
                    rule_params.extend(
                        [StringMgr.trans_type(option) for option in rule_params_dict["options"].split(",")]
                    )
                    rule_params_dict.pop("options")
                if len(rule_params_dict.keys()) > 0:
                    for key in rule_params_dict:
                        rule_params_dict[key] = StringMgr.trans_type(rule_params_dict[key])
                    rule_params.append(rule_params_dict)
                config_rules[rule_name] = rule_params
        
        # 设置plugin
        if jsx_a11y_plugin:
            config_plugins.append("jsx-a11y")
        if vuejs_accessibility_plugin:
            config_plugins.append("vuejs-accessibility")

    def _find_eslintrc(self, root_dir):
        """
        查找项目目录下所有的.eslintrc.*
        这里只检查根目录下的文件是否包含eslint配置文件
        package.json文件也可以设置eslint配置，但这里不对package.josn进行检查，因为每个Js项目都可能有该文件
        :param root_dir:
        :return:
        """
        for fileOrDir in os.listdir(root_dir):
            path = os.path.join(root_dir, fileOrDir)
            if os.path.isdir(path):
                continue
            if re.match("(\.eslintrc.*)", fileOrDir, re.I):
                return True
        return False

    def _find_tsconfig(self, root_dir):
        """
        查找项目目录下所有的tsconfig.json文件
        某些规则需要配置tsconfig.json路径
        这里检查项目中已存在的tsconfig文件
        :param root_dir: 项目地址
        :return List: 所有tsconfig路径
        """
        tsconfigFiles = []
        dirList = os.walk(root_dir)
        for root, dirs, files in dirList:
            for f in files:
                if "tsconfig.json" == f:
                    tsconfigFiles.append(os.path.join(root, f))
        return tsconfigFiles

    def _set_tsconfig_file(self, work_dir):
        """写入默认tsconfig文件, 返回project配置
        :param work_dir:
        :return tsconfigFile: 默认tsconfig配置路径
        """
        tsconfigFile = "{}/tsconfig.json".format(work_dir)
        with open(tsconfigFile, "w") as f:
            json.dump(
                """{
                        "extends": "",
                        "compilerOptions": {},
                        "include": [],
                        "exclude": []
                        }""",
                f,
                indent=2,
            )
        return tsconfigFile

    def scan(self, params, config_path, error_output, eslint_ext):
        """

        :param params:
        :param config_path:
        :param error_output:
        :return:
        """
        source_dir = params.source_dir
        path_exclude = params.path_filters.get("wildcard_exclusion", [])
        path_include = params.path_filters.get("wildcard_inclusion", [])
        incr_scan = params["incr_scan"]
        envs = os.environ

        if "ESLINT_MAX_OLD_SPACE_SIZE" in envs:
            # 或者设置NODE_OPTIONS="--max-old-space-size=4096"
            scan_cmd = ["node", "--max-old-space-size=" + envs["ESLINT_MAX_OLD_SPACE_SIZE"]]
            if sys.platform == "win32":
                scan_cmd.append(os.path.join(envs.get("NODE_HOME"), "node_modules", "eslint", "bin", "eslint.js"))
            else:
                scan_cmd.append(
                    os.path.join(envs.get("NODE_HOME"), "lib", "node_modules", "eslint", "bin", "eslint.js")
                )
        else:
            scan_cmd = ["eslint"]

        if config_path:
            scan_cmd.extend(["--config", config_path, "--no-eslintrc"])

        scan_cmd.extend(["-f", "checkstyle", "-o", error_output, "--debug"])

        if "ESLINT_OPTION_PARAMS" in envs:
            scan_cmd.extend(shlex.split(envs["ESLINT_OPTION_PARAMS"]))

        scan_cmd.extend(["--ext", eslint_ext])

        # 设置扫描路径过滤 exclusion and inclusion
        scan_cmd.extend(self._get_path_filte(path_exclude, path_include))
        # 默认不使用代码库下eslintignore文件中的过滤路径, 除非设置环境变量ESLINT_IGNORE指定
        eslint_ignore = envs.get("ESLINT_IGNORE", None)
        ignore_file = eslint_ignore if eslint_ignore else self.get_ignore_file(params)
        scan_cmd.extend(["--ignore-path", ignore_file])

        # 指定扫描目录或者文件，支持增量
        relpos = len(source_dir) + 1
        if incr_scan:
            diffs = SCMMgr(params).get_scm_diff()
            toscans = [
                os.path.join(source_dir, diff.path)
                for diff in diffs
                if diff.path.endswith(tuple(eslint_ext.split(","))) and diff.state != "del"
            ]
            toscans = FilterPathUtil(params).get_include_files(toscans, relpos)
            toscans = [path[relpos:].replace(os.sep, "/") for path in toscans]

            # windows下增量文件路径总长度超长，改为扫描整个soucedir，否则会执行异常
            # 因为 windows 下执行subprocess.Popen方法且shell=False的情况下，命令长度限制为32768字节
            # 这里文件路径长度限制为32500，因为前面还要预留cppcheck命令的长度
            if sys.platform == "win32" and len(" ".join(toscans)) > 32500:
                toscans = ["."]
        else:
            toscans = ["."]

        if not toscans:
            LogPrinter.debug("To-be-scanned files is empty ")
            return
        scan_cmd.extend(toscans)

        # 由于eslint会按照js的严格模式来解析js代码，若解析错误便会产生一个error，导致返回值非0
        self.print_log("cmd: %s" % " ".join(scan_cmd))
        sub_proc = SubProcController(
            scan_cmd, cwd=source_dir, stdout_line_callback=self.print_log, stderr_line_callback=self.print_log
        )
        sub_proc.wait()
        # 适配代码库下没有js相关文件的情况
        if sub_proc.returncode != 0:
            LogPrinter.error("命令执行返回码为: %d" % sub_proc.returncode)
            err_log = self.__get_stderr_log(sub_proc)
            if err_log.find("No files matching the pattern") != -1:
                LogPrinter.error("指定扫描的代码目录下面无可扫描文件，请检查配置")
                return
            # 查找"Cannot find module" 可能会出现误报
            elif err_log.find("ESLint couldn't find the") != -1:
                raise ConfigError("复用客户代码库中的Eslint配置文件，但没有安装相关插件，请在机器上安装，或者评估使用默认Alloy配置")
            # 设置没有配置文件错误提示
            elif err_log.find("ESLint couldn't find a configuration file.") != -1:
                raise ConfigError("代码库根目录中没有发现Eslint配置文件")

            # 捕获JS堆溢出异常
            elif (
                err_log.find(
                    "FATAL ERROR: Ineffective mark-compacts near heap limit Allocation failed \
                    - JavaScript heap out of memory"
                )
                != -1
            ):
                raise ConfigError("JS堆溢出错误，麻烦设置过滤库文件或者设置增加JS堆")

    def data_handle(self, params, error_output, rule_filte_flag):
        """
        处理结果文件
        :param params:
        :param error_output:
        :param rule_filte_flag:
        :return:
        """
        source_dir = params.source_dir
        filter_mgr = FilterPathUtil(params)
        pos = len(source_dir) + 1
        rules = params.get("rules", [])

        if not os.path.exists(error_output) or os.stat(error_output).st_size == 0:
            LogPrinter.info("result is empty ")
            return []

        # 处理unicode字符，否则会导致解析失败, 并非所有有效的Unicode字符在XML中都有效
        text = open(error_output, "r").read()
        # 替换所有无效Unicode字符
        text = re.sub(
            r"&#([0-8]);|&#1([1-24-9]);|&#2([0-9]);|&#3([0-1]);|&#x0?([0-8bcBCefEF]);|&#x1([0-9a-fA-F])",
            "",
            text,
            count=0,
            flags=re.I,
        )
        raw_warning = ET.fromstring(text)
        issues = []
        for file in raw_warning.findall("file"):
            # tag, attrib
            path = file.attrib.get("name")[pos:]
            if filter_mgr.should_filter_path(path):
                continue
            for error in file:
                # 若解析文件失败，便可能会line为undefined，该结果无效
                if error.attrib.get("line") == "undefined":
                    continue
                line = int(error.attrib.get("line"))
                column = error.attrib.get("column")
                if column in ("NaN",):
                    column = 0
                # need rule real name
                tmp = error.attrib.get("source").split(".")
                rule = tmp[-1]
                msg = error.attrib.get("message")
                # 记录解析错误带来的问题
                if rule == "" and msg.startswith("Parsing error:"):
                    rule = "parse-error"
                    # parse-error规则，移除msg中的代码块
                    if msg.find(".\n\n") != -1:
                        msg = "".join(msg.split(".\n\n")[:-1])
                # 兼容旧版typescript的规则
                # if alloy_version == "2.0.5" and rule.startswith("@typescript-eslint/"):
                if rule.startswith("@typescript-eslint/"):
                    rule = rule.replace("@typescript-eslint/", "typescript/")
                # 若使用客户的配置文件，不进行规则过滤
                if rule_filte_flag and rule not in rules:
                    continue
                if msg.startswith("Definition for rule"):
                    continue
                issues.append({"path": path, "rule": rule, "msg": msg, "line": line, "column": column})
        return issues

    def __get_stderr_log(self, sub_proc):
        """
        获取执行stderr的log
        :param sub_proc:
        :return: stderr中的log
        """
        if not os.path.exists(sub_proc.stderr_filepath):
            return ""
        spc_err = open(sub_proc.stderr_filepath, "r", encoding="utf-8")
        log = spc_err.read()
        spc_err.close()
        return log

    def _recursive_merge(self, src, add):
        """
        递归合并两json内容
        :param src: 原始json
        :param add: 需要添加的内容
        :return:
        """
        if isinstance(src, dict):
            for a in add:
                if a in src:
                    # 如果在src中，且是复合类型，则递归
                    if isinstance(src[a], dict) or isinstance(src[a], list):
                        self._recursive_merge(src[a], add[a])
                    else:
                        # 若是String或者bool等基本类型，则直接覆盖
                        src[a] = add[a]
                else:
                    # 如果不在src中，则添加
                    src[a] = add[a]
        elif isinstance(src, list):
            # list只能添加，不能继续递归修改
            for a in add:
                if a not in src:
                    src.append(a)

    def _get_path_filte(self, path_exclude, path_include):
        """
        给scan_cmd设置路径过滤扫描的命令行配置
        其中：
        **匹配多个目录，当test/**时候，匹配test目录下所有目录和文件
        *匹配除了/以外的任意多个字符
        ?匹配出了/以外的一个字符
        :param path_exclude:
        :param path_include:
        :return:
        """
        path_filter = []

        # 使用!来做--ignore-pattern的否定判断
        # 默认会过滤掉/**/node_modules/*  但是--ignore-pattern优先级更高
        # 但是这个不能不扫描include以外的文件，只是表示要扫描哪些文件
        if path_include:
            for tmp_path in path_include:
                path_filter.append("--ignore-pattern")
                tmp_path = re.sub("^\*/", "**/", tmp_path)
                tmp_path = re.sub("/\*$", "/**", tmp_path)
                tmp_path = re.sub("/\*/", "/**/", tmp_path)
                path_filter.append(f"'!{tmp_path}'")

        if path_exclude:
            for tmp_path in path_exclude:
                path_filter.append("--ignore-pattern")
                tmp_path = re.sub("^\*/", "**/", tmp_path)
                tmp_path = re.sub("/\*$", "/**", tmp_path)
                tmp_path = re.sub("/\*/", "/**/", tmp_path)
                path_filter.append(f"'{tmp_path}'")

        return path_filter

    def get_ignore_file(self, params, eslint_ext=None):
        """
        1. 忽略文件需要在代码库根目录下，否则base目录有误，会取代码库根目录和忽略文件路径的交叉处作为baseDir
        2. 会增加内存。目前8GB堆内存，可以支撑54300条，耗时从原本的5min增加到16min，若没有**/前缀，则是13min
        :param params:
        :param eslint_ext:
        :return:
        """
        source_dir = params.source_dir
        relpos = len(source_dir) + 1
        work_dir = params.work_dir
        ignore_file = os.path.join(work_dir, "codedog_eslintignore")

        if eslint_ext:
            want_suffix = eslint_ext.split(",")
            files = PathMgr().get_dir_files(source_dir, tuple(want_suffix))
            files = [path.replace(os.sep, "/") for path in files]
            include_files = FilterPathUtil(params).get_include_files(files, relpos)
            exclude_files = list(set(files) - set(include_files))
            ignore_files = ["**/%s" % path[relpos:] for path in exclude_files]
        else:
            ignore_files = list()
        with open(ignore_file, "w", encoding="UTF-8") as f:
            f.write("\n".join(ignore_files))
        return ignore_file

    def check_tool_usable(self, tool_params):
        """
        这里判断机器是否支持运行eslint
        1. 支持的话，便在客户机器上扫描
        2. 不支持的话，就发布任务到公线机器扫描
        :return:
        """
        if SubProcController(["node", "--version"], stderr_line_callback=self.print_log).wait() != 0:
            return []
        if SubProcController(["eslint", "--version"], stderr_line_callback=self.print_log).wait() != 0:
            return []
        return ["analyze"]


tool = Eslint

if __name__ == "__main__":
    pass
