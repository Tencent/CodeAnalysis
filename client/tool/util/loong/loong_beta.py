#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================


import os
import sys
import json

from node.app import settings
from task.basic.common import subprocc_log
from util.subprocc import SubProcController
from util.logutil import LogPrinter


logger = LogPrinter


class Loong(object):
    def __init__(
        self,
        dbdir: str,
        project_root: str,
        jar_mode: bool = False,
    ):
        self.dbdir = dbdir
        self.project_root = project_root
        self.jar_mode = jar_mode

        self.tool_home = os.environ.get("LOONG_BETA_HOME", "")

    def parse(self):
        cmds = self.get_cmd("APIFinder2", [
            "path=%s" % self.project_root,
            "useapi=true",
            "out=%s" % os.path.join(self.dbdir, "codedog_bc.db"),
        ])
        SubProcController(
            cmds,
            stdout_line_callback=subprocc_log,
            stderr_line_callback=subprocc_log,
        ).wait()

    def scan(self) -> list:
        options = [
            "--dbdir",
            self.dbdir,
            "--project_root",
            self.project_root,
        ]
        if self.jar_mode:
            options.append("--jar_mode")
        cmds = self.get_cmd("Loong", options)
        spc = SubProcController(
            cmds,
            stdout_line_callback=subprocc_log,
            stderr_line_callback=subprocc_log,
        )
        spc.wait()

        output_path = os.path.join(self.dbdir, "result.json")
        f = open(output_path)
        result = json.load(f)
        f.close()
        if not result:
            result = []
        return result

    def get_cmd(self, tool_name: str, options: list) -> list:
        tool_path = os.path.join(self.tool_home, "bin", settings.PLATFORMS[sys.platform], tool_name)
        if settings.PLATFORMS[sys.platform] == "windows":
            tool_path = f"{tool_path}.exe"
        cmds = [tool_path]
        cmds.extend(options)
        return cmds


tool = Loong


if __name__ == "__main__":
    pass
