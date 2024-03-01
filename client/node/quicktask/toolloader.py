# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""拉取quickscan工具
"""

from node.localtask.localconfig import LocalConfig
from node.toolloader.loadtool import ToolLoader, ToolConfigLoader
from node.quicktask.configloader import QuickScanConfigLoader
from node.quicktask.quickscan import QuickScan
from node.common.userinput import UserInput
from util import errcode
from util.api.dogserver import RetryDogServer
from util.textutil import StringMgr
from util.logutil import LogPrinter
from util.exceptions import NodeError


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
        if args.scheme_template_id:
            if args.token and args.org_sid:  # 通过server获取指定的分析方案模板的任务参数
                LogPrinter.info(f"token and scheme_template_id are set, get task config from server ...")
                server_url = LocalConfig.get_server_url()
                dog_server = RetryDogServer(server_url, args.token).get_api_server(retry_times=2)
                proj_conf = dog_server.get_jobconfs_by_scheme_template(args.scheme_template_id, args.org_sid)
                tool_tasks = proj_conf["tasks"]
            else:
                raise NodeError(code=errcode.E_NODE_TASK_CONFIG, msg="已输入scheme_template_id, "
                                                                     "但缺少--token和--org-sid参数, "
                                                                     "无法获取到分析方案模板, 请补充参数!")
        else:
            tool_tasks = QuickScan.get_scan_tasks(languages, labels, {})
        tool_names = [task['task_name'] for task in tool_tasks]

        custom_tools = []
        for tool_name in tool_names:
            try:
                __import__("tool." + tool_name)
            except ModuleNotFoundError:
                # 记录自定义工具列表
                custom_tools.append(tool_name)
            except:
                LogPrinter.exception("encounter error.")
                pass

        LogPrinter.info("Initing other tools ...")
        ToolLoader(tool_names=tool_names, task_list=tool_tasks, custom_tools=custom_tools, include_common=False).git_load_tools(print_enable=False)


if __name__ == '__main__':
    pass
