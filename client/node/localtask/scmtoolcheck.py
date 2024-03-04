# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
TaskProcessMgr
"""
import logging

from util.exceptions import NodeError
from util.errcode import E_NODE_TASK_SCM_FAILED
from util.subprocc import SubProcController

logger = logging.getLogger(__name__)


class ScmToolCheck(object):
    @staticmethod
    def check_scm_cmd_tool(scm_type):
        """
        检查是否有安装svn|git命令行工具:
        1. git命令行工具是必须安装,因为puppy依赖git拉取扫描工具
        2. 如果要扫描的代码类型是svn,则需要安装svn命令行工具
        :return:
        """
        cmd_args = ["git", "--version"]
        spc = SubProcController(command=cmd_args)
        spc.wait()
        if spc.returncode != 0:
            logger.info("run cmd: %s" % ' '.join(cmd_args))
            raise NodeError(code=E_NODE_TASK_SCM_FAILED, msg="未安装git命令行工具,请先安装工具!")

        if scm_type == "svn":
            cmd_args = ["svn", "--version"]
            spc = SubProcController(command=cmd_args)
            spc.wait()
            if spc.returncode != 0:
                logger.info("run cmd: %s" % ' '.join(cmd_args))
                raise NodeError(code=E_NODE_TASK_SCM_FAILED, msg="未安装svn命令行工具,请先安装工具!")
