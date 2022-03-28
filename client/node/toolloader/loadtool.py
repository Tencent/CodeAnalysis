# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
工具加载管理类
"""

import os
import time

from tqdm import tqdm

from node.app import settings
from node.toolloader.gitload import GitLoader
from node.toolloader.loadconfig import ConfigLoader
from util.envset import EnvSet
from util.exceptions import ConfigError
from util.pathlib import PathMgr
from util.logutil import LogPrinter


class ToolCommonLoader(object):
    @staticmethod
    def load_tool_type(tool_dirpath, tool_dirname):
        """
        判断使用哪种方式加载工具
        :param tool_dirpath: 工具目录绝对路径
        :param tool_dirname: 工具目录名
        :param is_custom_tool: 是否自定义工具
        :return:
        """
        if settings.USE_LOCAL_TOOL == "True":
            if os.path.exists(tool_dirpath):
                LogPrinter.info(f"USE_LOCAL_TOOL=True, use local tool dir: {tool_dirpath}")
                return "Local", None
            else:
                raise ConfigError(f"USE_LOCAL_TOOL=True, but local tool dir ({tool_dirpath}) not exists, please check!")
        else:
            copy_tools_src_dir = os.environ.get("COPY_TOOLS_FROM")
            if copy_tools_src_dir and os.path.exists(copy_tools_src_dir):
                if os.path.exists(tool_dirpath):  # 目录存在，不拷贝，直接使用
                    # LogPrinter.info(f"{tool_dirpath} exists, skip copy.")
                    return "Local", None
                else:
                    tool_dirpath_copy_from = os.path.join(copy_tools_src_dir, tool_dirname)
                    if os.path.exists(tool_dirpath_copy_from):
                        return "Copy", tool_dirpath_copy_from
                    else:  # 拷贝源目录不存在，从git拉取
                        return "Git", None
            else:
                return "Git", None

    @staticmethod
    def load_tool(load_type, tool_dirpath, tool_dirpath_copy_from, git_url, scm_auth_info=None, print_enable=False):
        """

        :param load_type:
        :param tool_dirpath:
        :param tool_dirpath_copy_from:
        :param git_url:
        :param scm_auth_info:
        :param print_enable:
        :return:
        """
        if load_type == "Local":
            if print_enable:
                LogPrinter.info(f"Use local tool dir: {tool_dirpath}")
            return tool_dirpath
        elif load_type == "Copy":
            if print_enable:
                LogPrinter.info(f"Copy from {tool_dirpath_copy_from} to {tool_dirpath}")
            PathMgr().retry_copy(tool_dirpath_copy_from, tool_dirpath)
            return tool_dirpath
        else:
            if print_enable:
                LogPrinter.info(f"Load from git to {tool_dirpath} ...")
            # print_enable不能设置为True,否则会覆盖掉logging输出的日志
            GitLoader(scm_url=git_url, dest_dir=tool_dirpath, scm_auth_info=scm_auth_info, print_enable=False).load()
            return tool_dirpath


class LoadToolProcess(object):
    def __init__(self):
        """
        :param error_list: 收集子线程异常，返回给主线程
        """
        self._process_bar = None

    def __load_tool(self, tool_info):
        # LogPrinter.info("初始化工具: %s" % tool_info["tool_dirname"])
        ToolCommonLoader.load_tool(tool_info["load_type"], tool_info["tool_dirpath"],
                                   tool_info["copy_from"], tool_info["git_url"],
                                   scm_auth_info=tool_info.get("auth_info"))

        # 更新进度条
        self._process_bar.update(1)

    def run(self, tool_lists):
        tool_name_list = [info["tool_dirname"] for info in tool_lists]
        tools_count = len(tool_name_list)
        # LogPrinter.info("Initialize tools: %s" % ", ".join(tool_name_list))
        LogPrinter.info(f"Initing {tools_count} tools, please wait a minute ...")

        self._process_bar = tqdm(total=tools_count, desc="[Tools init]", ncols=100)
        for tool_info in tool_lists:
            self.__load_tool(tool_info)
        self._process_bar.close()


class ToolLoader(object):
    """工具拉取管理类"""

    def __init__(self, tool_names=None, os_type=None, task_list=None):
        """
        构造函数
        :param tool_names: <list> 工具名列表，可以指定单个或多个工具；默认为空，表示全量工具
        :param os_type: <str> 操作系统，可以指定拉取某个OS（忽略当前机器环境所处OS）的工具
        :param task_list: <list> 任务参数的列表，可以包含单个或多个工具任务
        :return:
        """
        # 读取工具配置信息
        self.__tool_config = ConfigLoader(os_type=os_type).read_tool_config(tool_names=tool_names, task_list=task_list)

    def git_load_tools(self, print_enable):
        """
        按需拉取|更新内置工具库（自定义工具不通过该方法拉取）
        :param print_enable: 是否打印拉取过程
        :param tool_names:
        :return:
        """
        # 拉取工具
        tool_url_info = {}
        for tool_name, tool_info in self.__tool_config.items():
            if tool_info["tool_url"]:
                tool_url = tool_info["tool_url"]
                if isinstance(tool_url, list):
                    for url in tool_url:
                        tool_url_info[url] = tool_info
                else:
                    tool_url_info[tool_url] = tool_info
        # LogPrinter.info(f">>>>>type:{type(tool_url_info)}\n tool_url_info: {tool_url_info}")
        # import json
        # LogPrinter.info(">>> 工具配置: %s" % json.dumps(self.__tool_config, indent=1))

        # LogPrinter.info("开始更新工具...")
        load_tool_list = []
        for git_url, tool_info in tool_url_info.items():
            tool_dirname = git_url.split('/')[-1].strip().replace(".git", "")
            tool_dirpath = os.path.join(settings.TOOL_BASE_DIR, tool_dirname)

            load_type, dirpath_copy_from = ToolCommonLoader.load_tool_type(tool_dirpath, tool_dirname)
            # 如果设置了不自动拉工具，且工具目录存在，跳过

            load_tool_list.append({
                "load_type": load_type,
                "git_url": git_url,
                "tool_dirname": tool_dirname,
                "tool_dirpath": tool_dirpath,
                "copy_from": dirpath_copy_from,
                "print_enable": print_enable,
                "auth_info": tool_info.get("`auth_info`")
            })

        if load_tool_list:
            start_time = time.time()
            LoadToolProcess().run(load_tool_list)
            LogPrinter.info(f"Initialize tools done.(use time: {format(time.time() - start_time, '.2f')}s)")

    def set_tool_env(self):
        """
        加载工具所需的环境变量
        :return:
        """
        EnvSet().set_tool_env(self.__tool_config)


class ToolConfigLoader(object):
    def __init__(self):
        self._tool_config_dir_name = settings.TOOL_CONFIG_URL.split('/')[-1].strip().replace(".git", "")
        self._tool_config_dir = os.path.join(settings.TOOL_BASE_DIR, self._tool_config_dir_name)

    def load_tool_config(self):
        """
        拉取|更新工具配置文件
        :return:
        """
        load_type, dirpath_copy_from = ToolCommonLoader.load_tool_type(self._tool_config_dir,
                                                                       self._tool_config_dir_name)
        ToolCommonLoader.load_tool(load_type, self._tool_config_dir, dirpath_copy_from, settings.TOOL_CONFIG_URL)
