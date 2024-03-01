# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""命令行版Scm控制器接口

不建议在上层应用直接导入该模块，可以选择 `import cmdscm`，相关的类已在cmdscm倒入
"""
# -*- -*- -*- -*- -*- -*-
# -*- -*- -*- -*- -*- -*-


import collections
import errno
import os
import re
import shutil
import stat

# -*- 数据结构
"""DiffPath差异文件结构
path: <str> 文件路径
state: <str> 文件变更状态
"""
DiffPath = collections.namedtuple("DiffPath", ["path", "state"])

"""DiffInfo差异代码行号结构
add: <list> 新增的行号列表
delete: <list> 删除的行号列表
"""
DiffInfo = collections.namedtuple("DiffInfo", ["add", "delete"])

"""DiffNumInfo差异代码行数结构
path: <str> 文件路径
add_num: <int> 新增的行数
del_num: <int> 删除的行数
"""
DiffNumInfo = collections.namedtuple("DiffNumInfo", ["path", "add_num", "del_num"])

"""BlameInfo代码信息结构
author: <str> 修改的责任人
email: <str> 修改的责任人邮箱
revision: <str> 修改的版本号（统一为str格式，方便svn和git同时使用）
timestamp: <float> 修改的时间戳
"""
BlameInfo = collections.namedtuple("BlameInfo", ["author", "email", "revision", "timestamp"])

"""LogInfo日志信息结构
author: <str> 提交的责任人
timestamp: <float> 提交的时间戳
message: <str> 提交的备注信息
revision: <str> 提交的版本号（统一为str格式，方便svn和git同时使用）
changed_paths: <list> DiffPath列表，DiffPath包含字段如下:
    path: <str> 文件路径
    state: <str> 文件变更状态
