# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scalastyle 扫描任务
"""

import os
import sys

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from task.scmmgr import SCMMgr
from util.pathfilter import FilterPathUtil
from task.codelintmodel import CodeLintModel
from util.exceptions import AnalyzeTaskError
from util.subprocc import SubProcController
from util.configlib import ConfigReader

from util.logutil import LogPrinter

logger = LogPrinter


class ScalaStyle(CodeLintModel):
    """ScalaStyle 类"""

    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.model_config_file = os.path.join(os.environ["SCALASTYLE_HOME"], "config", "model.xml")
        self.sensitive_word_maps = {
            "ScalaStyle": "Tool",
            "scalastyle": "Tool",
        }

    def analyze(self, params):
        source_dir = params["source_dir"]
        self.pos = len(source_dir) + 1
        self.rules = params["rules"]
        envs = os.environ
        rule_list = params["rule_list"]
        incr_scan = params["incr_scan"]
        scalastyle_home = envs.get("SCALASTYLE_HOME")
        config_type = envs.get("SCALA_TYPE", None)
        output_file = os.path.join(os.getcwd(), "result.xml")
        # 根据是否配置使用腾讯代码规范设置配置文件
        if not config_type:
            config_file = self.generate_config(rule_list)
        # 使用规范配置
        elif config_type == "tencent":
            config_file = os.path.join(scalastyle_home, "config", "standard.xml")
        scan_cmd = [
            os.path.join(os.environ["JDK_8_HOME"], "bin", "java"),
            "-jar",
            os.path.join(os.environ["SCALASTYLE_HOME"], "scalastyle_2.12-1.0.0-batch.jar"),
            "--config",
            config_file,
            "--xmlOutput",
            output_file,
        ]
        toscans = []
        if incr_scan:
            diffs = SCMMgr(params).get_scm_diff()
            toscans = [
                os.path.join(source_dir, diff.path).replace(os.sep, "/")
                for diff in diffs
                if diff.path.endswith(tuple(".scala")) and diff.state != "del"
            ]
            relpos = len(source_dir) + 1
            # toscans = PathFilter.get_include_files(toscans, relpos, path_include, path_exclude)
            toscans = FilterPathUtil(params).get_include_files(toscans, relpos)
        else:
            toscans = [source_dir]
        if sys.platform == "win32" and len(max(toscans)) > 32500:
            # 增量命令长度超过限制为了保证不失败进行全量分析
            toscans = [source_dir]

        if not toscans:
            LogPrinter.debug("To-be-scanned files is empty ")
            return []
        scan_cmd.extend(toscans)
        issues = []
        LogPrinter.info(" ".join(scan_cmd))
        spc = SubProcController(
            scan_cmd,
            stdout_line_callback=ScalaStyle(params).print_log,
            stderr_line_callback=ScalaStyle(params).print_log,
        )
        spc.wait()
        issues = self.format_issues(output_file)
        return issues

    def generate_config(self, rule_list):
        """生成配置文件
        :param rule_list: 规则参数
        :return path: 配置文件绝对路径
        """
        # 读取空模版
        config_file = os.path.join(os.path.abspath(os.curdir), "config.xml")
        if not os.path.exists(self.model_config_file):
            raise AnalyzeTaskError(
                f"The template configuration file {self.model_config_file} does not exist, please check! "
            )
        # 写入模版框架
        open(config_file, "wb").write(open(self.model_config_file, "rb").read())
        config_data = ET.parse(config_file)
        root = config_data.getroot()
        LogPrinter.info(root)
        # 读取前端规则的自定义参数格式为 max=120 这种形式
        for rule in rule_list:
            rule_params = rule.get("params", None)
            check_node = ET.Element("check")
            check_node.set("class", rule["name"])
            check_node.set("enabled", "true")
            check_node.set("level", "warning")
            if rule_params:
                # 配置转换为ini这种配置
                if "[scalastyle]" not in rule_params:
                    rule_params = "[scalastyle]\r\n" + rule_params
                rule_params = ConfigReader(cfg_string=rule_params).read("scalastyle")
                logger.info(rule_params)
                child_node = ET.Element("parameters")
                for key, value in rule_params.items():
                    param_node = ET.Element("parameter")
                    param_node.set("name", key)
                    param_node.text = str(value)
                    child_node.append(param_node)
                check_node.append(child_node)
            root.append(check_node)
        config_data.write(config_file)
        return config_file

    def format_issues(self, output_file):
        """格式化scalastyle结果
        """
        if not os.path.exists(output_file):
            LogPrinter.info("分析失败")
            return []
        issues = []
        root = ET.parse(output_file).getroot()
        files = root.findall("file")
        for file_node in files:
            errors = file_node.findall("error")
            for error in errors:
                path = file_node.get("name")
                rule = error.get("source")
                line = error.get("line")
                # 有些是文件层级错误没有line信息
                if not line:
                    line = 1
                column = error.get("column")
                if not column:
                    column = "1"
                msg = error.get("message")
                if rule not in self.rules:
                    continue
                issues.append(
                    {
                        "path": path[self.pos :],
                        "line": int(line),
                        "column": column,
                        "msg": msg,
                        "rule": rule,
                    }
                )
        return issues


tool = ScalaStyle

if __name__ == "__main__":
    pass
