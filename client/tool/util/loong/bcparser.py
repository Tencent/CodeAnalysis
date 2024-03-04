#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================


import os
import sys

from node.app import settings
from util.subprocc import SubProcController, ProcessExecuteTimeoutError
from task.basic.common import subprocc_log
from task.authcheck.check_license import __lu__
from util.logutil import LogPrinter


logger = LogPrinter


class ByteCodeParser(object):
    def __init__(self, source_dir, db_dir=None):
        self.project_root = source_dir
        if db_dir and os.path.exists(db_dir):
            if os.path.isdir(db_dir):
                self.bc_db = os.path.join(db_dir, "codedog_bc.db")
            else:
                self.bc_db = db_dir
        else:
            self.bc_db = os.path.join(source_dir, "codedog_bc.db")

    def get_tool(self):
        tool_home = os.environ["LOONG_HOME"]
        tool_path = os.path.join(tool_home, "bin", settings.PLATFORMS[sys.platform], "APIFinder2")
        if settings.PLATFORMS[sys.platform] == "windows":
            tool_path = f"{tool_path}.exe"
        return tool_path

    def parser(self, need_field=False):
        tool_path = self.get_tool()
        args = [
            "path=%s" % self.project_root,
            "useapi=true",
            "out=%s" % self.bc_db,
        ]
        if need_field:
            logger.info("use field mode parser.")
            args.append("field=true")
        apifinder_cmd = __lu__().format_cmd(tool_path, args)

        try:
            spc = SubProcController(apifinder_cmd, stdout_line_callback=subprocc_log, stderr_line_callback=subprocc_log)
            if need_field:
                spc.wait(60 * 60)
            else:
                spc.wait(20 * 60)
        except ProcessExecuteTimeoutError:
            logger.info("apifinder timeout.")


if __name__ == "__main__":
    pass
