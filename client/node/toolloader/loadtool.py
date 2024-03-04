# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
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
from node.toolloader.loadconfig import ConfigLoader, ToolConfig, LoadToolTypes
from node.toolloader.httploadtool import HttpToolLoader
from util.envset import EnvSet
from util.scanlang.callback_queue import CallbackQueue
from util.pathlib import PathMgr
from util.logutil import LogPrinter
from util.scmurlmgr import BaseScmUrlMgr
from util.subprocc import SubProcController
from util.textutil import ZIP_EXT


class ToolCommonLoader(object):
    @staticmethod
    def is_zip_url(tool_url):
        """判断是否是压缩包地址"""
        if tool_url.lower().endswith(ZIP_EXT):
            return True
        else:
            return False
    @staticmethod
    def load_tool_type(tool_dirpath, tool_dirname, tool_url=None):
        """
        判断使用哪种方式加载工具
        :param tool_dirpath: 工具目录绝对路径
        :param tool_dirname: 工具目录名
        :param tool_url: 工具下载地址
        :return:
        """
        if settings.USE_LOCAL_TOOL == "True":
            if os.path.exists(tool_dirpath):
                LogPrinter.info(f"USE_LOCAL_TOOL=True, use local tool dir: {tool_dirpath}")
                return "Local", None
            elif tool_url and ToolCommonLoader.is_zip_url(tool_url):
                return "HTTP", None
            else:
                return "Git", None
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
            elif tool_url and ToolCommonLoader.is_zip_url(tool_url):
                return "HTTP", None
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
        if settings.DEBUG:
            print_enable = True
        if load_type == "Local":
            if print_enable:
                LogPrinter.info(f"Use local tool dir: {tool_dirpath}")
            return tool_dirpath
        elif load_type == "Copy":
            if print_enable:
                LogPrinter.info(f"Copy from {tool_dirpath_copy_from} to {tool_dirpath}")
            PathMgr().retry_copy(tool_dirpath_copy_from, tool_dirpath)
            return tool_dirpath
        elif load_type == "HTTP":
            if print_enable:
                LogPrinter.info(f"Load from {git_url} to {tool_dirpath}")
            HttpToolLoader.download_tool(git_url, tool_dirpath)
            return tool_dirpath
        else:
            if print_enable:
                LogPrinter.info(f"Load from git to {tool_dirpath} ...")
            # print_enable不能设置为True,否则会覆盖掉logging输出的日志
            GitLoader(scm_url=git_url, dest_dir=tool_dirpath, scm_auth_info=scm_auth_info, print_enable=False).load()
            return tool_dirpath


class ThreadRunner(object):
    """多线程拉取工具"""

    def __init__(self):
        """
        :param error_list: 收集子线程异常，返回给主线程
        """
        self._error_list = []
        self._process_bar = None

    def __load_tool_callback__(self, tool_info):
        # LogPrinter.info("初始化工具: %s" % tool_info["tool_dirname"])
        try:
            ToolCommonLoader.load_tool(tool_info["load_type"], tool_info["tool_dirpath"],
                                       tool_info["copy_from"], tool_info["git_url"],
                                       scm_auth_info=tool_info.get("auth_info"))
        except Exception as err:
            LogPrinter.error(f"load tool err: {str(err)}")
            self._error_list.append(err)

        # 更新进度条
        self._process_bar.update(1)

    def run(self, tool_lists):
        tool_name_list = [info["tool_dirname"] for info in tool_lists]
        tools_count = len(tool_name_list)
        # LogPrinter.info("Initialize tools: %s" % ", ".join(tool_name_list))
        LogPrinter.info(f"Initing {tools_count} tools, please wait a minute ...")

        self._process_bar = tqdm(total=tools_count, desc="[Tools init]", ncols=100)

        min_t = 20
        max_t = 1000
        callback_queue = CallbackQueue(min_threads=min_t, max_threads=max_t)
        for tool_info in tool_lists:
            callback_queue.append(self.__load_tool_callback__, tool_info)
        callback_queue.wait_for_all_callbacks_to_be_execute_and_destroy()
        self._process_bar.close()
        return self._error_list