"""
LogInfo = collections.namedtuple("LogInfo", ["author", "email", "timestamp",
                                             "message", "revision", "changed_paths"])

"""Info代码库信息结构
url: <str> 代码库地址
commit_revision: <str> 代码库的版本号（统一为str格式，方便svn和git同时使用）
commit_time: <float> 代码库版本对应的时间戳（注：git获取不到远程仓库的提交时间，默认为""）
commit_author: <str> 代码库版本对应的责任人（注：git获取不到远程仓库的提交责任人，默认为""）
branch: <str> 代码库的分支信息（注：svn分支名称以"^/"开头）
"""
Info = collections.namedtuple("Info", ["url", "commit_revision", "commit_time", "commit_author", "branch"])

"""SubmoduleInfo代码库信息结构
url: <str> 子模块代码库地址
revision: <str> 子模块代码库版本号
path: <str> 子模块存放在主工程的相对路径
"""
SubmoduleInfo = collections.namedtuple("SubmoduleInfo", ["url", "revision", "path"])


# -*- -*- -*- -*- -*- -*- -*- -*- -*- -*- -*- -*- -*- -*- -*- -*-


class ScmCommandError(Exception):
    """Scm 命令执行失败异常

    应用场景：执行 svn/git 命令时svn/git出现错误信息，抛该异常
    """
    pass


class ScmRepoInvalidError(ScmCommandError):
    """Scm 代码库无效异常

    应用场景：当本地代码库不完整或非有效代码库时，抛该异常
    """
    pass


class ScmVersionUnSupportError(ScmCommandError):
    """Scm工具版本不支持异常

    应用场景：
    1. 本地的svn版本执行 info 命令时，没有包含 Relative URL 或 Repository Root
    """


class ScmAuthFailedError(ScmCommandError):
    """Scm 鉴权失败异常
    """


class ScmSSHKeyInvalidError(ScmCommandError):
    """Scm ssh密钥格式无效异常

    应用场景：使用本地的ssh拉取密钥时，提示无效格式，抛该异常
    """


class ScmSSHKeyNotFoundError(ScmCommandError):
    """Scm ssh密钥无法找到异常

    应用场景：本地的Git/SVN使用ssh拉取密钥时，无法找到密钥时，抛该异常
    """


# 兼容老版本
ScmSSHKeyNotFound = ScmSSHKeyNotFoundError


class ScmNotFoundOrNoPermError(ScmCommandError):
    """Scm项目不存在或没有权限异常

    应用场景： Git拉取 Git OA项目时地址不准确或没有权限时，抛该异常
    """


class ScmRevisionNotFoundError(ScmCommandError):
    """Scm版本号不存在异常

    应用场景： Git checkout 指定的版本号不存在时，抛该异常
    """


class ScmPathNotExistError(ScmCommandError):
    """Scm路径不存在异常

    应用场景：Git获取指定的路径不存在，抛该异常
    """


class ScmBranchNotExistError(ScmCommandError):
    """Scm分支不存在异常

    应用场景：Git切换到指定的分支不存在，抛该异常
    """


class ScmNetworkError(ScmCommandError):
    """Scm网络异常

    应用场景：SVN拉取大项目时网络异常，抛该异常
    """


class ICmdScm(object):
    """抽象类
    """

    SVN = "SVN"
    GIT = "GIT"
    TGIT = "TGIT"
    GIT_OAUTH = "GIT-OAUTH"
    ScmParmes = collections.namedtuple("ScmParmes", ["url", "dst", "username", "password"])

    def __init__(self, parmes):
        """构造函数

        :param parmes: <ICmdScm.ScmParmes> Scm版本库URL和本地目录，以及账号密码。
        """
        assert isinstance(parmes, ICmdScm.ScmParmes), "参数错误"
        self.parmes = parmes
        self.print_enable = False
        self.stdout_filepath = "cmdscm_stdout.log"
        self.stderr_filepath = "cmdscm_stderr.log"

    def __convert_base_type__(self, item):
        """基础类型转换

        :param item: <str> 待转换的字符串，例如字符串满足浮点，则转换为浮点，依次类推可自动转换字符串为对应的类型。
        :return: <int>|<float>|<bool>|<None>|<str>
        """
        if re.match(r'^\d+\.\d+$', item): return float(item)
        if re.match(r'^\d+$', item): return int(item)
        if re.match(r'^True$', item, re.I): return True
        if re.match(r'^False$', item, re.I): return False
        if re.match(r'|'.join(['^None$', '^NULL$']), item, re.I): return None
        return item

    def _base_error_callback(self, line, datadict):
        """通用ErrorLine回调（目标是降低上层应用的代码）

        :param line: <str> 发生error时回调的当前行
        :param datadict: <dict> 该buffer在本类中初始化，并传给SubProcC，再回调回来。
        """
        if line != '':
            errlines = datadict.get("errlines", list())
            errlines.append(line)
            datadict.update({"errlines": errlines})

    def _remove_path(self, path):
        """移除指定目录

        :param path: <str> 指定目录
        """

        def error_handler(func, _path, err_info):
            """错误处理

            :param func: <func> 删除函数
            :param _path: <str> 待删除的路径
            :param err_info: <list> 错误信息
            """
            etype = err_info[0]
            err = err_info[1]
            if issubclass(etype, OSError) and err.errno == errno.EACCES:
                # change readonly to writable, this is required for readonly file in windows
                os.chmod(_path, stat.S_IWRITE)
                func(_path)
            else:
                raise err

        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path, onerror=error_handler)

    def check_path_start_with_src_root(self, path):
        """判断指定路径是否包含源码根目录

        :param path: <str> 指定路径
        :return: <boolean> True表示指定路径包含了源码根目录，False表示指定路径不包含源码根目录
        """
        path = path.replace(os.sep, '/')
        _working_path = self._working_path.replace(os.sep, '/')
        if path.startswith(_working_path):
            return True
        else:
            return False

    def get_rel_path_with_src_root(self, path):
        """获取源码目录内绝对路径相对于源码根目录的路径信息

        :param path: <str> 指定路径
        :return: <str> 指定路径相对源码根目录的路径信息
        """
        if self.check_path_start_with_src_root(path):
            return os.path.relpath(path.replace(os.sep, '/'), self._working_path.replace(os.sep, '/'))
        else:
            return path.replace(os.sep, '/')

    def get_abs_path_with_src_root(self, path):
        """获取指定路径在源码库内的绝对路径

        :param path: <str> 指定路径
        :return: <str> 指定路径在源码库内的绝对路径
        """
        if not self.check_path_start_with_src_root(path):
            return os.path.join(self._working_path, path)
        else:
            return path

    def info(self, remote, interval):
        """Info 命令，获取代码目录的基本信息

        :param remote: <boolean> True表示获取远程代码库的基本信息，False表示获取本地代码库的基本信息
        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        :return: <Info> Info对象，包含字段如下:
            url: <str> 代码库地址
            commit_revision: <str> 代码库的版本号（统一为str格式，方便svn和git同时使用）
            commit_time: <float> 代码库版本对应的时间戳（注：git获取不到远程仓库的提交时间，默认为""）
            commit_author: <str> 代码库版本对应的责任人（注：git获取不到远程仓库的提交责任人，默认为""）
            branch: <str> 代码库的分支信息（注：svn分支名称以"^/"开头）
        """
        raise NotImplementedError()

    def info_by_remote(self, interval):
        """Info 命令，获取远程代码目录的基本信息

        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        :return: <Info> Info对象，包含字段如下:
            url: <str> 代码库地址
            commit_revision: <str> 远程代码库的版本号（统一为str格式，方便svn和git同时使用）
            commit_time: <float> 远程代码库版本对应的时间戳（注：git获取不到远程仓库的提交时间，默认为""）
            commit_author: <str> 远程代码库版本对应的责任人（注：git获取不到远程仓库的提交责任人，默认为""）
            branch: <str> 远程代码库的分支信息（注：svn分支名称以"^/"开头）
        """
        raise NotImplementedError()

    def info_by_local(self, interval):
        """Info 命令，获取本地代码目录的基本信息

        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        :return: <Info> Info对象，包含字段如下:
            url: <str> 代码库地址
            commit_revision: <str> 本地代码库的版本号（统一为str格式，方便svn和git同时使用）
            commit_time: <float> 本地代码库版本对应的时间戳
            commit_author: <str> 本地代码库版本对应的责任人
            branch: <str> 本地代码库的分支信息（注：svn分支名称以"^/"开头）
        """
        raise NotImplementedError()

    def check_auth_with_cache(self, interval):
        """判断本地缓存的鉴权是否有效
        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        :return: <boolean> True表示本地缓存的鉴权信息有效，False表示本地缓存的鉴权信息无效或无缓存
        """
        raise NotImplementedError()

    def check_auth(self, raise_exception, interval):
        """判断输入的帐号和密码或指定的SSH私钥是否有效
        :param raise_exception: <boolean> True表示抛出异常，False表示不抛出异常
        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        :return: <boolean> True表示指定的鉴权有效，False表示指定的鉴权无效
        """
        raise NotImplementedError()

    def can_reuse_by(self, scm_url):
        """判断本地代码的地址是否与指定scm_url相同

        :param scm_url: <str> 代码库地址
        :return: <boolean> True表示相同可复用，False表示不相同不可复用
        """
        raise NotImplementedError()

    def checkout(self, revision, callback, enable_submodules, enable_lfs, interval):
        """检出源码库到本地目录
        如果本地不存在则拉取，如果本地已存在，则更新

        :param revision: <str> 指定代码库版本
        :param callback: <str> 用户自定义回调函数
        :param enable_submodules: <boolean> 拉取子模块开关
        :param enable_lfs: <boolean> 拉取lfs开关
        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        """
        raise NotImplementedError()

    def update(self, revision, callback, enable_submodules, enable_lfs,
               enable_reset, enable_checkout, interval):
        """更新本地代码库到指定版本

        :param revision: <str> 指定代码库版本
        :param callback: <str> 用户自定义回调函数
        :param enable_submodules: <boolean> 拉取子模块开关
        :param enable_lfs: <boolean> 拉取lfs开关
        :param enable_reset: <boolean> 重置开关
        :param enable_checkout: <boolean> checkout开关
        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        """
        raise NotImplementedError()

    def blame(self, path, revision, ignore_whitespace, include_externals, include_email, interval):
        """获取文件的blame信息, 返回blame信息列表
        注：include_externals 暂时只对Git代码库有效

        :param path: <str> 指定代码文件路径
        :param revision: <str> 指定代码库版本
        :param ignore_whitespace: <boolean> 在与父版本比较中是否忽略空格，True表示忽略，False表示不忽略，默认不忽略
        :param include_externals: <boolean> True表示支持子模块的blame，False表示不支持子模块的blame
        :param include_email: <boolean> True表示包含负责人邮件信息，False表示不包含邮件信息
        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        :return: <list> BlameInfo列表，BlameInfo包含字段如下:
            author: <str> 修改的责任人
            revision: <str> 修改的版本号（统一为str格式，方便svn和git同时使用）
            timestamp: <float> 修改的时间戳
        """
        raise NotImplementedError()

    def diff_summarize(self, path, start_revision, end_revision, include_externals, rename, interval):
        """获取版本差异摘要，返回差异列表
        注：include_externals 暂时只对Git代码库有效

        :param path: <str> 支持文件夹或具体的文件
        :param start_revision: <str> 起始版本号
        :param end_revision: <str> 结束版本号
        :param include_externals: <boolean> True表示支持子模块的blame，False表示不支持子模块的blame
        :param rename: <boolean> True表示显示重命名的内容，False表示不显示重命名的内容
        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        :return: <list> DiffPath列表，DiffPath包含字段如下:
            path: <str> 文件路径，文件路径为相对于当前代码库根目录的路径
            state: <str> 文件变更状态，字段值为 mod/del/add 其中一项
        """

    def diff(self, path, start_revision, end_revision, include_externals, interval):
        """获取版本差异化内容

        :param path: <str> 指定代码文件路径
        :param start_revision: <str> 指定代码库起始版本
        :param end_revision: <str> 指定代码库结束版本
        :param include_externals: <boolean> True表示支持获取子模块的文件，False表示不支持获取子模块的文件
        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        :return: <str> 版本差异内容
        """
        raise NotImplementedError()

    def diff_lines(self, path, start_revision, end_revision, interval):
        """获取版本差异化内容中新版本新增的行号和删除的行号

        :param path: <str> 指定代码文件路径
        :param start_revision: <str> 指定代码库起始版本
        :param end_revision: <str> 指定代码库结束版本
        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        :return: <DiffInfo> DiffInfo对象，包含字段如下：
                add: <list> 新增的行号列表
                delete: <list> 删除的行号列表
        """
        raise NotImplementedError()

    def diff_linenum(self, revision, path, include_merge, interval):
        """获取指定版本指定路径增加和删除的行数

        :param revision: <str> 指定版本号
        :param path: <str> 指定路径，默认为空（path为空，则获取当前路径下所有的变更信息）
        :param include_merge: <Boolean> True表示包含Merge版本的变更行数，False表示不包含Merge版本的变更行数
        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        :return: <list> DiffNumInfo对象列表，包含字段如下：
                            path: <str> 路径
                            add_num: <int> 增加的行数
                            del_num: <int> 删除的行数
        """
        raise NotImplementedError()

    def get_file(self, path, revision, to_path, include_externals, interval):
        """获取指定版本文件，保存到指定路径

        :param path: <str> 指定代码文件路径
        :param revision: <str> 指定代码库起始版本
        :param to_path: <str> 存储该文件的指定路径
        :param include_externals: <boolean> True表示支持获取子模块的文件，False表示不支持获取子模块的文件
        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        """
        raise NotImplementedError()

    def cat_file(self, path, revision, interval=180):
        """获取指定版本文件

        :param path: <str> 支持具体的文件
        :param revision: <str> 指定版本号
        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        :return: <str> 文件内容
        """
        raise NotImplementedError()

    def log(self, path, start_revision, end_revision, limit, interval):
        """获取指定版本区间的提交日志 - 注意：start_revision <= end_revision

        :param path: <str> 指定代码文件路径
        :param start_revision: <str> 指定代码库起始版本
        :param end_revision: <str> 指定代码库结束版本
        :param limit: <int> 限制返回的log个数
        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        :return: <list> LogInfo列表，LogInfo包含字段如下:
            author: <str> 提交的责任人
            timestamp: <float> 提交的时间戳
            message: <str> 提交的备注信息
            revision: <str> 提交的版本号（统一为str格式，方便svn和git同时使用）
            changed_paths: <list> DiffPath列表，DiffPath包含字段如下:
                path: <str> 文件路径，文件路径为相对于当前代码库根目录的路径
                state: <str> 文件变更状态，字段值为 mod/del/add 其中一项
        """
        raise NotImplementedError()

    def get_file_list(self, path, include_externals, interval):
        """获取指定目录下在代码库中包含的文件列表

        :param path: <str> 指定本地代码库目录
        :param include_externals: <boolean> True表示包含外链文件，False表示不包含外链文件
        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        :return: <list> 文件名列表，文件路径为相对于当前代码库根目录的路径
        """
        raise NotImplementedError()

    def get_uncommit_files(self, path, unversioned, interval):
        """获取未提交的文件列表

        :param path: <str> 指定本地代码库目录
        :param unversioned: <boolean> True表示包含未在代码库的文件，False表示不包含未在代码库的文件
        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        :return: <list> DiffPath列表，DiffPath字段如下:
            path: <str> 文件路径，文件路径为相对于当前代码库根目录的路径
            state: <str> 文件变更状态，字段值为 mod/del/add/unversioned/mission/conflict 其中一项
        """
        raise NotImplementedError()

    def check_versioned_file(self, path, include_externals, external_files, interval):
        """检查指定文件是否在版本库中

        :param path: <str> 指定本地代码库中的文件
        :param include_externals: <boolean> True表示外链文件，False表示不包含外链文件，默认为False
        :param external_files: <list> 指定的外链文件列表，默认为None
        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        :return: <Boolean> True表示文件在版本库中，False表示文件不在版本库中
        """
        raise NotImplementedError()

    def ls_tree(self, path=None, revision=None, recursive=False, interval=180):
        """获取指定路径下的子目录和文件列表

        :param path: <str> 指定本地代码库中的文件
        :param path: <str> 指定路径
        :param revision:  <str> 指定版本号
        :param recursive: <boolean> True表示递归获取子目录下的文件，False表示不递归，只适用Git
        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        :return: <Boolean> True表示文件在版本库中，False表示文件不在版本库中
        :return: <list> 名称及类型，[{"name": "xx", "type": "file or dir"}]
        """
        raise NotImplementedError()

    def clean_submodules(self, interval):
        """清理子模块

        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        """
        raise NotImplementedError()

    def cleanup(self, path, interval):
        """解锁仓库

        :param path: <str> 指定路径
        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        """
        raise NotImplementedError()

    def clean(self, path, interval):
        """清除指定代码库目录中非版本控制的文件

        :param path: <str> 指定本地代码库目录
        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        """
        raise NotImplementedError()

    def is_source_dir(self, interval):
        """检查是否是一个包含源码的目录

        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        :return: <boolean> True表示本地为源码目录，False表示本地不是源码目录
        """
        raise NotImplementedError()

    def remove(self):
        """删除本地源码和scm的相关数据
        """
        raise NotImplementedError()

    def get_external_files(self, interval):
        """获取当前代码库所有外链文件列表

        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        :return: <list> 外链文件列表，文件路径为相对于当前代码库根目录的路径
        """
        raise NotImplementedError()

    def check_merged_revision(self, revision, interval):
        """检查指定版本号是当前分支还是其他分支的

        :param revision: <str> 指定代码库版本
        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        :return: <boolean> True 表示为其他分支的，False表示为当前分支的
        """
        raise NotImplementedError()

    def list_revisions(self, branch, first_parent=False, interval=180):
        """获取指定分支的版本号列表

        :param branch: <str> 指定分支名称
        :param first_parent: <boolean> 是否筛选仅当前分支引入的版本号，默认为不筛选
        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        :return: <list> 版本号列表
        """
        raise NotImplementedError()

    def set_credential_store(self, store_file, interval):
        """【Git专用】设置Git凭证存储模式

        :param store_file: <str> 存储凭证的文件路径
        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        """
        raise NotImplementedError()

    def set_credential_cache(self, timeout=3600, interval=180):
        """【Git专用】设置Git凭证存储模式

        :param timeout: <int> 存储凭证缓存时间长度，单位为秒
        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        """
        raise NotImplementedError()

    def unset_credential_helper(self, interval):
        """【Git专用】清理Git凭证存储模式

        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        """
        raise NotImplementedError()

    def get_submodule_infos(self):
        """【Git专用】获取子模块的url、版本号和路径信息（后续支持SVN）

        :return: <list> SubmoduleInfo列表，SubmoduleInfo包含字段如下:
                        url: <str> 子模块代码库地址
                        revision: <str> 子模块代码库版本号
                        path: <str> 子模块存放在主工程的相对路径
        """
        raise NotImplementedError()

    def revision_range(self, path, start_revision, end_revision, limit=0, interval=180):
        """获取指定路径的版本号区间

        :param path: <str> 支持文件夹或具体的文件
        :param start_revision: <str> 起始版本号，默认为起始版本号
        :param end_revision: <str> 结束版本号，默认为HEAD
        :param limit: <int> 每次限制获取的log个数，默认为0（即不限制）
        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        :return: <list> 版本号区间列表
        """
        raise NotImplementedError()

    def revision_lt(self, start_revision, end_revision, interval):
        """比较版本号大小

        :param start_revision: <str> 指定代码库起始版本
        :param end_revision: <str> 指定代码库结束版本
        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        :return: <boolean> True表示 start_revision < end_revision，False表示 start_revision >= end_revision
        """
        raise NotImplementedError()

    def get_revision_time(self, revision):
        """获取指定版本号的提交时间
        :param revision: <str> 版本号
        :return: <float> 提交的时间
        """
        raise NotImplementedError()

    def get_merge_revision(self, parent_branch, source_branch, interval):
        """【Git专用】获取指定分支最近合并父分支的版本号

        :param parent_branch: <str> 父分支
        :param source_branch: <str> 源分支
        :param interval: <int> 进程卡住超出该值（秒），则视为超时
        :return: <str> 最近一次合并版本号
        """
        raise NotImplementedError()

# -*- -*- -*- -*- -*- -*- -*- -*- -*- -*- -*- -*- -*- -*- -*- -*-
