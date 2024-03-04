# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""从git拉取|更新,使用公共账号权限
"""

import logging
import os
import uuid

from node.app import settings
from util.cmdscm import ScmClient
from util.crypto import Crypto
from util.pathlib import PathMgr
from util.exceptions import NodeError
from util.errcode import E_NODE_TASK_SCM_FAILED
from util.scmcache import SshFlieClient

logger = logging.getLogger(__name__)


class GitLoader(object):
    def __init__(self, scm_url, dest_dir, scm_auth_info=None, print_enable=False):
        """

        :param scm_url: git库地址
        :param dest_dir: 拉取到本地的目录路径
        :param scm_auth_info: git鉴权方式
        :param print_enable: 是否打印详细日志到终端, 默认不打印
        """
        self._scm_type = "git"
        self._scm_url = scm_url
        self._dest_dir = dest_dir
        self._scm_auth_info = scm_auth_info
        self._print_enable = print_enable
        # 生成一个随机的文件路径保存ssh私钥，避免多个工具相互覆盖，以及删除时误删
        self._ssh_temp_file = os.path.abspath(f"tool_ssh_{uuid.uuid1().hex}")
        self._scm_client = self.__init_scm_client()

    def __init_scm_client(self):
        """
        初始化scm实例的公共函数
        :return: 返回一个新的scm实例
        """
        if self._print_enable:
            stdout_filepath = None
            stderr_filepath = None
        else:
            stdout_filepath = "cmdgit_stdout.log"
            stderr_filepath = "cmdgit_stderr.log"

        if self._scm_auth_info:  # 使用传递的鉴权方式
            self._ssh_file = self.__get_ssh_file()
            if self._ssh_file:  # 使用ssh方式
                scm_client = ScmClient(
                    self._scm_type,
                    self._scm_url,
                    self._dest_dir,
                    ssh_file=self._ssh_file,
                    print_enable=self._print_enable,
                    stdout_filepath=stdout_filepath,
                    stderr_filepath=stderr_filepath
                )
            else:  # 使用账号密码/oauth方式
                password = Crypto(settings.PASSWORD_KEY).decrypt(
                    self._scm_auth_info["scm_password"])
                scm_client = ScmClient(
                    self._scm_type,
                    self._scm_url,
                    self._dest_dir,
                    self._scm_auth_info["scm_username"],
                    password,
                    print_enable=self._print_enable,
                    stdout_filepath=stdout_filepath,
                    stderr_filepath=stderr_filepath
                )
        else:
            if settings.TOOL_LOAD_ACCOUNT["USERNAME"] and settings.TOOL_LOAD_ACCOUNT["PASSWORD"]:
                username = settings.TOOL_LOAD_ACCOUNT["USERNAME"]
                password = settings.TOOL_LOAD_ACCOUNT["PASSWORD"]
            else:
                username = ""
                password = ""
                # raise NodeError(code=E_NODE_TASK_SCM_FAILED, msg="请先在config.ini中配置TOOL_LOAD_ACCOUNT信息")
            scm_client = ScmClient(
                scm_type="git",
                scm_url=self._scm_url,
                source_dir=self._dest_dir,
                scm_username=username,
                scm_password=password,
                print_enable=self._print_enable,
                stdout_filepath=stdout_filepath,
                stderr_filepath=stderr_filepath
            )
        return scm_client

    def __get_ssh_file(self):
        """
        创建ssh私钥文件
        :return:
        """
        if self._scm_auth_info:
            if "scm_ssh_key" in self._scm_auth_info:
                if self._scm_auth_info["scm_ssh_key"]:
                    ssh_key = Crypto(settings.PASSWORD_KEY).decrypt(
                        self._scm_auth_info["scm_ssh_key"])
                    return SshFlieClient.create_temp_ssh_file(ssh_key, self._ssh_temp_file)
        return None

    def load(self):
        """
        从git拉取或更新一个代码仓库
        :return:
        """
        try:
            if os.path.exists(self._dest_dir):  # 目录已存在
                local_dir_scm = ScmClient(scm_type="git",
                                          scm_url="",
                                          source_dir=self._dest_dir,
                                          scm_username="",
                                          scm_password="")
                if local_dir_scm.can_reuse_by(self._scm_url):  # 可以复用
                    self.__retry_update()
                else:  # 不能复用，删除当前工具目录重新拉取
                    # logger.info(f"不能复用{self._dest_dir}，删除当前工具目录重新拉取...")
                    PathMgr().safe_rmpath(self._dest_dir)
                    self.__retry_checkout()
            else:  # 目录不存在
                dir_path = os.path.dirname(self._dest_dir)
                if not os.path.exists(dir_path):  # 如果上层目录不存在,先创建
                    os.makedirs(dir_path)
                self.__retry_checkout()
        except Exception as err:
            raise NodeError(code=E_NODE_TASK_SCM_FAILED, msg=str(err))
        finally:
            # 删除临时保存的ssh key文件
            SshFlieClient.remove_temp_ssh_file(self._ssh_temp_file)

    def __retry_update(self):
        try:
            self._scm_client.update()
        except Exception as err:
            # logger.error(f"本地目录更新异常,Error:{str(err)}, 删除目录重新拉取...")
            PathMgr().safe_rmpath(self._dest_dir)
            self.__retry_checkout()

    def __retry_checkout(self):
        try:
            self._scm_client.checkout()
        except Exception as err:
            # logger.error(f"拉取异常,Error:{str(err)}, 删除目录重新拉取...")
            PathMgr().safe_rmpath(self._dest_dir)
            self._scm_client.checkout()
