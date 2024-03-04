# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
ScmAuthCheck
"""
from node.localtask.scmtoolcheck import ScmToolCheck
from util.cmdscm import ScmClient
from util.exceptions import NodeError
from util.errcode import E_NODE_TASK_CONFIG


class ScmAuthCheck(object):
    def __init__(self, scm_info, scm_auth_info, source_dir):
        self._scm_info = scm_info
        self._source_dir = source_dir
        self._ssh_file = scm_auth_info.ssh_file
        self._scm_username = scm_auth_info.username
        self._scm_password = scm_auth_info.password

    def check_scm_authority(self):
        """
        检查 username 和 password 权限
        :return: True(有权限)|False(重新输入后仍无权限)
        """
        # 先检查是否有安装svn|git命令行工具
        ScmToolCheck.check_scm_cmd_tool(self._scm_info.scm_type)

        # 2019-04-02 add
        # 如果指定了本地代码目录,且是git类型,后续命令可以正常执行,可以不执行鉴权操作
        # 原因:可能由于机器git配置问题,导致鉴权命令执行失败,但实际上执行其他git命令都是有权限的
        if self._source_dir and self._scm_info.scm_type == "git":
            return

        # 校验账号密码是否有效
        scm_auth = False
        if self._ssh_file:
            scm_client = ScmClient(
                scm_type=self._scm_info.scm_type,
                scm_url=self._scm_info.scm_url,
                source_dir=self._source_dir,
                ssh_file=self._ssh_file
            )
        else:
            scm_client = ScmClient(
                scm_type=self._scm_info.scm_type,
                scm_url=self._scm_info.scm_url,
                source_dir=self._source_dir,
                scm_username=self._scm_username,
                scm_password=self._scm_password)
        if (self._scm_username and self._scm_password) or self._ssh_file:
            # 有输入账号密码,或者指定了ssh_file时,验证账号权限是否有效
            scm_auth = scm_client.check_auth()
        else:
            # 否则,验证缓存的账号权限是否有效
            scm_auth = scm_client.check_auth_with_cache()

        if not scm_auth:
            raise NodeError(code=E_NODE_TASK_CONFIG, msg="未输入账号密码,或账号密码无权限!")

