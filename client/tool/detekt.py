#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
detekt: kotlin static analysis tool
"""

import os
import yaml
import csv
import json
import shlex
from shutil import copyfile

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from util.pathlib import PathMgr
from util.pathfilter import FilterPathUtil
from task.codelintmodel import CodeLintModel
from util.subprocc import SubProcController
from util.logutil import LogPrinter


class Detekt(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.sensitive_word_maps = {"detekt": "Tool", "Detekt": "Tool"}

    def analyze(self, params):
        """
        分析执行函数
        :param params:
        :return:
        """
        source_dir = params.source_dir
        work_dir = os.getcwd()
        enabled_rules = params.rules
        filter_mgr = FilterPathUtil(params)
        error_output = os.path.join(work_dir, "detekt-checkstyle.xml")
        envs = os.environ
        detekt_home = envs.get("DETEKT_171_HOME")
        pos = len(source_dir) + 1

        self.scan(
            params, detekt_home, report_type="xml", report_path=error_output, config=self.config(params, detekt_home)
        )

        raw_warning = ET.ElementTree(file=error_output)
        issues = []
        for f in raw_warning.iter(tag="file"):
            path = f.attrib.get("name")[pos:]
            if filter_mgr.should_filter_path(path):
                continue
            for error in f:
                line = int(error.attrib.get("line"))
                column = int(error.attrib.get("column"))
                tmp = error.attrib.get("source").split(".")
                rule = tmp[1]
                # 项目使用自己的规则配置文件，这里当项目指定了配置文件时候不做规则过滤
                if "DETEKT_PLUGINS_CONFIG" in envs and rule not in enabled_rules:
                    continue
                msg = error.attrib.get("message")
                issues.append({"path": path, "rule": rule, "msg": msg, "line": line, "column": column})
        LogPrinter.debug(issues)
        return issues

    def config(self, params, detekt_home):
        """

        :param params:
        :param detekt_home:
        :return:
        """
        source_dir = params.source_dir
        work_dir = params.work_dir
        enabled_rules = params.rules
        envs = os.environ

        # enable rules
        config_file = os.path.join(work_dir, "detekt-config.yml")
        if os.path.exists(config_file):
            os.remove(config_file)
        if enabled_rules:
            copyfile(os.path.join(detekt_home, "detekt-config-example.yml"), config_file)
            config = open(config_file)
            content = yaml.safe_load(config)
            for item in content.values():
                if not isinstance(item, dict):
                    continue
                for rule in enabled_rules:
                    if rule in item:
                        item.get(rule)["active"] = True
            config = open(config_file, "w")
            yaml.dump(content, config, default_flow_style=False)
            config.close()
        else:
            copyfile(os.path.join(detekt_home, "puppy-default-detekt-config.yml"), config_file)

        # 设置第三方规则集jar配置
        user_plugins_config = envs.get("DETEKT_PLUGINS_CONFIG", None)
        if user_plugins_config:
            user_plugins_config_path = os.path.join(source_dir, user_plugins_config)
            # 若是配置文件，则提取出来
            # 修改为直接调用该config文件
            if os.path.isfile(user_plugins_config_path):
                config_file = user_plugins_config_path
            else:
                # 若是配置字符串
                user_config = json.loads(user_plugins_config)
                content = yaml.safe_load(open(config_file))
                content.update(user_config)
                config = open(config_file, "w")
                # content中可能部分为unicode编码，dump时候可能会报错，这里是
                yaml.safe_dump(content, config, default_flow_style=False)
                config.close()

        return config_file

    def scan(self, params, detekt_home, report_type, report_path, source_dir=None, config=None, rule=None):
        """

        :param params:
        :param detekt_home:
        :param report_type:
        :param report_path:
        :param source_dir:
        :param config:
        :param rule:
        :return:
        """
        source_dir = source_dir if source_dir else params.source_dir
        path_include = params.path_filters.get("wildcard_inclusion", [])
        path_exclude = params.path_filters.get("wildcard_exclusion", [])
        envs = os.environ
        path_mgr = PathMgr()

        scan_cmd = [
            "java",
            "-jar",
            os.path.join(detekt_home, "detekt.jar"),
            "-i",
            source_dir,
            "--report",
            "%s:%s" % (report_type, report_path),
            "--debug",
            "--parallel",
        ]

        # 查看工具libs下有没有plugins第三方规则集jar包
        # 相关的第三方规则集配置写在detekt-config-example.yml中
        jars_list = path_mgr.get_dir_files(os.path.join(detekt_home, "libs"), ".jar")
        # 若客户指定代码库中的第三方规则集jar包, 支持输入目录或者文件，使用;隔开
        user_plugins = envs.get("DETEKT_PLUGINS", None)
        if user_plugins:
            user_plugins_list = [os.path.join(source_dir, path) for path in user_plugins.split(";")]
            for path in user_plugins_list:
                if os.path.isdir(path):
                    jars_list.extend(path_mgr.get_dir_files(path, ".jar"))
                elif os.path.isfile(path) and path.endswith(".jar"):
                    jars_list.append(path)
        if jars_list:
            scan_cmd.append("--plugins")
            scan_cmd.append(";".join(jars_list))

        # 设置规则配置
        if config:
            scan_cmd.extend(["--config", config])
        if rule:
            scan_cmd.extend(["--run-rule", rule])

        # 设置额外的detekt参数
        # 比如--jvm-target --classpath
        detekt_option_params = envs.get("DETEKT_OPTION_PARAMS", None)
        if detekt_option_params:
            scan_cmd.extend(shlex.split(detekt_option_params))

        # 设置路径过滤
        if path_exclude:
            scan_cmd.extend(
                ["--excludes", '"%s"' % (",".join(["**" + path.replace("*", "**") for path in path_exclude]))]
            )
        if path_include:
            scan_cmd.extend(
                ["--includes", '"%s"' % (",".join(["**" + path.replace("*", "**") for path in path_include]))]
            )

        self.print_log("scan cmd: %s" % " ".join(scan_cmd))
        subProC = SubProcController(scan_cmd, cwd=source_dir)
        subProC.wait()
        rt = subProC.returncode
        if rt != 0:
            LogPrinter.error("工具分析异常，返回码为%d" % rt)


tool = Detekt

if __name__ == "__main__":
    pass
