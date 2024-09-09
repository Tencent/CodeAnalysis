#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""程序主入口。在命令行中执行： python codepuppy.py -h， 查看命令帮助。
"""

import io
import locale
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from node import app
from node.app import settings
from node.common.cmdarg import CmdArgParser
from node.toolloader.loadtool import ToolLoader, ToolConfigLoader
from node.common.printversion import VersionPrinter
from util.gitconfig import GitConfig
from util.logutil import LogPrinter
from util.textutil import StringMgr

logger = logging.getLogger("codepuppy")


class CodePuppy(object):
    """codepuppy启动管理类
    """
    def __init__(self):
        # 命令行输入参数
        self._params = CmdArgParser.parse_args()
        # 日志输出设置
        self.__setup_logger()

        # 打印版本信息
        VersionPrinter.print_client_version()
        # 检查python版本
        VersionPrinter.check_python_version()

        # 运行环境默认编码检查
        self.__check_encoding()

        # 默认git配置
        GitConfig.set_default_config()

    def __setup_logger(self):
        """日志打印配置

        :param params:命令行参数
        :return:
        """
        # 设置日志级别和格式
        if app.settings.DEBUG:
            level = logging.DEBUG
        else:
            level = logging.INFO

        format_pattern = '%(asctime)s-%(levelname)s: %(message)s'
        logging.basicConfig(level=level, format=format_pattern)
        # 设置日志输出文件,如果文件大于10MB,自动备份,备份文件多于10个时,自动删除
        if self._params.log_file:
            handler = RotatingFileHandler(filename=self._params.log_file, maxBytes= 10 * 1024 * 1024, backupCount=10)
            formatter = logging.Formatter(format_pattern)
            handler.setFormatter(formatter)
            root_logger = logging.getLogger()
            root_logger.addHandler(handler)

    def __check_encoding(self):
        """检查默认编码,如果为空,设置为en_US.UTF-8

        :return:
        """
        # 默认编码检查
        try:
            code, encoding = locale.getdefaultlocale()
            # LogPrinter.debug('locale is %s.%s' % (code, encoding))
        except Exception as err:
            LogPrinter.warning('locale.getdefaultlocale() encounter err: %s' % str(err))
            encoding = None

        if encoding is None:
            LogPrinter.warning('locale default encoding is None. LANG env may not set correctly! Set LANG env now.')
            os.environ["LC_ALL"] = "en_US.UTF-8"
            os.environ["LANG"] = "en_US.UTF-8"
            code, encoding = locale.getdefaultlocale()
            LogPrinter.info('Setting Lang env done, locale is %s.%s' % (code, encoding))

    def main(self):
        args = self._params

        if args.command == 'localscan':
            '''执行本地项目扫描'''
            from node.localtask.localrunner import LocalRunner
            LocalRunner(args).run()

        elif args.command == 'start':
            '''启动任务执行端,持续获取并执行任务'''
            from node.servertask.looprunner import LoopRunner
            if args.token:
                LoopRunner(args).run()
            else:
                LogPrinter.error("缺少token参数,请通过-t <token>启动start命令.")

        elif args.command == 'quickinit':
            '''快速分析初始化工具'''
            from node.quicktask.toolloader import QuickScanToolLoader
            QuickScanToolLoader.load_tools(args)

        elif args.command == 'quickscan':
            from node.quicktask.quickrunner import QuickRunner
            QuickRunner(args).run()

        elif args.command == 'task':
            '''执行单个工具任务'''
            from node.testrunner import TestRunner
            if args.request_file:
                TestRunner(args.request_file).run()
            else:
                LogPrinter.error("请输入request.json文件, 输入 -h 查看帮助文档.")

        elif args.command == 'updatetool':
            '''更新工具库'''
            # 从git拉取工具配置库
            ToolConfigLoader().load_tool_config()
            if args.tool:  # 更新指定工具
                tool_name_list = StringMgr.str_to_list(args.tool)
                ToolLoader(tool_names=tool_name_list, os_type=args.os_type, include_common=False).git_load_tools(print_enable=False)
            elif args.all_tools:  # 更新全量工具
                ToolLoader(os_type=args.os_type, config_all_tools=True, include_common=False).git_load_tools(print_enable=False)
            else:
                LogPrinter.error("请输入必要的参数(-a|-t)! 输入 -h 查看帮助文档.")

        elif args.command == 'help':
            '''输出帮助文档'''
            CmdArgParser.print_help()

        else:
            CmdArgParser.print_help()


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    CodePuppy().main()
