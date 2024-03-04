#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================


import os
import json
import sys
import yaml

from task.scmmgr import SCMMgr
from task.basic.common import subprocc_log
from util.subprocc import SubProcController
from util.textutil import CodecClient
from util.pathfilter import PathMgr, FilterPathUtil
from node.app import settings
from util.logutil import LogPrinter
from task.authcheck.check_license import __lu__


class Amani(object):
    support_languages = [
        "cpp",
        "oc",
        "cs",
        "css",
        "dart",
        "java",
        "js",
        "kotlin",
        "lua",
        "php",
        "python",
        "go",
        "ruby",
        "scala",
        "swift",
        "ts",
    ]

    def __init__(self, params=None, source_dir=None, work_dir=None, scan_languages=None):
        self.params = params
        if self.params:
            self.source_dir = params.source_dir if source_dir is None else source_dir
            self.relpos = len(self.source_dir) + 1
            self.work_dir = params.work_dir if work_dir is None else work_dir
            self.scan_languages = (
                scan_languages if scan_languages is not None else self.params.get("scan_languages", [])
            )
            # 获取支持的语言
            self.scan_languages = [
                lang.lower() for lang in self.scan_languages if lang.lower() in self.support_languages
            ]

        self.tool_home = os.environ.get("AMANI_HOME")
        self.tool_name = self.__class__.__name__

    def get_cmd(self, args):
        tool_path = os.path.join(self.tool_home, "bin", settings.PLATFORMS[sys.platform], self.tool_name)
        if settings.PLATFORMS[sys.platform] == "windows":
            tool_path = f"{tool_path}.exe"
        return __lu__().format_cmd(tool_path, args)

    def get_version(self):
        """
        获取工具版本号
        :param params:
        :return:
        """
        work_dir = self.params.work_dir
        scan_cmd = self.get_cmd(
            [
                "--version",
            ]
        )
        lang_ext_output = os.path.join(work_dir, f"{self.tool_name}_version.txt")
        # 获取对应语言的文件后缀
        # LogPrinter.info(f"scan_cmd: {' '.join(scan_cmd)}")
        spc = SubProcController(
            scan_cmd,
            stdout_line_callback=subprocc_log,
            stderr_line_callback=subprocc_log,
            stdout_filepath=lang_ext_output,
        )
        spc.wait()

        fi = open(lang_ext_output, "rb")
        # 读取文件内容并解码为字符串
        content = CodecClient().decode(fi.read())
        fi.close()
        return content.split("(")[-1][:-1]

    def check(self, files=None, want_suffix=None, force_all=False):
        """

        :param params:
        :param source_dir:
        :param scan_languages: 列表
        :param files:
        :param want_suffix:
        :param force_all:
        :return:
        """
        incr_scan = self.params.get("incr_scan", False)
        output = os.path.join(self.work_dir, f"{self.tool_name.lower()}_output")
        files_path = os.path.join(self.work_dir, f"{self.tool_name.lower()}_paths.txt")

        toscans = files
        want_suffix = want_suffix if want_suffix else self.get_lang_ext()
        if toscans is None:
            if incr_scan and not force_all:
                diffs = SCMMgr(self.params).get_scm_diff()
                toscans = [
                    os.path.join(self.source_dir, diff.path)
                    for diff in diffs
                    if diff.path.endswith(tuple(want_suffix)) and diff.state != "del"
                ]
            else:
                toscans = PathMgr().get_dir_files(self.source_dir, tuple(want_suffix))
        else:
            toscans = [file for file in toscans if file.endswith(tuple(want_suffix))]
        toscans = [path.replace(os.sep, "/") for path in toscans]
        toscans = FilterPathUtil(self.params).get_include_files(toscans, self.relpos)

        if not toscans:
            LogPrinter.info("被分析文件列表为空")
            return None
        with open(files_path, "w", encoding="UTF-8") as f:
            f.write("\n".join(toscans))

        options = [
            "-s",
            self.source_dir,
            "-l",
            ",".join(self.scan_languages),
            "-o",
            output,
            "-p",
            files_path,
        ]
        # 支持指定规则，使用config文件来指定规则，rules和rulepath字段
        rules = self.params.get("rules", list())
        rules_config = {"rules": []}
        rulepaths = list()
        for rule in rules:
            for language in self.scan_languages:
                rulepath = os.path.join(self.tool_home, "rules", language, rule)
                if os.path.exists(rulepath):
                    rulepaths.append(rulepath)
                else:
                    rules_config["rules"].append({"name": rule, "languages": language})
        if rulepaths:
            rules_config["rulepath"] = ",".join(rulepaths)
        config_path = os.path.join(self.work_dir, f"{self.tool_name}_config.yml")
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(rules_config, f)
        options.extend(["-c", config_path])

        scan_cmd = self.get_cmd(options)

        # LogPrinter.info(f"scan_cmd: {' '.join(scan_cmd)}")
        spc = SubProcController(
            scan_cmd,
            self.tool_home,
            stdout_line_callback=subprocc_log,
            stderr_line_callback=subprocc_log,
        )
        spc.wait()

        return output

    def get_lang_ext(self):
        """
        获得对应语言的文件后缀
        :param params:
        :param scan_languages:
        :return:
        """
        # 为空时，直接返回
        if not self.scan_languages:
            return []

        scan_cmd = self.get_cmd(
            [
                "-l",
                ",".join(self.scan_languages),
                "-e",
            ]
        )
        lang_ext_output = os.path.join(self.work_dir, "lang_ext.txt")
        # 获取对应语言的文件后缀
        # logger.info(f"scan_cmd: {' '.join(scan_cmd)}")
        spc = SubProcController(
            scan_cmd,
            stdout_line_callback=subprocc_log,
            stderr_line_callback=subprocc_log,
            stdout_filepath=lang_ext_output,
        )
        spc.wait()
        fi = open(lang_ext_output, "rb")
        # 读取文件内容并解码为字符串
        content = CodecClient().decode(fi.read())
        fi.close()
        return content.split()[-1].strip().split(",")

    def get_issue(self, output):
        """
        解析结果文件
        :param output:
        :return:
        """
        if not output or not os.path.exists(output):
            return

        rules = self.params.get("rules", list())
        relpos = len(self.params.source_dir) + 1

        for issue_file in PathMgr().get_dir_files(output, tuple(".issue")):
            # 解析结果
            f = open(issue_file, "r", encoding="utf-8")
            content = json.load(f)
            for block in content:
                path = block["path"][relpos:]
                line = int(block["start_line"])
                column = int(block["start_column"])
                rule = block["rule"]
                if rule not in rules:
                    continue
                msg = block["message"]
                yield {
                    "rule": rule,
                    "msg": msg,
                    "path": path,
                    "line": line,
                    "column": column,
                }
            f.close()


tool = Amani

if __name__ == "__main__":
    pass
