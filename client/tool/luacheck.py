#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2023 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
luacheck: static analysis for Lua.
"""

import sys
import os

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from task.scmmgr import SCMMgr
from util.pathlib import PathMgr
from task.codelintmodel import CodeLintModel
from util.subprocc import SubProcController
from util.pathfilter import FilterPathUtil
from util.logutil import LogPrinter

logger = LogPrinter


class Luacheck(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        pass

    def analyze(self, params):
        source_dir = params.source_dir
        work_dir = os.getcwd()
        rules = params.get("rules", [])
        incr_scan = params["incr_scan"]
        path_exclude = params.path_filters.get("wildcard_exclusion", [])
        path_include = params.path_filters.get("wildcard_inclusion", [])
        error_output = os.path.join(work_dir, "luacheck_result.xml")
        LUACHECK_HOME = os.environ.get("LUACHECK_HOME")
        pos = len(source_dir) + 1
        path_mgr = PathMgr()
        want_suffix = ".lua"

        # update_task_progress(request, 'LuaCheck工具开始扫描', 40)
        # luacheck在win下支持扫描目录，在mac和linux下需要安装luafilesystem才能支持扫描目录.暂不使用 --cache
        # 1. --read-globals coroutine._yield 是为了消除luacheck对coroutine._yield的误报，详细如下：
        # IIRC coroutine._yield is ngx_lua specific and not documented.
        # Can use read_globals option to silence the warning: 
        # add read_globals = {"coroutine._yield"} to config (.luacheckrc),
        # or pass --read-globals coroutine._yield on the command line,
        # or put -- luacheck: read globals coroutine._yield before the line with the warning.
        # 2. --std max 设置各版本Lua标准全局变量，比如ngx, module()
        # 3. --ignore 212/self 设置忽略掉UnusedArgument规则识别self参数
        # scan_cmd = "luacheck --formatter JUnit --codes --ignore 212/self --read-globals coroutine._yield --std max "
        scan_cmd = [
            "luacheck",
            "--formatter",
            "JUnit",
            "--codes",
            "--ignore",
            "212/self",
            "--read-globals",
            "coroutine._yield",
            "--std max",
        ]
        if sys.platform == "win32":
            scan_cmd.append(source_dir)

            # 过滤
            if path_include:
                scan_cmd.append("--include-files")
                for path in path_include:
                    scan_cmd.append(os.path.join(source_dir, path))
            if path_exclude:
                scan_cmd.append("--exclude-files")
                for path in path_exclude:
                    scan_cmd.append(os.path.join(source_dir, path))
        else:
            toscans = []
            if incr_scan:
                diffs = SCMMgr(params).get_scm_diff()
                toscans = [
                    os.path.join(source_dir, diff.path)
                    for diff in diffs
                    if diff.path.endswith(want_suffix) and diff.state != "del"
                ]
            else:
                toscans = path_mgr.get_dir_files(source_dir, want_suffix)
            # filter include and exclude path
            relpos = len(source_dir) + 1
            toscans = FilterPathUtil(params).get_include_files(toscans, relpos)
            if not toscans:
                logger.debug("To-be-scanned files is empty ")
                return []
            # 在文件前后加上双引号，变成字符串，防止文件路径中有特殊字符比如(，luacheck无法扫描
            toscans = [self.handle_path_with_space(path) for path in toscans]
            scan_cmd.extend(toscans)

        SubProcController(scan_cmd, stdout_filepath=error_output).wait()

        # update_task_progress(request, '扫描结果处理', 60)
        if sys.platform == "win32":
            xmlContent = open(error_output, "r", encoding="gbk").read()
            open(error_output, "w", encoding="utf-8").write(xmlContent)
        raw_warning = ET.ElementTree(file=error_output)
        issues = []
        for file in raw_warning.iter(tag="testcase"):
            # tag, attrib
            path = file.attrib.get("classname")[pos:]
            for error in file.findall("failure"):
                rule = error.attrib.get("type")
                if rules and rule not in rules:
                    continue
                msg = error.attrib.get("message")[pos:]
                line = int(msg.split(":")[1])
                column = int(msg.split(":")[2])
                issues.append({"path": path, "rule": rule, "msg": msg, "line": line, "column": column})
        logger.debug(issues)
        return issues

    def handle_path_with_space(self, path):
        """
        处理文件路径中包含特殊字符比如(的情况
        :param path:
        :return:
        """
        return '"' + path + '"'


tool = Luacheck

if __name__ == "__main__":
    pass
