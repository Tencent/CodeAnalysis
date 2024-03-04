
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================
"""
本地配置管理类
"""

import os
import logging

from node.app import settings
from util.configlib import ConfigReader

logger = logging.getLogger(__name__)


class LocalConfig(object):
    """
    本地配置管理
    """
    @staticmethod
    def get_server_url(config_file=None):
        """
        从配置文件中获取用户指定的server url
        如果获取不到,默认从settings中获取
        :param config_file: 本地配置文件路径
        :return:
        """
        # 1.从配置文件获取
        if not config_file:
            cur_working_dir = os.path.abspath(os.curdir)
            config_file = os.path.join(cur_working_dir, 'codedog.ini')
        if os.path.exists(config_file):
            config_dict = ConfigReader(cfg_file=config_file).read("config")
            codedog_env = config_dict.get("codedog_env")
            if codedog_env:
                codedog_env = codedog_env.strip()
                if codedog_env not in ["dev", "test", "tiyan", "prod"]:
                    # 补充http头
                    if not codedog_env.startswith("http"):
                        codedog_env = "http://%s" % codedog_env
                    # 修正settings中的server url,不使用默认的
                    settings.SERVER_URL["URL"] = codedog_env
                    # 设置到环境变量中,供task中使用(因为task进程的工作目录不在codedog根目录，无法获取到ini文件的codedog_env配置)
                    os.environ["CODEDOG_SERVER"] = codedog_env
                    return codedog_env
        # 2.如果配置文件没有指定,从环境变量获取
        codedog_server_url = os.environ.get("CODEDOG_SERVER", None)
        if codedog_server_url:
            return codedog_server_url
        # 3.默认使用setting默认对应的url地址
        return settings.SERVER_URL["URL"]
