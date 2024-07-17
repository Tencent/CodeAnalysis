#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
luacheck: static analysis for Lua.
"""

import sys
import os
import threading

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
from util.scanlang.callback_queue import CallbackQueue

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
        LUACHECK_HOME = os.environ.get("LUACHECK_HOME")
        pos = len(source_dir) + 1
        path_mgr = PathMgr()
        want_suffix = ".lua"
        issues = []
        # update_task_progress(request, 'LuaCheck工具开始分析', 40)
        # luacheck在win下支持分析目录，在mac和linux下需要安装luafilesystem才能支持分析目录.暂不使用 --cache
        # 1. --read-globals coroutine._yield 是为了消除luacheck对coroutine._yield的误报，详细如下：
        # IIRC coroutine._yield is ngx_lua specific and not documented.
        # Can use read_globals option to silence the warning: add read_globals = {"coroutine._yield"} to config (.luacheckrc),
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
            "--std",
            "max",
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
            error_output = os.path.join(work_dir, "luacheck_result.xml")
            issues.extend(LuaCheckRunner().run_luacheck(scan_cmd, error_output, pos, rules))
        else:
            # 单文件分析
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
            toscans = FilterPathUtil(params).get_include_files(toscans, pos)
            if not toscans:
                logger.debug("To-be-scanned files is empty ")
                return []
            # 在文件前后加上双引号，变成字符串，防止文件路径中有特殊字符比如(，luacheck无法分析
            toscans = [self.handle_path_with_space(path) for path in toscans]
            # 多线程分析
            issues = ThreadRunner(scan_cmd, work_dir, pos, rules).run(toscans)
        logger.info(issues)
        return issues

    def handle_path_with_space(self, path):
        """
        处理文件路径中包含特殊字符比如(的情况
        :param path:
        :return:
        """
        return '"' + path + '"'

class LuaCheckRunner(object):
    def __init__(self):
        pass

    def run_luacheck(self, scan_cmd, error_output, pos, rules):
        """
        执行luacheck并处理结果
        """
        SubProcController(scan_cmd, stdout_filepath=error_output, stderr_line_callback=logger.info).wait()
        if sys.platform == "win32":
            xmlContent = open(error_output, "r", encoding="gbk").read()
            open(error_output, "w", encoding="utf-8").write(xmlContent)
        raw_warning = ET.ElementTree(file=error_output)
        issues = []
        for file in raw_warning.iter(tag="testcase"):
            # tag, attrib
            path = file.attrib.get("classname")
            for error in file.findall("failure"):
                rule = error.attrib.get("type")
                if rules and rule not in rules:
                    continue
                # 2024/4/18 移除msg中的行列号信息
                message = error.attrib.get("message")
                if message is None or not message.startswith(path):
                    continue
                message = message[len(path)+1:]
                infos = message.split(":", 2)
                # msg中 on line 后面也会跟着行号
                msg = infos[2].split("on line ")[0].strip()
                line = int(infos[0])
                column = int(infos[1])
                issues.append({"path": path[pos:], "rule": rule, "msg": msg, "line": line, "column": column})
        return issues


class ThreadRunner(object):
    # 多线程执行 luacheck 类
    def __init__(self, scan_cmd, work_dir, pos, rules):
        self.scan_cmd = scan_cmd
        self.work_dir = work_dir
        self.issues = []
        self.pos = pos
        self.rules = rules
        self.mutex = threading.Lock()  # 线程锁

    def __run_luacheck_on_file(self, index, file_path):
        scan_cmd = self.scan_cmd.copy()
        scan_cmd.append(file_path)
        scan_cmd = PathMgr().format_cmd_arg_list(scan_cmd)
        error_output = os.path.join(self.work_dir, str(index) + "luacheck_result.xml")
        return LuaCheckRunner().run_luacheck(scan_cmd, error_output, self.pos, self.rules)

    def __scan_file_callback_(self, index, file_path):
        file_result = self.__run_luacheck_on_file(index, file_path)
        self.mutex.acquire()  # 上锁
        self.issues.extend(file_result)
        self.mutex.release()  # 解锁

    def run(self, toscans):
        # 多线程执行类
        callback_queue = CallbackQueue(min_threads=20, max_threads=1000)
        for index, path in enumerate(toscans):
            LogPrinter.info("path: %s" % path)
            callback_queue.append(self.__scan_file_callback_, index, path)
        callback_queue.wait_for_all_callbacks_to_be_execute_and_destroy()
        return self.issues


tool = Luacheck

if __name__ == "__main__":
    pass
