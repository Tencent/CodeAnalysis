#!/usr/bin/env python
# -*- encoding: utf-8 -*-
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
from node.cmdarg import CmdArgParser
from tool.util.pythontool import PythonTool
from util.exceptions import ConfigError
from util.gitconfig import GitConfig
from util.logutil import LogPrinter

logger = logging.getLogger("codepuppy")


class CodePuppy(object):
    """codepuppy启动管理类
    """
    def __init__(self):
        # 命令行输入参数
        self._params = CmdArgParser.parse_args()
        # 日志输出设置
        self.__setup_logger()
        # 检查是否为python3.7版本
        if not PythonTool.is_local_python_command_available("python3", python_version="3.7"):
            raise ConfigError("python3 command(Python Version 3.7) is not available, please install first.")
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

        format_pattern = '%(asctime)s-%(levelname)s-%(name)s: %(message)s'
        logging.basicConfig(level=level, format=format_pattern)
        # 设置日志输出文件,如果文件大于10MB,自动备份,备份文件多于10个时,自动删除
        if self._params.log_file:
            handler = RotatingFileHandler(filename=self._params.log_file, maxBytes= 10 * 1024 * 1024, backupCount=10)
            formatter = logging.Formatter(format_pattern)
            handler.setFormatter(formatter)
            root_logger = logging.getLogger()
            root_logger.addHandler(handler)
        LogPrinter.info(f"Tencent Cloud Code Analysis ({settings.EDITION.name} Beta)")

    def __check_encoding(self):
        """检查默认编码,如果为空,设置为en_US.UTF-8

        :return:
        """
        # 默认编码检查
        try:
            code, encoding = locale.getdefaultlocale()
            # LogPrinter.debug('locale is %s.%s' % (code, encoding))
        except Exception as err:
            LogPrinter.error('locale.getdefaultlocale() encounter err: %s' % str(err))
            encoding = None

        if encoding is None:
            LogPrinter.warning('locale default encoding is None. LANG env may not set correctly! Set LANG env now.')
            os.environ["LC_ALL"] = "en_US.UTF-8"
            os.environ["LANG"] = "en_US.UTF-8"
            code, encoding = locale.getdefaultlocale()
            LogPrinter.info('Setting Lang env done, locale is %s.%s' % (code, encoding))

    def main(self):
        args = self._params
        LogPrinter.print_logo()

        if args.command == 'localscan':
            '''执行本地项目扫描'''
            from node.localrunner import LocalRunner
            LocalRunner(args).run()

        elif args.command == 'help':
            '''输出帮助文档'''
            CmdArgParser.print_help()

        elif args.show_help:
            CmdArgParser.print_help()

        else:
            print('输入命令有误,请输入 -h 命令查看帮助文档!')


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    CodePuppy().main()
