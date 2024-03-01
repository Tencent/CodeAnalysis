# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================


import os
import sys

from util.subprocc import SubProcController
from util.envset import EnvSet
from util.logutil import LogPrinter
from node.app import settings
from task.authcheck.check_license import __lu__
from task.basic.common import subprocc_log

logger = LogPrinter


class Compass(object):
    def __init__(self, params):
        self.tool_home = os.environ.get("COMPASS_HOME")
        self.tool_name = self.__class__.__name__
        self.params = params

    def scan(self, source_dir=None, task_request=None, args=None) -> str:
        # 2022/11/25 参数不能使用可变类型变量作为默认值，比如[] {}等，每次调用都会指向同一个指针
        if args is None:
            args = []

        source_dir = source_dir if source_dir else self.params["source_dir"]
        task_dir = os.path.dirname(os.getcwd())
        os.environ["SOURCE_DIR"] = source_dir
        request_file = os.path.abspath(os.path.join(task_dir, "task_request.json"))
        os.environ["TASK_REQUEST"] = task_request if task_request else request_file
        tool_cmd = self.get_cmd(args)
        work_dir = os.getcwd()

        sp = SubProcController(
            command=tool_cmd,
            cwd=work_dir,
            stdout_line_callback=subprocc_log,
            stderr_line_callback=subprocc_log,
            env=EnvSet().get_origin_env(),
        )
        sp.wait()
        return os.path.join(work_dir, "result.json")

    def get_cmd(self, args):
        tool_path = os.path.join(self.tool_home, "bin", settings.PLATFORMS[sys.platform], self.tool_name)
        if settings.PLATFORMS[sys.platform] == "windows":
            tool_path = f"{tool_path}.exe"
        return __lu__().format_cmd(tool_path, args)


tool = Compass

if __name__ == "__main__":
    pass
