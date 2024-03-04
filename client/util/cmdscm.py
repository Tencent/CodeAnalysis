# -*-  coding: utf-8  -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""命令行版Scm控制器，依赖标准的SVN或GIT命令行客户端（该模块主要目标是减轻第三方模块的依赖，例如pysvn需要管理员权限才能部署。该模块适用于Python2&3）

SVN参数说明：
  --username ARG      : 指定用户名称 ARG
  --password ARG      : 指定密码 ARG
  --no-auth-cache     : 不要缓存用户认证令牌
  --non-interactive   : 不要交互提示
  --trust-server-cert : 不提示的接受未知的 SSL 服务器证书(只用于选项 “--non-interactive”)
"""

# -*- -*- -*- -*- -*- -*-

from ._cmdsvn import CmdSvn
from ._cmdgit import CmdGit
from ._scmbase import ICmdScm, ScmCommandError, ScmRepoInvalidError, ScmSSHKeyNotFoundError, ScmAuthFailedError
from ._scmbase import BlameInfo, DiffPath, Info, LogInfo, DiffInfo, SubmoduleInfo

# -*- -*- -*- -*- -*- -*- -*- -*- -*- -*- -*- -*- -*- -*- -*- -*-


def ScmClient(scm_type, scm_url, source_dir, scm_username=None, scm_password=None, **kwargs):
    """Scm客户端

    :param scm_type: <str> "git" 或者 "svn"
    :param scm_url: <str> 代码库地址
    :param source_dir: <str> 当前机器代码已拉取或待拉取的存放目录，如果指定目录路径不存在，会自动创建该目录。
    :param scm_username: <str> 拉取代码的用户名
    :param scm_password: <str> 拉取代码的密码
    :param **kwargs: <dict> 可选参数：
        ssh_file: <str> 代码库的SSH密钥路径
        stdout_filepath: <str> CmdScm执行命令标准输出内容写入的文件，默认值为cmdsvn_stdout.log/cmdgit_stdout.log，显式声明None表示不输出
        stderr_filepath: <str> CmdScm执行命令标准错误内容写入的文件，默认值为cmdsvn_stderr.log/cmdgit_stderr.log，，显式声明None表示不输出
        print_enable: <boolean> CmdScm执行命令标准输出内容和标准错误内容是否打印，True表示打印，False表示打印，默认为False
    :return ICmdScm: Scm客户端
    """
    _parmes = ICmdScm.ScmParmes(scm_url, source_dir, scm_username, scm_password)
    if str(scm_type).upper() == ICmdScm.SVN:
        scm_client = CmdSvn(_parmes, **kwargs)
    elif str(scm_type).upper() in [ICmdScm.GIT, ICmdScm.TGIT]:
        scm_client = CmdGit(_parmes, **kwargs)
    else:
        raise NotImplementedError("%s not supported" % scm_type)
    assert isinstance(scm_client, ICmdScm)
    return scm_client


if __name__ == "__main__":
    pass
