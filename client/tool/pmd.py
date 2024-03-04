#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
pmd: An extensible cross-language static code analyzer.
"""

import json
import os
import sys

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from util.pathlib import PathMgr
from util.pathfilter import FilterPathUtil
from task.codelintmodel import CodeLintModel
from util.subprocc import SubProcController
from util.logutil import LogPrinter

logger = LogPrinter


class Pmd(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.sensitive_word_maps = {"Pmd": "Tool", "PMD": "Tool", "pmd": "Tool"}

    def analyze(self, params):
        """

        :param params:
        :return:
        """
        source_dir = params.source_dir
        work_dir = os.getcwd()
        rules = params["rules"]
        filter_mgr = FilterPathUtil(params)
        error_output = os.path.join(work_dir, "PMDErrorOutput.xml")
        PMD_HOME = os.environ.get("PMD_HOME")
        path_mgr = PathMgr()

        # enabled rules
        default_rules = list()
        custom_rules = list()
        if not rules:
            pmd_rulesets = os.path.join(PMD_HOME, "pmd_rulesets.json")
            with open(pmd_rulesets, "r") as f:
                pmdRuleSetContent = f.read()
                default_rules = json.loads(pmdRuleSetContent)
                LogPrinter.debug("load all rules!")
        else:
            # Server传来规则，需要将之分为pmd自带规则和自定义规则
            for rule in rules:
                if rule.startswith("custom_"):
                    custom_rules.append(rule)
                else:
                    default_rules.append(rule)
        # 添加自定义规则
        usedRules = ",".join(default_rules + path_mgr.get_dir_files(os.path.join(PMD_HOME, "plugins"), ".xml"))
        LogPrinter.debug(usedRules)

        # example
        # ./run.sh pmd -d ../../pmd/pmd/pmd-java -R rulesets/java/basic.xml
        # ./run.sh pmd -d ../../pmd/pmd/pmd-java -R rulesets/java/basic.xml/CollapsibleIfStatements,
        # rulesets/java/basic.xml/DoubleCheckedLocking
        #   -f xml -r PMDresult2.xml -shortnames -debug
        if sys.platform == "win32":
            scan_cmd = [os.path.join(PMD_HOME, "bin", "pmd.bat")]
        else:
            # mac and linux
            scan_cmd = [os.path.join(PMD_HOME, "bin", "run.sh"), "pmd"]
        scan_cmd.extend(
            [
                "-R",
                usedRules,
                "-f",
                "xml",
                "-failOnViolation",
                "false",
                "-r",
                error_output,
                "-shortnames",
                "-debug",
                "-encoding",
                "utf-8",
            ]
        )

        scan_cmd.extend(["-d", source_dir])
        self.print_log("cmd: %s" % " ".join(scan_cmd))
        SubProcController(scan_cmd, cwd=source_dir).wait()

        # update_task_progress(request, '扫描结果处理', 60)
        raw_warning = ET.ElementTree(file=error_output)
        issues = []
        for file in raw_warning.findall("file"):
            # tag, attrib
            path = file.attrib.get("name")
            if filter_mgr.should_filter_path(path):
                continue
            for error in file:
                line = int(error.attrib.get("beginline"))
                column = int(error.attrib.get("begincolumn"))
                # rule real name
                ruleUrl = error.attrib.get("externalInfoUrl", None)
                if ruleUrl.startswith("https://"):
                    pos = ruleUrl.find("rules/")
                    rule = ruleUrl[pos:]
                    rule = rule.replace("rules", "rulesets")
                    rule = rule.replace("html#", "xml/")
                else:
                    rule = ruleUrl
                if rule not in rules:
                    continue
                msg = error.text + ruleUrl
                issues.append({"path": path, "rule": rule, "msg": msg, "line": line, "column": column})
        LogPrinter.debug(issues)

        return issues


tool = Pmd

if __name__ == "__main__":
    pass
