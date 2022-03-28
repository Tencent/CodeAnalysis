# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""从git拉取环境变量和工具配置,并读取配置文件
"""

import os
import platform
import sys
import configparser

from node.app import settings
from util.configlib import ConfigReader
from util.textutil import StringMgr
from util.logutil import LogPrinter
from util.exceptions import NodeConfigError


class ConfigLoader(object):
    """配置文件加载类"""
    def __init__(self, os_type=None):
        if not os_type:
            os_type = settings.PLATFORMS[sys.platform]
        tool_config_dir_name = settings.TOOL_CONFIG_URL.split('/')[-1].strip().replace(".git", "")
        tool_config_dir = os.path.join(settings.TOOL_BASE_DIR, tool_config_dir_name)
        # linux arm64使用单独的tool配置文件
        if os_type == "linux" and platform.machine() == "aarch64":
            os_type = f"{os_type}_arm64"
        self._tool_config_file = os.path.join(tool_config_dir, "%s_tools.ini" % os_type)

    def check_config_exists(self):
        """检查配置文件是否存在"""
        if not os.path.exists(self._tool_config_file):
            error_msg = f"Tool config ({self._tool_config_file}) not exists!" \
                        f"\nPlease run this command to load tools: python3 codepuppy.py updatetool -a"
            LogPrinter.error(error_msg)
            raise NodeConfigError(error_msg)

    def __str_to_dict(self, key_str, ref_dict):
        """
        将"key1;key2;..."字符串转换为key-value字典
        :param key_str: "key1;key2;..."字符串,环境变量名
        :param ref_dict: dict,参考环境变量键值对
        :return: dict, 需要的环境变量键值对
        """
        env_dict = {}
        key_name_list = [key_name.strip() for key_name in key_str.split(";") if key_name.strip()]
        key_name_list = list(set(key_name_list))  # 去重
        for key_name in key_name_list:
            env_dict[key_name] = ref_dict[key_name]
        return env_dict

    def __str_to_list(self, data_str, uniq=True):
        """
        将英文分号分隔的字符串,拆分为列表,并去重
        :param data_str:
        :param uniq: 是否需要去重,默认需要
        :return:
        """
        data_list = [item.strip() for item in data_str.split(';') if item.strip()]
        if uniq:
            data_list = list(set(data_list))  # 去重
        return data_list

    def read_tool_config(self, tool_names=None, task_list=None):
        """
        读取工具配置文件
        :param tool_names:  <list>, 工具名列表.默认为空,读取全量工具配置
        :param task_list: <list>, 任务参数的列表，可以包含单个或多个工具任务
        :return: dict, 环境变量和工具配置
            {
               "common":
                   {
                       "env_path"  : {"xxx": "xxx", "xxx": "xxx", ...},
                       "env_value" : {"xxx": "xxx", "xxx": "xxx", ...},
                       "path"      : ["xxx", "xxx"],
                       "tool_url"  : ["xxx", "xxx"]
                   },
                "tool_1": {...},
                "tool_2": {...},
                ...
            }
        """
        self.check_config_exists()
        cfg = ConfigReader(cfg_file=self._tool_config_file, interpolation=configparser.ExtendedInterpolation())

        # 读取env_path
        env_path_section = cfg.read("env_path")
        # 读取env_value
        env_value_section = cfg.read("env_value")
        # 读取tool_url
        tool_url_section = cfg.read("tool_url")

        config_dict = {}

        # 读取common配置
        common_config = cfg.read("common")
        common_config["tool_url"] = self.__str_to_list(common_config["tool_url"])
        common_config["path"] = self.__str_to_list(common_config["path"], uniq=False)
        config_dict["common"] = common_config

        section_names = cfg.get_section_names()

        # config_all_tools 标记是否配置全量工具
        config_all_tools = False
        # 如果工具名列表为空,默认为全量工具
        if not tool_names:
            config_all_tools = True
            tool_names = [sec_name for sec_name in section_names
                          if sec_name not in ["server_config", "env_path", "env_value", "tool_url", "common", "base_value"]]

        # 读取工具配置
        for tool_name in tool_names:
            # 不在配置文件中,说明该工具不需要从git拉取,也不需要配置环境变量,跳过
            if tool_name not in section_names:
                continue
            tool_cfg = cfg.read(tool_name)
            tool_cfg["tool_url"] = self.__str_to_list(tool_cfg["tool_url"])
            tool_cfg["path"] = self.__str_to_list(tool_cfg["path"], uniq=False)
            config_dict[tool_name] = tool_cfg

        # 将环境变量字符串转换为字典
        for cfg_name, cfg_data in config_dict.items():
            cfg_data["env_path"] = self.__str_to_dict(cfg_data["env_path"], env_path_section)
            cfg_data["env_value"] = self.__str_to_dict(cfg_data["env_value"], env_value_section)

        # 如果是全量工具,把编译工具配置添加进来
        if config_all_tools:
            compile_config = {}
            # 获取key为"PATH"的元素值,作为编译工具的PATH,并在env_path_section中删掉
            compile_config["path"] = self.__str_to_list(env_path_section.pop("PATH"),
                                                        uniq=False) if "PATH" in env_path_section else []
            compile_config["tool_url"] = list(set(tool_url_section.values()))  # 去重
            # env_path_section中现在已经没有key为"PATH"的元素,可以作为编译工具的env_path
            compile_config["env_path"] = env_path_section
            compile_config["env_value"] = env_value_section
            config_dict["compile_config"] = compile_config

        # with open("tool_config_before.json", "w") as wf:
        #     json.dump(config_dict, wf, indent=2)

        if task_list:
            self.update_tool_config(config_dict, tool_names, task_list)

            # with open("tool_config_after.json", "w") as wf:
            #     json.dump(config_dict, wf, indent=2)

        return config_dict

    def update_tool_config(self, config_dict, tool_names=None, task_list=None):
        """
        从任务参数中读取工具配置
        :param config_dict:
        :param tool_names:
        :param task_list:
        :return: dict, 环境变量和工具配置
            {
               "tool_1":
                   {
                       "env_path"  : {"xxx": "xxx", "xxx": "xxx", ...},
                       "env_value" : {"xxx": "xxx", "xxx": "xxx", ...},
                       "path"      : ["xxx", "xxx"],
                       "tool_url"  : ["xxx", "xxx"]
                   },
                "tool_2": {...},
                ...
            }
        """
        for task_config in task_list:
            task_name = task_config["task_name"]
            if tool_names and task_name not in tool_names:
                continue
            task_params = task_config.get("task_params", {})
            check_tool = task_params.get("checktool", {})
            tool_schemes = check_tool.get("tool_schemes", [])
            # tool_name = check_tool.get("display_name")
            if tool_schemes:
                # 移除已有配置，以tool_schemes为准
                if task_name in config_dict:
                    config_dict.pop(task_name)
                elif "customscan" in config_dict:  # 自定义工具
                    config_dict.pop("customscan")
                for tool_scheme in tool_schemes:
                    scheme_supprot_os = tool_scheme.get("os")
                    # 判断是否符合条件
                    if self.__check_tool_scheme_condition(task_name, task_params, tool_scheme):
                        cur_os = settings.PLATFORMS[sys.platform]
                        # 判断是否支持当前的操作系统
                        if cur_os in scheme_supprot_os:
                            tool_libs = tool_scheme.get("tool_libs", [])
                            for tool_lib in tool_libs:
                                lib_support_os = tool_lib.get("os", [])
                                if cur_os in lib_support_os:
                                    lib_envs = tool_lib.get("envs", {})
                                    scm_url = tool_lib.get("scm_url")
                                    lib_dir_name = scm_url.split('/')[-1].strip().replace(".git", "")
                                    # 环境变量中的$GIT_ROOT_DIR替换为目录名，后续加载环境变量时会拼接为全路径
                                    for key, value in lib_envs.items():
                                        if "$GIT_ROOT_DIR" in value:
                                            lib_envs[key] = value.replace("$GIT_ROOT_DIR", lib_dir_name)
                                    # PATH和其他环境变量分开处理
                                    path_envs = []
                                    other_envs = {}
                                    for env_name, env_value in lib_envs.items():
                                        if env_name == "PATH":
                                            path_envs = self.__str_to_list(env_value)
                                        else:
                                            other_envs[env_name] = env_value
                                    lib_config = {
                                        "tool_url": scm_url,
                                        "scm_type": tool_lib.get("scm_type"),
                                        "auth_info": tool_lib.get("auth_info"),
                                        "path": path_envs,
                                        "env_path": lib_envs,
                                        "env_value": {}
                                    }
                                    lib_name = tool_lib.get("name")
                                    config_dict[lib_name] = lib_config

    def __check_tool_scheme_condition(self, tool_name, task_params, tool_scheme):
        """
        检查当前task是否满足某个工具配置方案的条件
        :param task_params:
        :param tool_scheme:
        :return:
        """
        default_flag = tool_scheme.get("default_flag")
        condition_str = tool_scheme.get("condition")
        condition = StringMgr.str_to_dict(condition_str) if condition_str else {}
        task_envs_str = task_params.get('envs', None)
        task_envs = StringMgr.str_to_dict(task_envs_str) if task_envs_str else {}

        if default_flag:  # 当前配置方案为默认的情况
            if task_envs:
                if condition:
                    if self.__envs_match_condition(task_envs, condition):
                        return True
                    else:
                        return False
                else:  # 当前配置方案为默认，且条件为空，此时任何环境变量都符合条件
                    return True
            else:  # 当前配置方案为默认，如果task环境变量未设置，符合条件
                return True
        else:  # 当前配置方案不是默认的情况
            if condition:
                if task_envs:
                    if self.__envs_match_condition(task_envs, condition):
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                LogPrinter.warning(f"{tool_name} tool_lib scheme error, not default condition is empty!")
                return True  # 理论上判断为符合条件，但实际上不应该出现这种情况（非default且condition为空）

    def __envs_match_condition(self, task_envs, condition):
        """
        判断task_envs是否符合tool_lib的条件
        :param task_envs:
        :param condition:
        :return:
        """
        for key, value in condition.items():
            if key not in task_envs:
                return False
            if task_envs[key] != condition[key]:
                return False
        return True
