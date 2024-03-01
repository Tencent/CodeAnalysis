# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
用户输入管理类
"""


import os
import logging

from util.smartinput import SmartInput, InputRetryError
from util import errcode

from util.cmdscm import ScmClient
from util.pathlib import PathMgr
from util.textutil import StringMgr
from util.exceptions import NodeError
from util.languagetype import LanguageType

logger = logging.getLogger(__name__)

class UserInput(object):
    """
    接收用户输入,对输入进行必要的校验和重试
    """
    def __format_language_name(self, input_name):
        """
        格式为server支持的语言名称；如果不支持，返回None
        """
        # 先转换成小写
        lowcase_name = input_name.lower()
        for key, value in LanguageType.LANGUAGE_DICT.items():
            if lowcase_name in value['user_input']:
                return value['server_name']
        # 不支持的语言类型，返回None
        return None

    def format_languages(self, language_str):
        """
        将输入的语言字符串转换为list,并判断是否是支持的语言类型.如果不支持,抛异常
        :param language_str: 语言类型字符串,以英文逗号或分号分隔
        :return: <list>
        """
        # 先转换str为list
        language_list = StringMgr.str_to_list(language_str)
        format_languages = []
        for language in language_list:
            format_name = self.__format_language_name(language)
            if format_name:
                format_languages.append(format_name)
            else:
                message = "不支持的语言类型: %s" % language
                logger.error(message)
                raise NodeError(code=errcode.E_NODE_TASK_CONFIG, msg=message)
        # self._languages 重新赋值,使用标准拼写的语言类型
        return list(set(format_languages))

    def __get_local_scm_info(self, source_dir, scm_type):
        """
        获取本地代码库的scm info
        :param source_dir: 本地代码目录
        :param scm_type: scm类型
        :return: scm info | 如果获取失败,返回None
        """
        try:
            scm_info = ScmClient(scm_type=scm_type,
                                 scm_url="",
                                 source_dir=source_dir,
                                 scm_username="",
                                 scm_password="").info()
            return scm_info
        except Exception as err:
            logger.warning(str(err))
            return None

    def get_remote_scm_info(self, scm_type, scm_url, source_dir, username=None, password=None):
        """
        获取远程代码仓库的scm info信息(需要用户名密码权限)
        :param scm_type:
        :param scm_url:
        :param source_dir:
        :param username:
        :param password:
        :return:
        """
        os.environ.update({"GIT_SSL_NO_VERIFY": "1"})

        try:
            remote_scm_info = ScmClient(
                scm_type=scm_type,
                scm_url = scm_url,
                source_dir=source_dir,
                scm_username=username,
                scm_password=password
            ).info(remote=True)
            return remote_scm_info
        except Exception as err:
            raise NodeError(code=errcode.E_NODE_TASK_SCM_FAILED, msg="获取远端代码库信息失败! %s" % str(err))

    def input_token(self):
        """
        Token 输入
        :return:
        """
        try:
            return SmartInput().input(prompt="认证令牌(Token):")
        except InputRetryError as err:
            logger.warning(str(err))
            return None
        except EOFError as err:
            logger.warning(str(err))
            return None

    def input_proj_id(self):
        """
        proj_id 输入
        :return:
        """
        def check_func(proj_id):
            if proj_id.isdigit():
                return True
            else:
                return False
        try:
            proj_id = SmartInput().input(prompt="项目编号:",
                                     check_func=check_func,
                                     retry_prompt="输入有误,项目编号应该是一个数字!请重新输入:")
            return int(proj_id)
        except InputRetryError as err:
            logger.warning(str(err))
            return None
        except EOFError as err:
            logger.warning(str(err))
            return None

    def input_source_dir(self):
        """
        sourcedir 输入
        :return: sourcedir
        """
        def check_func(source_dir):
            source_dir = PathMgr().format_path(source_dir)
            if os.path.exists(source_dir):
                return True
            else:
                return False
        try:
            source_dir = SmartInput().input(prompt="本地代码目录:",
                                     check_func=check_func,
                                     retry_prompt="路径不存在, 请重新输入:")
            # 格式化目录路径,确保格式唯一
            source_dir = PathMgr().format_path(source_dir)
            return source_dir
        except InputRetryError as err:
            logger.warning(str(err))
            return None
        except EOFError as err:
            logger.warning(str(err))
            return None

    def input_scm_type(self):
        """
        scm_type 输入
        :return:
        """
        def check_func(data):
            if data in ['svn', 'git']:
                return True
            else:
                return False
        try:
            scm_type = SmartInput().input(prompt="代码库类型(svn/git):",
                                     check_func=check_func,
                                     retry_prompt="不支持的代码库类型,请重新输入(svn/git):")
            return scm_type
        except InputRetryError as err:
            logger.warning(str(err))
            return None
        except EOFError as err:
            logger.warning(str(err))
            return None

    def input_user_info(self, scm_type, scm_url):
        """
        username,password 输入
        :param scm_type:
        :param scm_url:
        :return:
        """
        try:
            if not scm_url or not scm_type:  # 如果没有scm_url和scm_type,不能验证权限
                logger.error("scm_url(%s) 或 scm_type(%s) 不能为空!" % (scm_url, scm_type))
                return None

            username = SmartInput().input("Username:")
            password = SmartInput().input("Password:", is_password=True)

            input_times = 3  # 账号密码输入3次错误,直接退出
            # 通过访问远程仓库信息,判断账号密码是否正确

            # 检查输入的账号密码是否有效
            while not ScmClient(scm_type=scm_type,scm_url = scm_url,source_dir=None,
                                scm_username=username,scm_password=password).check_auth():
                input_times -= 1
                if not input_times:
                    # 超过失败重试次数,直接返回
                    logger.error("3次输入错误,退出!")
                    return None
                logger.warning("账号密码不对,请重新输入!")
                username = SmartInput().input("Username:")
                password = SmartInput().input("Password:", is_password=True)
            return {"username": username, "password": password}
        except EOFError as err:
            logger.warning(str(err))
            return None

    def input_languages(self):
        """
        输入语言
        :return: list, 语言列表
        """
        def check_func(input_str):
            try:
                self.format_languages(input_str)
                return True
            except NodeError:
                return False

        try:
            languages = SmartInput().input(prompt="代码语言类型:",
                                           check_func=check_func,
                                           retry_prompt="输入有误!请重新输入:")
            return self.format_languages(languages)
        except InputRetryError as err:
            logger.warning(str(err))
            return None
        except EOFError as err:
            logger.warning(str(err))
            return None
