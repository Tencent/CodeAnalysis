#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================


import os
import sys
from multiprocessing import cpu_count

from node.app import settings
from util.subprocc import SubProcController
from task.basic.common import subprocc_log
from task.authcheck.check_license import __lu__
from util.logutil import LogPrinter


logger = LogPrinter


class ASTParser(object):
    def __init__(self, source_dir, db_dir=None):
        self.project_root = source_dir
        if db_dir and os.path.exists(db_dir):
            if os.path.isdir(db_dir):
                self.ast_db = os.path.join(db_dir, "codedog_ast.db")
            else:
                self.ast_db = db_dir
        else:
            self.ast_db = os.path.join(source_dir, "codedog_ast.db")
        self.want_suffix = (".java", ".jar")

    def get_tool(self):
        tool_home = os.environ["LOONG_HOME"]
        tool_path = os.path.join(tool_home, "bin", settings.PLATFORMS[sys.platform], "JAP")
        if settings.PLATFORMS[sys.platform] == "windows":
            tool_path = f"{tool_path}.exe"
        return tool_path

    def parser(self):
        tool_path = self.get_tool()
        args = [
            "path=%s" % self.project_root,
            "thread=%s" % cpu_count(),
            "data=%s" % self.ast_db,
        ]
        astparser_cmd = __lu__().format_cmd(tool_path, args)
        SubProcController(astparser_cmd, stdout_line_callback=subprocc_log, stderr_line_callback=subprocc_log).wait()


if __name__ == "__main__":
    pass
