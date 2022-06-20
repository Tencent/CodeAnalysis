# -*- encoding: utf-8 -*-
# Copyright (c) 2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""拉取quickscan工具
"""

from node.toolloader.loadtool import ToolLoader, ToolConfigLoader
from node.quicktask.configloader import QuickScanConfigLoader
from node.quicktask.quickscan import QuickScan
from node.common.userinput import UserInput
from util.textutil import StringMgr
from util.logutil import LogPrinter


class QuickScanToolLoader(object):
    @staticmethod
    def load_tools(args):
        if args.language:
            languages = UserInput().format_languages(args.language)
        else:
            languages = []

        # 拉取quick scan配置库
        QuickScanConfigLoader.load_config()

        if args.label:
            labels = StringMgr.str_to_list(args.label)
        else:
            labels = []

        # 从git拉取工具配置库
        ToolConfigLoader().load_tool_config()
        # LogPrinter.info(f"---> labels: {labels}")
        tool_tasks = QuickScan.get_scan_tasks(languages, labels, {})
        tool_names = [task['task_name'] for task in tool_tasks]
        LogPrinter.info(f"Initing other tools: {tool_names}")
        ToolLoader(tool_names=tool_names, task_list=tool_tasks, include_common=False).git_load_tools(print_enable=False)


if __name__ == '__main__':
    pass
