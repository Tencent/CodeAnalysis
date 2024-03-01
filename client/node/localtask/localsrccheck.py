# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
LocalSourcedir
"""
import os
import logging

from util.exceptions import NodeError
from util.errcode import E_NODE_TASK_SCM_FAILED
from util.scmurlmgr import BaseScmUrlMgr
from node.localtask.scmtoolcheck import ScmToolCheck
from util.cmdscm import ScmClient

logger = logging.getLogger(__name__)


class LocalSrcScm(object):
    def __init__(self, scm_info, scm_client, branch):
        self._scm_info = scm_info
        self._scm_client = scm_client
        self._branch = branch

    def get_scm_url(self, local_scm_info):
        """
        从本地代码scm info中获取scm url
        :return:
        """
        if not local_scm_info.url:
            err_msg = "本地代码库获取不到 [origin标签] 远程代码库链接，" \
                      "请在代码目录下检查确认是否为空: git config --get remote.origin.url," \
                      "并执行以下命令进行设置：git remote add origin ${代码库链接}"
            raise NodeError(code=E_NODE_TASK_SCM_FAILED, msg=err_msg)
        repo_url = BaseScmUrlMgr.format_url(local_scm_info.url)
        self._scm_info.repo_url = repo_url
        if self._scm_info.scm_type == "svn":
            self._scm_info.scm_url = repo_url
            self._scm_info.branch = "master"
            return self._scm_info
        elif self._scm_info.scm_type == "git":
            if self._branch:  # 如果参数有指定git分支名称,不需要自动识别
                if "master" == self._branch:  # 为了兼容旧版,master分支直接只用url,不加分支名
                    self._scm_info.scm_url = repo_url
                    self._scm_info.branch = "master"
                    return self._scm_info
                else:
                    self._scm_info.scm_url = "%s#%s" % (repo_url, self._branch)
                    self._scm_info.branch = self._branch
                    return self._scm_info
            elif self._scm_client.check_branch_at_detach_state():  # 如果是游离态分支,提醒用户使用--branch指定分支名
                raise NodeError(code=E_NODE_TASK_SCM_FAILED, msg="本地git代码属于游离态分支,请使用--branch参数指定分支名称.")
            else:  # 如果不是是游离分支,使用识别出来的分支名称
                # 更新分支名信息
                self._scm_info.branch = local_scm_info.branch
                if "master" == local_scm_info.branch:  # 为了兼容旧版,master分支直接只用url,不加分支名
                    self._scm_info.scm_url = repo_url
                    return self._scm_info
                else:
                    self._scm_info.scm_url = "%s#%s" % (repo_url, local_scm_info.branch)
                    return self._scm_info
        else:
            raise NodeError(code=E_NODE_TASK_SCM_FAILED, msg="不支持的scm类型: %s!" % self._scm_info.scm_type)


class LocalSourcedir(object):
    def __init__(self, scm_info, source_dir, branch):
        self._scm_info = scm_info
        self._source_dir = source_dir
        self._branch = branch
        self._scm_client = None

    def check_local_source_dir(self):
        """
        检查本地代码目录是否符合扫描条件
        :return: 本地代码符合扫描条件,返回True;否则返回False
        """
        # 根据scm_type先检查是否有安装svn|git命令行工具,避免后续报错不清晰
        ScmToolCheck.check_scm_cmd_tool(self._scm_info.scm_type)
        # 1.source_dir是否是一个scm代码库(包含scm信息)
        self._scm_client = ScmClient(scm_type=self._scm_info.scm_type,
                                     scm_url="",
                                     source_dir=self._source_dir,
                                     scm_username="",
                                     scm_password="")

        if not self._scm_client.is_source_dir():
            msg = "%s不是一个%s代码库(不包含%s信息)!" % (self._source_dir, self._scm_info.scm_type, self._scm_info.scm_type)
            raise NodeError(code=E_NODE_TASK_SCM_FAILED, msg=msg)

        # 本地代码url和版本号
        local_scm_info = self._scm_client.info()
        self._scm_info = LocalSrcScm(self._scm_info,
                                     self._scm_client,
                                     self._branch).get_scm_url(local_scm_info)
        self._scm_info.scm_revision = local_scm_info.commit_revision
        self._scm_info.scm_time = local_scm_info.commit_time

        local_uncommit_files = self._scm_client.get_uncommit_files()
        # 排除unversioned(未加入版本库)的文件,比如编译生成的中间文件
        local_uncommit_files = [item for item in local_uncommit_files if item.state != "unversioned"]
        if local_uncommit_files:
            logger.warning("检测到以下文件改动,未提交代码库:")
            for diff_info in local_uncommit_files:
                logger.warning(diff_info)
            logger.warning("扫描结果展示的代码，是git远端代码，如果有扫描未提交代码，请参考本地代码查看结果.")
        return self._scm_client, self._scm_info
