# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================


import os
import csv
import json
import sys
import psutil

from task.scmmgr import SCMMgr
from node.common.processmgr import ProcMgr
from task.basic.common import subprocc_log
from util.subprocc import SubProcController
from util.textutil import CodecClient
from util.pathfilter import PathMgr, FilterPathUtil
from util.textutil import CommentsManager
from util.logutil import LogPrinter
from util.configlib import ConfigReader
from node.app import settings
from task.authcheck.check_license import __lu__

logger = LogPrinter


class Collie(object):
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
            self.scan_languages = [
                lang.lower() for lang in self.scan_languages if lang.lower() in self.support_languages
            ]

        self.tool_home = os.environ.get("COLLIE_HOME")
        self.tool_name = self.__class__.__name__

    def get_cmd(self, args):
        tool_path = os.path.join(self.tool_home, "bin", settings.PLATFORMS[sys.platform], self.tool_name)
        if settings.PLATFORMS[sys.platform] == "windows":
            tool_path = f"{tool_path}.exe"
        return __lu__().format_cmd(tool_path, args)

    def _close_proc(self, pid):
        try:
            psutil.Process(pid)
            ProcMgr().kill_proc_famliy(pid)
        except psutil.NoSuchProcess as e:
            # logger.exception("exception: %s", str(e))
            pass

    def scan(self, files=None, want_suffix=None, force_all=False):
        """
        :return: 返回ccn相关结果
        """
        output = self.check(files, want_suffix, force_all, True)
        if output:
            return os.path.join(output, "ccn.csv")
        return None

    def check(self, files=None, want_suffix=None, force_all=False, method_mode=False):
        incr_scan = self.params.get("incr_scan", False)
        func_output = os.path.join(self.work_dir, f"{self.tool_name.lower()}_output")
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
            logger.info("被分析文件列表为空")
            return None
        with open(files_path, "w", encoding="UTF-8") as f:
            f.write("\n".join(toscans))

        options = [
            "-l",
            ",".join(self.scan_languages),
            "-o",
            func_output,
            "-F",
            "csv",
            "-s",
            self.source_dir,
            "-p",
            files_path,
        ]
        if method_mode:
            options.append("-m")

        # 默认开启所有规则
        # 支持指定规则，使用配置文件的方式，以下是demo
        # {
        #     "enableCheckers": {
        #         "GoFuncVisitor": {},
        #         "JavaScriptFuncVisitor": {
        #             "ignoreNestingMethods": true
        #         }
        #     }
        # }
        config = dict()
        enable_rules = dict()
        rule_list = self.params.get("rule_list", list())
        for rule in rule_list:
            # 因为有这个字段但本身就是None，所以返回None
            rule_params = rule.get("params")
            if rule_params is None:
                rule_params = ""
            if f"[{self.tool_name.lower()}]" not in rule_params:
                rule_params = f"[{self.tool_name.lower()}]\r\n" + rule_params
            rule_params_dict = ConfigReader(cfg_string=rule_params).read(self.tool_name.lower())
            enable_rules[rule["name"]] = rule_params_dict
        config["enableCheckers"] = enable_rules
        config_path = os.path.join(self.work_dir, f"{self.tool_name}_config.json")
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        options.extend(["-c", config_path])

        scan_cmd = self.get_cmd(options)

        spc = SubProcController(
            scan_cmd,
            cwd=self.tool_home,
            stdout_line_callback=subprocc_log,
            stderr_line_callback=subprocc_log,
        )
        spc.wait()
        self._close_proc(spc.pid)

        return func_output

    def get_lang_ext(self):
        """
        获得对应语言的文件后缀
        :return:
        """
        if not self.scan_languages:
            return []

        scan_cmd = self.get_cmd(
            [
                "-l",
                ",".join(self.scan_languages),
                "-le",
            ]
        )
        lang_ext_output = os.path.join(self.work_dir, "lang_ext.txt")
        # logger.info(f"scan_cmd: {' '.join(scan_cmd)}")
        spc = SubProcController(
            scan_cmd,
            stdout_line_callback=subprocc_log,
            stderr_line_callback=subprocc_log,
            stdout_filepath=lang_ext_output,
        )
        spc.wait()
        self._close_proc(spc.pid)
        fi = open(lang_ext_output, "rb")
        content = CodecClient().decode(fi.read())
        fi.close()
        return content.split(":")[-1].strip().split(",")

    def get_issue(self, output):
        if not output or not os.path.exists(output):
            return

        relpos = len(self.params.source_dir) + 1
        rules = self.params.get("rules", list())

        f = open(output, "r", encoding="utf-8")
        fieldnames = (
            "checker",
            "description",
            "path",
            "line",
            "column",
        )
        csv_f = (line for line in f if "\0" not in line)
        reader = csv.DictReader(csv_f, fieldnames)
        next(reader)
        for row in reader:
            path = row["path"][relpos:]
            line = int(row["line"])
            column = int(row["column"])
            rule = row["checker"]
            if rule not in rules:
                continue
            msg = row["description"]

            row_refs = row.get(None, [])
            refs = list()
            for ref in row_refs:
                parts = ref.split(":")
                refs.append(
                    {
                        "line": parts[2],
                        "column": parts[3],
                        "msg": parts[0],
                        "path": parts[1][relpos:],
                    }
                )
            yield {
                "rule": rule,
                "msg": msg,
                "path": path,
                "line": line,
                "column": column,
                "refs": refs,
            }

        f.close()

    def get_methods(self, output):
        if not output or not os.path.exists(output):
            return

        f = open(output, "r", encoding="utf-8")
        fieldnames = (
            "path",
            "start_line",
            "end_line",
            "func_name",
            "long_name",
            "scope",
        )
        csv_f = (line for line in f if "\0" not in line)
        reader = csv.DictReader(csv_f, fieldnames)
        next(reader)
        for row in reader:
            path = row["path"]
            start_line = int(row["start_line"])
            end_line = int(row["end_line"])
            func_name = row["func_name"]
            long_name = row["long_name"]
            scope = row["scope"]

            temp_f = open(path, "rb")
            lines = CodecClient().decode(temp_f.read()).splitlines()
            temp_f.close()
            code_line_num = len(
                CommentsManager(row["path"], "\n".join(lines[start_line - 1 : end_line - 1])).get_codes()
            )
            yield (
                code_line_num,
                path,
                start_line,
                end_line,
                self.get_parent(scope),
                func_name,
                long_name,
                scope,
            )

        f.close()

    def get_method_dict(self, source_dir=None, scan_languages=None, files=None, want_suffix=None, force_all=False):
        funcs = dict()
        func_output = self.scan(
            self.params,
            source_dir=source_dir,
            scan_languages=scan_languages,
            files=files,
            want_suffix=want_suffix,
            force_all=force_all,
        )
        if func_output:
            for row in self.get_methods(func_output):
                (code_line_num, path, start_line, end_line, func_name, long_name, scope) = row

                rel_path = path[len(source_dir) + 1 :]

                func = {
                    "code_line_num": code_line_num,
                    "start_line": start_line,
                    "end_line": end_line,
                    "class_name": self.get_parent(scope),
                    "func_name": func_name,
                    "long_name": long_name,
                    "scope": scope,
                }
                if rel_path not in funcs:
                    funcs[rel_path] = [func]
                else:
                    funcs[rel_path].append(func)
        return funcs

    def get_parent(self, scope):
        if scope.endswith("$"):
            return scope
        return scope.split(".")[-1]

    def get_ccn_infos(self, params, output, source_dir=None):
        f = open(output, "r", encoding="utf-8")
        fieldnames = (
            "path",
            "start_line",
            "end_line",
            "func_name",
            "long_name",
            "scope",
            "ccn",
        )
        reader = csv.DictReader(f, fieldnames)
        next(reader)
        for row in reader:
            path = row["path"]
            start_line = int(row["start_line"])
            end_line = int(row["end_line"])
            temp_f = open(path, "rb")
            lines = CodecClient().decode(temp_f.read()).splitlines()
            temp_f.close()
            code_line_num = len(
                CommentsManager(row["path"], "\n".join(lines[start_line - 1 : end_line - 1])).get_codes()
            )
            row["line_num"] = end_line - start_line + 1
            row["code_line_num"] = code_line_num
            row["token"] = -1
            row["func_param_num"] = -1
            yield row
        f.close()


tool = Collie

if __name__ == "__main__":
    pass
