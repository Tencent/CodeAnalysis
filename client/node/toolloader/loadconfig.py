# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""从git拉取环境变量和工具配置,并读取配置文件
"""


import os
import json
import platform
import sys
import configparser

from node.app import settings
from util.configlib import ConfigReader
from util.textutil import StringMgr
from util.logutil import LogPrinter
from util.exceptions import NodeConfigError
from util.scmurlmgr import BaseScmUrlMgr


class LoadToolTypes(object):
    """拉取内置工具方式"""
    GIT_LOAD = "1"  # 从git下载


class ToolConfig(object):
    """tool config配置库管理"""
    def __init__(self):
        self._url = settings.TOOL_CONFIG_URL
        self._tool_config_dir_name = BaseScmUrlMgr.get_last_dir_name_from_url(self._url)
        self._tool_config_dir_path = os.path.join(settings.TOOL_BASE_DIR, self._tool_config_dir_name)

    def get_tool_config_url(self):
        return self._url

    def get_tool_config_dir_name(self):
        return self._tool_config_dir_name

    def get_tool_config_dir_path(self):
        return self._tool_config_dir_path


class ConfigLoader(object):
    """配置文件加载类"""
    def __init__(self, os_type=None):
        if not os_type:
            os_type = settings.PLATFORMS[sys.platform]
        tool_config_dir = ToolConfig().get_tool_config_dir_path()
        # linux arm64使用单独的tool配置文件
        if os_type == "linux" and platform.machine() == "aarch64":
            os_type = f"{os_type}_arm64"
        self._tool_config_file = os.path.join(tool_config_dir, "%s_tools.ini" % os_type)
        self._os_type = os_type

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

    def read_tool_config(self, tool_names, task_list=None, custom_tools=None, config_all_tools=False, include_common=True):
        """
        读取工具配置文件
        :param tool_names:  <list>, 工具名列表.默认为空,读取全量工具配置
        :param task_list: <list>, 任务参数的列表，可以包含单个或多个工具任务
        :param custom_tools: <list>, 自定义工具名称列表
        :param config_all_tools: <bool>, 是否读取所有工具配置
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
        scheme_config_tools, config_dict_from_tool_schemes = self.read_config_from_tool_schemes(tool_names, task_list)
        # aaaa = "_".join(scheme_config_tools)
        # with open(f"tool_{aaaa}_from_schemes.json", "w") as wf:
        #     json.dump(config_dict_from_tool_schemes, wf, indent=2)

        ini_config_tools = []
        if tool_names:  # 先判空
            for tool_name in tool_names:
                if tool_name not in scheme_config_tools:
                    ini_config_tools.append(tool_name)

        # 从ini文件中读取工具配置
        config_dict = self.read_tool_config_from_ini_file(ini_config_tools, custom_tools, task_list, config_all_tools=config_all_tools, include_common=include_common)

        # aaaa = "_".join(ini_config_tools)
        # with open(f"tool_{aaaa}_from_ini.json", "w") as wf:
        #     json.dump(config_dict, wf, indent=2)

        # 合并两边的配置
        if config_dict_from_tool_schemes:
            config_dict.update(config_dict_from_tool_schemes)

            # aaaa = "_".join(tool_names)
            # cur_time = time.time()
            # with open(f"tool_{aaaa}_merged_{cur_time}.json", "w") as wf:
            #     json.dump(config_dict, wf, indent=2)

        return config_dict

    def __update_tool_names(self, tool_names, task_list):
        """
        如果tool_names中包含customscan工具，只有部分特殊规则按需加载依赖和配置
        其他规则无额外依赖，不需要加载依赖和配置
        """
        # LogPrinter.info(f"task_list: {json.dumps(task_list, indent=2)}")
        c_name = "customscan"
        special_rule_list = ["FunctionTooLong"]

        if c_name not in tool_names:
            return tool_names

        if not task_list:
            return tool_names

        for task_config in task_list:
            task_name = task_config.get("task_name")
            if task_name == c_name:
                task_params = task_config.get("task_params", {})
                rule_names = task_params.get("rules", [])
                for special_rule in special_rule_list:
                    if special_rule in rule_names:
                        tool_names.append(special_rule)

        # 从工具列表中剔除customscan,不做统一加载配置
        tool_names.remove(c_name)
        return tool_names

    def read_tool_config_from_ini_file(self, tool_names=None, custom_tools=None, task_list=None, config_all_tools=False,
                                       include_common=True):
        """
        从ini文件中读取工具配置
        """
        if not os.path.exists(self._tool_config_file):
            raise NodeConfigError(f"{self._tool_config_file}  not exists!")
        config_dict = {}
        cfg = ConfigReader(cfg_file=self._tool_config_file, interpolation=configparser.ExtendedInterpolation())

        # 读取env_path
        env_path_section = cfg.read("env_path")
        # 读取env_value
        env_value_section = cfg.read("env_value")
        # 读取tool_url
        tool_url_section = cfg.read("tool_url")

        # 获取ini中配置的所有工具名称
        section_names = cfg.get_section_names()
        other_sections = ["server_config", "env_path", "env_value", "tool_url", "common", "base_value"]
        # 所有在ini中配置的工具名称(除了公共的section名称，其他的section都是工具名)
        all_tool_names = [sec_name for sec_name in section_names if sec_name not in other_sections]

        if config_all_tools:  # 如果是全量工具,把所有环境变量和tool_url都加载进来，不需要逐个工具去读取配置
            if "PATH" in env_path_section:  # 获取key为"PATH"的元素值,作为编译工具的PATH,并在env_path_section中删掉
                compile_tools_path = self.__str_to_list(env_path_section.pop("PATH"), uniq=False)
            else:
                compile_tools_path = []
            compile_config = {
                "path": compile_tools_path,
                "tool_url": list(set(tool_url_section.values())),
                "env_path": env_path_section,  # env_path_section中现在已经没有key为"PATH"的元素,可以作为编译工具的env_path
                "env_value": env_value_section
            }
            self.__format_to_fullpath(compile_config)
            config_dict["compile_config"] = compile_config
            return config_dict
        else:
            # 读取common配置
            if include_common:
                common_config = cfg.read("common")
                self.__format_config(common_config, env_path_section, env_value_section)
                config_dict["common"] = common_config

            wanted_tools = []  # 收集需要读取配置的工具列表
            for tool_name in tool_names:
                if tool_name in all_tool_names:
                    wanted_tools.append(tool_name)
                elif custom_tools:
                    if tool_name in custom_tools:  # 如果工具名不在ini中，且是自定义工具，需要加载customtool配置
                        if "customtool" not in wanted_tools:
                            wanted_tools.append("customtool")

            # customscan特殊处理
            # LogPrinter.info(f">> 1. tool_names: {wanted_tools}")
            wanted_tools = self.__update_tool_names(wanted_tools, task_list)
            # LogPrinter.info(f">> 2. tool_names: {wanted_tools}")

            # 读取工具配置
            for tool_name in wanted_tools:
                tool_cfg = cfg.read(tool_name)
                if tool_cfg:
                    self.__format_config(tool_cfg, env_path_section, env_value_section)
                    config_dict[tool_name] = tool_cfg

            return config_dict

    def __format_config(self, tool_cfg, env_path_section, env_value_section):
        """
        工具配置中的env_path和env_value，是变量字符串，需要将变量转换为实际值，并转换为dict格式
        工具配置中的tool_url和path，是字符串，需要转换为list格式
        path不需要去重，因为是需要按顺序加载的
        """
        tool_cfg["env_path"] = self.__str_to_dict(tool_cfg["env_path"], env_path_section)
        tool_cfg["env_value"] = self.__str_to_dict(tool_cfg["env_value"], env_value_section)
        tool_cfg["tool_url"] = self.__str_to_list(tool_cfg["tool_url"])
        tool_cfg["path"] = self.__str_to_list(tool_cfg["path"], uniq=False)
        self.__format_to_fullpath(tool_cfg)

    def __format_to_fullpath(self, tool_cfg):
        # 将路径类型的环境变量（env_path）中的相对路径转换成绝对路径
        for env_name, rel_path in tool_cfg["env_path"].items():
            if "PATH" == env_name:  # PATH应该单独放在path字段中，如果放在env_path中，忽略，避免影响和覆盖原有PATH变量
                continue
            full_path = os.path.join(settings.TOOL_BASE_DIR, rel_path)
            tool_cfg["env_path"][env_name] = full_path

        # 将PATH环境变量的相对路径转换成绝对路径
        path_env = []
        for rel_path in tool_cfg["path"]:
            if "$" in rel_path or "%" in rel_path:  # 带变量的环境变量，已经是全路径
                full_path = rel_path
            else:
                full_path = os.path.join(settings.TOOL_BASE_DIR, rel_path)
            path_env.append(full_path)
        tool_cfg["path"] = path_env

    def read_config_from_tool_schemes(self, tool_names=None, task_list=None):
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
        # 环境变量开关
        if os.getenv("USE_TOOL_SCHEME") == "False":
            return [], {}

        if not task_list:
            return [], {}

        config_dict = {}
        already_config_tools = []  # 记录已经读取到配置的工具
        for task_config in task_list:
            task_name = task_config.get("task_name")
            if tool_names and task_name not in tool_names:
                continue
            task_params = task_config.get("task_params", {})
            check_tool = task_params.get("checktool", {})
            tool_schemes = check_tool.get("tool_schemes", [])
            # tool_name = check_tool.get("display_name")
            if tool_schemes:
                already_config_tools.append(task_name)
                # 判断condition,获取符合条件的依赖方案
                tool_scheme = self.__get_tool_scheme(task_name, task_params, tool_schemes)
                if tool_scheme:
                    tool_libs = tool_scheme.get("tool_libs", [])
                    for tool_lib in tool_libs:
                        lib_support_os = tool_lib.get("os", [])
                        if self._os_type in lib_support_os:
                            # 使用新的结构存储环境变量，避免修改原有的任务参数
                            new_lib_envs = {}
                            lib_envs = tool_lib.get("envs", {})
                            if not lib_envs:  # 可能会传空list，这里判空，避免后面格式出错
                                new_lib_envs = {}

                            scm_url = tool_lib.get("scm_url")
                            # 支持git仓库地址和zip包地址两种格式
                            lib_dir_name = BaseScmUrlMgr.get_last_dir_name_from_url(scm_url)
                            lib_dir_path = os.path.join(settings.TOOL_BASE_DIR, lib_dir_name)

                            # 将环境变量中的$ROOT_DIR替换为实际路径，重新保存到new_lib_envs
                            for key, value in lib_envs.items():
                                if "$ROOT_DIR" in value:
                                    new_lib_envs[key] = value.replace("$ROOT_DIR", lib_dir_path)
                                else:
                                    new_lib_envs[key] = value

                            # PATH和其他环境变量分开处理
                            path_envs = []
                            other_envs = {}
                            for env_name, env_value in new_lib_envs.items():
                                if env_name == "PATH":
                                    path_envs = self.__str_to_list(env_value)
                                else:
                                    # 根据英文分号拆分后，再环境变量分隔符拼接到一起
                                    value_list = self.__str_to_list(env_value)
                                    value_format = os.pathsep.join(value_list)
                                    other_envs[env_name] = value_format
                            lib_config = {
                                "tool_url": scm_url,
                                "scm_type": tool_lib.get("scm_type"),
                                "auth_info": tool_lib.get("auth_info"),
                                "path": path_envs,
                                "env_path": other_envs,
                                "env_value": {}
                            }
                            lib_name = tool_lib.get("name")
                            config_dict[lib_name] = lib_config
        return already_config_tools, config_dict

    def __get_tool_scheme(self, tool_name, task_params, tool_schemes):
        """
        获取符合当前任务的工具依赖方案
        """
        default_scheme = None
        right_tool_scheme = None

        # 1. 判断是否符合方案条件
        for tool_scheme in tool_schemes:
            default_flag = tool_scheme.get("default_flag")
            if default_flag:
                default_scheme = tool_scheme
            if self.__check_tool_scheme_condition(task_params, tool_scheme):
                right_tool_scheme = tool_scheme
                break

        # 没有符合任一方案条件，且默认方案存在，则使用默认方案
        if not right_tool_scheme:
            if default_scheme:  # 如果未匹配到，使用默认的方案（有默认方案的情况下）
                right_tool_scheme = default_scheme
            else:
                LogPrinter.warning(f"{tool_name} has no default scheme, please check!")
                return None

        # 2. 判断是否支持当前的操作系统
        scheme_supprot_os = right_tool_scheme.get("os")
        if self._os_type in scheme_supprot_os:
            return right_tool_scheme
        else:
            return None

    def __check_tool_scheme_condition(self, task_params, tool_scheme):
        """
        判断当前task的envs是否符合tool_scheme的condition
        :param task_params:
        :param tool_scheme:
        :return:
        """
        condition_str = tool_scheme.get("condition")
        condition = StringMgr.str_to_dict(condition_str) if condition_str else {}
        task_envs_str = task_params.get('envs', None)
        task_envs = StringMgr.str_to_dict(task_envs_str) if task_envs_str else {}

        # 当条件和环境变量都存在时，才判断是否符合当前方案条件
        # 条件和环境变量任一不存在，都判定为不符合
        if condition and task_envs:
            if self.__envs_match_condition(task_envs, condition):
                return True
        return False

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
