# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
获取当前运行环境(开发|测试|体验|正式)
"""
import os
import logging

from util.configlib import ConfigReader

logger = logging.getLogger(__name__)


class SettingType(object):
    """
    节点运行采用的配置类型
    """
    def get_env(self):
        """
        获取当前使用的配置类型(开发|测试|正式环境)
        :return:
        """
        return "settings.base"

    def __get_setting_from_ini(self):
        """
        从codedog.ini中codedog_env字段获取配置类型
        :param config_file:
        :return:
        """
        work_dir = os.path.abspath(os.curdir)
        config_file = os.path.join(work_dir, 'codedog.ini')
        if not os.path.exists(config_file):
            return None
        try:
            config_dict = ConfigReader(cfg_file=config_file).read("config")
            codedog_env = config_dict.get("codedog_env")
        except Exception as err:
            logger.warning(f"read ini error: {str(err)}")
            return None

        return codedog_env.strip()


class LocalSetting(object):
    """
    支持通过 config.ini 和 CODEDOG_CONFIG_ 开头的环境变量自定义配置（优先级: config.ini > 环境变量）
    """
    def __set_from_env(self, settings_module, name):
        """
        config.ini 文件中 COMMON 区块的字段，如果没有配置值，再从环境变量读取
        环境变量命名方式: CODEDOG_CONFIG_字段名
        :param settings_module:
        :param name:
        :return:
        """
        env_value = os.getenv("CODEDOG_CONFIG_%s" % name)
        if env_value:  # 有值,则重置setting的对应key值
            setattr(settings_module, name, env_value)

    def add_local_setting(self, settings_module):
        """
        读取本地配置文件 config.ini, 添加到setting模块中
        :param settings_module:
        :return:
        """
        work_dir = os.path.abspath(os.curdir)
        config_file = os.path.join(work_dir, 'config.ini')
        if os.path.exists(config_file):
            cfg_reader = ConfigReader(cfg_file=config_file)
            section_names = cfg_reader.get_section_names()
            for name in section_names:
                data_dict = cfg_reader.read(name)
                # [common]区块的,直接作为setting模块的属性
                # 其他区块的,区块名作为setting模块的属性
                if name == "COMMON":
                    for key, value in data_dict.items():
                        value = value.strip()
                        if value:  # 有值,则重置setting的对应key值
                            setattr(settings_module, key, value)
                        else:
                            self.__set_from_env(settings_module, key)
                else:
                    # 标记该section中是否有值,如果有一个有值,则认为该section有值,需要覆盖原有的setting
                    # 如果值都为空,则忽略该section
                    has_value = False
                    for key, value in data_dict.items():
                        value = value.strip()
                        if value:
                            has_value = True
                            break
                    if has_value:
                        setattr(settings_module, name, data_dict)
