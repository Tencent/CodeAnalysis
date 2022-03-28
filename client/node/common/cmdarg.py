# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

""" 命令行参数解析类
"""

import argparse
import logging

from node.app import settings

logger = logging.getLogger(__name__)


class CmdArgParser(object):
    """
    命令行参数解析
    """
    @staticmethod
    def parse_args():
        """解析命令行参数

        :return:
        """
        argparser = argparse.ArgumentParser(add_help=True)
        argparser.add_argument('-v', '--version', action='version',
                               version=f"CodeAnalysis Version {settings.VERSION}({settings.EDITION.name} Beta)",
                               help="显示当前版本号")
        argparser.add_argument("-l", "--log-file", dest='log_file', help="指定log文件路径")
        subparsers = argparser.add_subparsers(dest='command', help="Commands")

        # localscan命令
        localscan_parser = subparsers.add_parser('localscan', help="执行本地项目扫描")
        localscan_parser.add_argument("-t", "--token", dest='token', type=str, help="个人Token,在代码分析网站获取")
        localscan_parser.add_argument("--org-sid", dest="org_sid", help="团队编号,在代码分析网站获取")
        localscan_parser.add_argument("--team-name", dest="team_name", help="项目名称,在代码分析网站获取")
        localscan_parser.add_argument("-s", "--source-dir", dest="source_dir", type=str, help="本地代码目录")
        localscan_parser.add_argument("--total", dest="total_scan", action="store_true",
                                      help="指定本次为全量扫描,不指定该参数时默认为增量扫描")
        localscan_parser.add_argument("--language", dest="language", type=str, help="代码语言类型,可以指定多门语言,用英文逗号(,)分隔")
        localscan_parser.add_argument("--scan-plan", dest="scan_plan", type=str,
                                      help="扫描方案名称,如果当前代码库已存在该名称的方案,直接使用;否则会新建该名称的方案")
        localscan_parser.add_argument("--ref-scheme-id", dest="ref_scheme_id", type=int,
                                      help="参照扫描方案ID,新建项目时复制指定ID的扫描方案使用,达到多个代码仓库使用相同的扫描方案的效果")
        localscan_parser.add_argument("--branch", dest="branch", type=str, help="指定本地扫描的git代码库分支名称")
        localscan_parser.add_argument("--exclude", dest="exclude_paths", type=str,
                                      help="需要过滤的目录或文件(相对路径),多个路径用英文逗号(,)分隔,路径格式遵循python fnmatch语法")
        localscan_parser.add_argument("--include", dest="include_paths", type=str,
                                      help="指定只扫描的目录或文件(相对路径),多个路径用英文逗号(,)分隔,路径格式遵循python fnmatch语法")
        localscan_parser.add_argument("--pre-cmd", dest="pre_cmd", type=str, help="前置命令(需要前置操作时使用)")
        localscan_parser.add_argument("--build-cmd", dest="build_cmd", type=str, help="编译命令(扫描编译型语言时使用)")
        localscan_parser.add_argument("--username", dest="username", type=str, help="代码库用户名")
        localscan_parser.add_argument("--password", dest="password", type=str, help="代码库密码")
        localscan_parser.add_argument("--ssh", dest="ssh_file", type=str, help="ssh私钥文件路径")
        localscan_parser.add_argument("-c", "--config-file", dest='config_file', type=str, help="项目配置文件")
        localscan_parser.add_argument("--report", dest="report_file", type=str,
                                      help="指定输出扫描结果简报的文件路径(json格式),默认输出在软件工作目录下的scan_status.json文件")
        localscan_parser.add_argument("--server", dest="server_url", type=str, help="指定连接的服务器url")
        localscan_parser.add_argument("--start-type", dest='start_type', type=str, help="启动方式,可选值：CI，分别表示CI场景")

        # updatetool命令
        updatetool_parser = subparsers.add_parser('updatetool', help="拉取工具")
        updatetool_parser.add_argument('-t', "--tool", dest='tool', type=str, help="更新指定工具,可以指定多个工具,用英文逗号(,)分隔")
        updatetool_parser.add_argument('-a', '--all', dest='all_tools', action="store_true", help="更新全量工具")
        updatetool_parser.add_argument("--os", dest='os_type', type=str, choices=['mac', 'linux', 'windows'],
                                       help="拉取指定操作系统下的工具")

        # start命令
        start_parser = subparsers.add_parser('start', help="启动节点")
        start_parser.add_argument("-t", "--token", dest='token', type=str, help="个人token,在代码分析网站获取", required=True)

        # help
        subparsers.add_parser('help', help="显示帮助文档")

        return argparser.parse_args()

    @staticmethod
    def print_help():
        """
        输出帮助文档
        :return:
        """
        cnt = 50
        print("")
        print("-" * cnt)
        print("欢迎使用 Tencent Cloud Code Analysis - 腾讯云代码分析")
        print("-" * cnt)
        print("")

        print("执行代码分析命令: localscan")
        print("-" * cnt)
        print("1. 使用配置文件启动")
        print("(1) 填写默认配置文件codedog.ini(必填字段：token、source_dir)")
        print("(2) python3 codepuppy.py localscan")
        print("2. 纯命令行启动")
        print("python3 codepuppy.py localscan -t <个人token> -s <本地代码目录>")
        print("")

        print("查看帮助信息")
        print("-"*cnt)
        print("help                  显示当前帮助信息")
        print("<command> -h,--help   显示子命令帮助信息")
        print("")