class ConfigUtil(object):
    @staticmethod
    def use_new_tool_lib_config(task_params):
        # 环境变量开关
        if os.getenv("USE_TOOL_SCHEME") == "False":
            return False
        tool_params = task_params.get("checktool", {})
        if tool_params.get("tool_schemes"):
            return True
        else:
            return False

    @staticmethod
    def generate_task_list(task_params):
        """根据单个task_params，生成一个task list格式数据结构"""
        task_name = task_params.get("tool_name", "cutsomtool")
        task_list = [{
            "task_name": task_name,
            "task_params": task_params
        }]
        return task_list


class ToolLoader(object):
    """工具拉取管理类"""

    def __init__(self, tool_names=None, os_type=None, task_list=None, custom_tools=None, config_all_tools=False, include_common=True):
        """
        构造函数
        :param tool_names: <list> 工具名列表，可以指定单个或多个工具；默认为空，表示全量工具
        :param os_type: <str> 操作系统，可以指定拉取某个OS（忽略当前机器环境所处OS）的工具
        :param task_list: <list> 任务参数的列表，可以包含单个或多个工具任务
        :return:
        """
        # 读取工具配置信息
        self.__tool_config = ConfigLoader(os_type=os_type).read_tool_config(tool_names=tool_names,
                                                                            task_list=task_list,
                                                                            custom_tools=custom_tools,
                                                                            config_all_tools=config_all_tools,
                                                                            include_common=include_common)

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
        tool_dirname_list = []
        for git_url, tool_info in tool_url_info.items():
            tool_dirname = BaseScmUrlMgr.get_last_dir_name_from_url(git_url)
            # 工具目录名重复，说明是同一工具，去重，避免重复拉取造成线程冲突
            if tool_dirname in tool_dirname_list:
                continue
            else:
                tool_dirname_list.append(tool_dirname)
            tool_dirpath = os.path.join(settings.TOOL_BASE_DIR, tool_dirname)

            load_type, dirpath_copy_from = ToolCommonLoader.load_tool_type(tool_dirpath, tool_dirname, git_url)

            load_tool_list.append({
                "load_type": load_type,
                "git_url": git_url,
                "tool_dirname": tool_dirname,
                "tool_dirpath": tool_dirpath,
                "copy_from": dirpath_copy_from,
                "print_enable": print_enable,
                "auth_info": tool_info.get("auth_info")
            })

        if load_tool_list:  # 多线程拉取工具
            start_time = time.time()
            error_list = ThreadRunner().run(load_tool_list)

            if error_list:
                # 将线程的第一个异常抛出
                raise error_list[0]
            LogPrinter.info(f"Initialize tools done.(use time: {format(time.time() - start_time, '.2f')}s)")

    def set_tool_env(self):
        """
        加载工具所需的环境变量
        :return:
        """
        EnvSet().set_tool_env(self.__tool_config)


class ToolConfigLoader(object):
    def load_tool_config(self, load_common_tools=True):
        """
        拉取|更新工具配置文件
        :return:
        """
        tool_config = ToolConfig()
        tool_config_url = tool_config.get_tool_config_url()
        LogPrinter.info(f"Load tool config: {tool_config_url}")
        tool_config_dir_name = tool_config.get_tool_config_dir_name()
        tool_config_dir_path = tool_config.get_tool_config_dir_path()
        load_type, dirpath_copy_from = ToolCommonLoader.load_tool_type(tool_config_dir_path, tool_config_dir_name, tool_config_url)

        ToolCommonLoader.load_tool(load_type, tool_config_dir_path, dirpath_copy_from, tool_config_url)
        if load_common_tools:
            self.load_common_tools_and_set_env()

    def load_common_tools_and_set_env(self):
        """
        拉取并加载所有common工具，包括zip工具，供后续解压工具zip包使用
        """
        tool_loader = ToolLoader(include_common=True)
        LogPrinter.info(f"Initing common tools ...")
        tool_loader.git_load_tools(print_enable=False)
        tool_loader.set_tool_env()
        self.setup_git_lfs()

    def setup_git_lfs(self):
        """
        拉取git lfs工具后，需要额外执行 git lfs install，避免部分机器lfs不可用：Skipping object checkout, Git LFS is not installed.
        """
        try:
            cmd_args = ["git", "lfs", "install"]
            LogPrinter.info('run cmd: %s' % ' '.join(cmd_args))
            spc = SubProcController(
                command=cmd_args,
                stdout_line_callback=LogPrinter.info,
                stderr_line_callback=LogPrinter.info,
                stdout_filepath=None,
                stderr_filepath=None
            )
            spc.wait()
        except Exception as err:
            LogPrinter.error(f"git lfs cmd error: {str(err)}, please check.")
