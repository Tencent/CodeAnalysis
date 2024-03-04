# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
源码库的操作功能
"""
import logging
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ScmPlatformEnum:
    """Scm平台枚举
    """
    GIT_OA = 1
    GIT_TENCENT = 2
    CODING = 3
    GITHUB = 4
    GITEE = 5
    GITLAB = 6
    OTHER = 7


SCM_PLATFORM_CHOICES = (
    (ScmPlatformEnum.GIT_OA, "tgit"),
    (ScmPlatformEnum.GIT_TENCENT, "tgitsaas"),
    (ScmPlatformEnum.CODING, "coding"),
    (ScmPlatformEnum.GITHUB, "github"),
    (ScmPlatformEnum.GITEE, "gitee"),
    (ScmPlatformEnum.GITLAB, "gitlab"),
    (ScmPlatformEnum.OTHER, "other"),
)

SCM_PLATFORM_NUM_AS_KEY = dict(SCM_PLATFORM_CHOICES)
SCM_PLATFORM_NAME_AS_KEY = dict((v, k) for k, v in SCM_PLATFORM_NUM_AS_KEY.items())
NEED_REFRESH_SCM_PLATFORMS = [ScmPlatformEnum.GITEE, ScmPlatformEnum.GITLAB]


class ScmUrlFormatter(object):

    @classmethod
    def get_scm_url(cls, scm_type, url):
        """格式化代码库地址
        :param scm_type: str, scm类型
        :param url: str，代码库地址
        :return: str，格式化后的代码库地址
        """
        if scm_type.lower() == "svn":
            return cls.get_svn_url(url)
        elif scm_type.lower() == "git":
            return cls.get_git_url(url)
        else:
            raise Exception('not yet support scm_type: %s' % scm_type)

    @classmethod
    def get_svn_url(cls, scm_url):
        """格式化SVN代码库地址
        """

        if scm_url.startswith("svn+ssh"):
            scm_url = re.sub("^svn+ssh", "http", scm_url)

        parsed_uri = urlparse(scm_url.strip())
        if not parsed_uri.scheme:
            scm_url = "http://%s" % scm_url
            parsed_uri = urlparse(scm_url)
        host_name, path = parsed_uri.hostname, parsed_uri.path
        if not path:
            logger.warning("svn scm_url[%s] 无法解析出repository" % scm_url)
            return None

        return "http://%s/%s" % (host_name, path.strip('/'))

    @classmethod
    def format_git_basic_url(cls, scm_url):
        """初步格式化URL

        :param scm_url: str，代码库地址
        :return: str，初步格式化后的代码库地址
        """
        scm_url = scm_url.split('#', 1)[0]
        scm_url = scm_url.strip().rstrip('/')
        if scm_url.startswith("https://"):
            scm_url = scm_url.replace("https://", "http://")
        elif scm_url.startswith("git@"):
            scm_url = scm_url.replace(':', '/', 1).replace("git@", "http://")
        elif scm_url.startswith("ssh://git@"):
            # ssh://git协议转换成http会去掉端口号
            scm_url = re.sub(r"(:\d+/)", "/", scm_url.replace("ssh://git@", "http://"))
        elif scm_url.startswith("ssh://"):
            scm_url = re.sub(r"(:\d+/)", "/", scm_url.replace("ssh://", "http://"))
        elif not scm_url.startswith(("https://", "http://")):
            scm_url = "http://%s" % scm_url
        return scm_url

    @classmethod
    def remove_git_suffix(cls, scm_url):
        """移除.git后缀
        :param scm_url:
        :return:
        """
        if scm_url.endswith(".git"):
            scm_url = scm_url[:-4]
        return scm_url

    @classmethod
    def get_git_url(cls, scm_url):
        """格式化外部Git代码库地址

        :param scm_url: str，代码库地址
        :return: str，代码库地址
        """
        scm_url = cls.format_git_basic_url(scm_url)
        # 使用python标准库分割url
        # 注：如果url前面没有scheme，会出现 hostname 为空的情况
        parsed_uri = urlparse(scm_url)
        host_name, port, path = parsed_uri.hostname, parsed_uri.port, parsed_uri.path

        # 提取项目group名称和项目名
        if not path:
            logger.warning("git scm_url[%s] 无法解析出repository" % scm_url)
            return None
        project_name = path.strip('/')

        if port:
            host_name = "%s:%s" % (host_name, port)

        # 可能存在使用@来连接分支
        if "@" in project_name:
            project_name = project_name.split('@')[0]

        # 可能存在.git后缀
        project_name = cls.remove_git_suffix(project_name)
        return "http://%s/%s" % (host_name, project_name)

    @classmethod
    def get_git_ssh_url(cls, scm_url):
        """格式化SSH URL
        """
        if "#" in scm_url:
            scm_url = scm_url.split('#')[0]
        # 可能存在.git后缀
        scm_url = cls.remove_git_suffix(scm_url)
        return scm_url

    @classmethod
    def check_git_ssh_url(cls, scm_url):
        """检查是否为git ssh格式的代码库地址
        """
        if scm_url.startswith(("git@", "ssh://")):
            return True
        else:
            return False

    @classmethod
    def check_svn_ssh_url(cls, scm_url):
        """检查是否为svn ssh格式的代码库地址
        """
        if scm_url.startswith("svn+ssh:"):
            return True
        else:
            return False

    @classmethod
    def check_ssh_url(cls, scm_type, scm_url):
        """检查是否为ssh格式的代码库地址
        """
        if scm_type.lower() == "svn":
            return cls.check_svn_ssh_url(scm_url)
        elif scm_type.lower() == "git":
            return cls.check_git_ssh_url(scm_url)
        else:
            raise Exception('not yet support scm_type: %s' % scm_type)


class ScmError(Exception):
    """Scm错误基类, 并提供下面的参数

    :param msg(unicode): 错误消息
    """

    def __init__(self, msg):
        if isinstance(msg, bytes):
            msg = msg.decode()
        super(ScmError, self).__init__(msg)
        self.msg = msg


class ScmConnectionError(ScmError):
    """Scm链接错误
    """
    pass


class ScmClientError(ScmError):
    """Scm用户输入错误
    """
    pass


class ScmAccessDeniedError(ScmClientError):
    """Scm访问权限被拒
    """
    pass


class ScmNotFoundError(ScmClientError):
    """访问不存在的文件
    """
    pass


class ScmErrorHandler(object):

    @classmethod
    def svn_error_handler(cls, error):
        """SVN 错误处理
        :param error: jsonrpclib.jsonrpc.ProtocolError - 错误信息
        """
        if hasattr(error, "faultString"):
            err_msg = error.faultString
        else:
            err_msg = str(error)
        logger.exception("scmproxy error message: %s" % err_msg)
        err_msg_dict = {
            "Authentication failed": ScmClientError("SVN帐号密码错误"),
            "Revision doesn't exist.": ScmNotFoundError("SVN版本号不存在"),
            "No permission.": ScmAccessDeniedError("SVN无权访问"),
            "File doesn't exist.": ScmNotFoundError("SVN路径不存在"),
            "Project doesn't exist.": ScmNotFoundError("SVN路径不存在"),
        }
        for pattern, error_type in err_msg_dict.items():
            if re.search(pattern, err_msg):
                raise error_type

        raise ScmError("未知错误: %s" % err_msg)

    @classmethod
    def git_error_handler(cls, error):
        """Git 错误处理
        :param error: jsonrpclib.jsonrpc.ProtocolError - 错误信息
        """
        if hasattr(error, "faultString"):
            err_msg = error.faultString
        else:
            err_msg = str(error)
        logger.exception("scmproxy error message: %s" % err_msg)

        err_msg_dict = {
            "Path .* does not exist": ScmNotFoundError("文件不存在"),
            "SHA .* could not be resolved": ScmNotFoundError("Git版本号不存在"),
            "Could not read from remote repository": ScmClientError("帐号密码错误"),
            "Revision doesn't exist": ScmNotFoundError("Git版本号不存在"),
            "File doesn't exist": ScmNotFoundError("文件不存在"),
            "Branch doesn't exist": ScmNotFoundError("分支不存在"),
            "Authentication failed": ScmClientError("帐号密码错误"),
            "Project doesn't exist or no project code access permission": ScmAccessDeniedError("代码库路径可能不存在或无访问权限"),
            "Project can't found": ScmNotFoundError("代码库路径可能不存在"),
            "timed out": ScmConnectionError("获取代码信息耗时较久，请稍后再试")
        }
        for pattern, error_type in err_msg_dict.items():
            if re.search(pattern, err_msg):
                raise error_type
        raise ScmError("未知错误: %s" % err_msg)


class IScmClient(object):
    """Scm库操作接口定义
    """

    def __init__(self, scm_url, username=None, password=None, **kwargs):
        """
        :param scm_url: str, scm库地址
        :param username: str, 用户名
        :param password: str, 密码
        """
        self._repository = None
        self._branch = None

    @property
    def latest_revision(self):
        """最新版本号
        """
        raise NotImplementedError()

    @property
    def repository(self):
        """代码库地址
        """
        if not self._repository:
            self._repository = self.get_repository()
        return self._repository

    def get_repository(self):
        """获取代码库地址
        """
        raise NotImplementedError()

    @property
    def branch(self):
        """分支
        """
        if not self._branch:
            self._branch = self.get_branch()
        return self._branch

    def get_branch(self):
        """分支名称
        """
        raise NotImplementedError()

    def get_ssh_url(self):
        """获取ssh格式的代码库地址
        """
        raise NotImplementedError()

    def auth_check(self):
        """SCM鉴权校验

        :return: boolean, True表示鉴权信息正常，False表示鉴权信息异常
        :raise: ScmError错误
        """
        raise NotImplementedError()

    def branch_check(self):
        """SCM分支校验

        :return: boolean, True表示分支存在，False表示分支不存在
        :raise: ScmError错误
        """
        raise NotImplementedError()

    def cat(self, path, revision):
        """获取文件内容

        :param path: 文件路径
        :param revision: 文件版本
        :type revision: str
        :return: 文件内容
        """
        raise NotImplementedError()

    def get_revision_datetime(self, revision):
        """获取指定版本的创建时间
        :param revision: 文件版本
        :return: datetime对象
        """
        raise NotImplementedError()
