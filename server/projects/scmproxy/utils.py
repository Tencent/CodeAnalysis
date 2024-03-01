# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""通用工具类
"""

import logging
import re
from hashlib import sha1

logger = logging.getLogger("utils")


def get_source_dir(scm_url):
    """根据scm_url获取源码位置

    :param scm_url: str - 项目的代码库地址
    :return: str - 源码目录路径
    """
    if isinstance(scm_url, str):
        scm_url = scm_url.encode()
    dir_name = sha1(scm_url).hexdigest()
    return dir_name


class ScmError(object):
    """SCM错误类
    """

    @classmethod
    def handler_msg(cls, scm_type, err_msg):
        """处理错误信息
        :param err_msg: str，错误信息
        :return: str，格式化后的错误信息
        """
        if scm_type in ["git", "tgit", "ssh+git", "coding-git", "git-oauth"]:
            return cls.__git_error_handler(err_msg)
        elif scm_type in ["svn", "ssh+svn"]:
            return cls.__svn_error_handler(err_msg)
        else:
            return "Scm type %s not support" % scm_type

    @classmethod
    def __git_error_handler(cls, err_msg):
        logger.info("handle git err msg: %s" % err_msg)

        err_msg_dict = {
            r"could not read Username for '.*': No such device or address":
                "Authentication failed - Bad username or password.",
            r"ambiguous argument '.*': unknown revision or path not in the working tree.": "Revision doesn't exist: %s",
            r"Could not resolve host:": "Project doesn't exist or no project code access permission.",
            r"The requested URL returned error: ": "Git server error.",
            r"from the remote, but no such ref was fetched": "Branch doesn't exist.",
            r"Remote branch .*? not found in upstream origin": "Branch doesn't exist.",
            r"Unexpected end of command[s]? stream": "Branch doesn't exist.",
            r"remote error: Git:Project not found": "Project doesn't exist or no project code access permission.",
            r"remote error: Git repository not found": "Project doesn't exist or no project code access permission.",
            r"Please make sure you have the correct access rights":
                "Project doesn't exist or no project code access permission.",
            r"repository '.*' not found": "Project doesn't exist or no project code access permission.",
            r"Path '.*?' does not exist": "File doesn't exist.",
            r"Authentication failed": "Authentication failed - Bad username or password.",
            r"Ref '.*?' did not resolve to an object": "Revision doesn't exist.",
            r"SHA .*? could not be resolved": "Revision doesn't exist.",
            r"Invalid object name '.*?'": "Revision doesn't exist.",
            r"Not a valid object name .*": "Revision doesn't exist.",
        }
        for pattern, msg in err_msg_dict.items():
            if re.search(pattern, err_msg):
                return msg
        return err_msg

    @classmethod
    def __svn_error_handler(cls, err_msg):
        """SVN错误日志处理
        """
        logger.info("handle svn git err msg: %s" % err_msg)
        err_msg_dict = {
            r"'.*' path not found": "File doesn't exist.",
            r"The node '.*' was not found": "File doesn't exist.",
            r"URL '.*' non-existent in revision .*": "File doesn't exist.",
            r".*Authentication failed": "Authentication failed - Bad username or password.",
            r"No such revision .*": "Revision doesn't exist",
            r"Unable to find repository location for '.*?' in revision": "Revision doesn't exist.",
            r"Unable to connect to a repository at URL '.*'\nsvn: E\d+: Access to '.*' forbidden$":
                "No permission.",
            r"Unable to connect to a repository at URL '.*'\nsvn: E\d+: Name or service not known$":
                "Project doesn't exist.",
            r"Unable to connect to a repository at URL '.*'\nsvn: E\d+: "
            r"Unexpected HTTP status 504 'Gateway Time-out' on '.*'": "SVN server error",
        }

        for pattern, msg in err_msg_dict.items():
            if re.search(pattern, err_msg):
                return msg
        return err_msg
