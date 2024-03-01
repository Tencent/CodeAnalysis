# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
资源管理类用于进行各个task的数据过滤与管理
资源管理的设计有两个思路：1. 针对不同类型的task进行区别处理 （优势，实现简单，劣势，可扩展性差，维护难度高）
                          2. 资源管理类不对task进行区分，自主实现一个规则，所有task通过遵循规则进行资源管理

本模块功能：
    1. 基础资源管理：资源清理等
    2. 数据传递，不同task、机器之间的数据传递

"""

import logging
import os
import time

from task.model.compile import CompileTask
from task.model.analyze import AnalyzeTask
from task.model.datahandle import DataHandleTask
from util.exceptions import SourceMgrError
from task.basic.incsourcemgr import IncSourceMgr
from node.app import settings
from util.pathlib import PathMgr
from util.taskscene import TaskScene
from util.codecount.repoter import CodeLineReporter
from util.reporter import Reporter, InfoType
from task.scmmgr import SCMMgr
from util.cmdscm import ScmCommandError
from task.transfermgr import TransferMgr

DATA_DIR = settings.DATA_DIR

logger = logging.getLogger(__name__)


class SourceReporter(object):
    """
    代码相关的进度上报
    """
    def __init__(self, task_type, task_params):
        self.task_type = task_type
        self.params = task_params

    def cache_report(self):
        """
        进度上报：应用缓存代码
        :return:
        """
        if self.task_type is CompileTask:
            Reporter(self.params).update_task_progress(InfoType.CompileCacheSource)
        elif self.task_type is AnalyzeTask:
            Reporter(self.params).update_task_progress(InfoType.AnalyzeCacheSource)
        elif self.task_type is DataHandleTask:
            Reporter(self.params).update_task_progress(InfoType.DataHandleCacheSource)

    def update_report(self):
        """
        进度上报：更新代码
        :return:
        """
        if self.task_type is CompileTask:
            Reporter(self.params).update_task_progress(InfoType.CompileSourceUpdate)
        elif self.task_type is AnalyzeTask:
            Reporter(self.params).update_task_progress(InfoType.AnalyzeSourceUpdate)
        elif self.task_type is DataHandleTask:
            Reporter(self.params).update_task_progress(InfoType.DataHandleSourceUpdate)

    def update_retry_report(self):
        """
        进度上报：更新代码失败后,重新拉取代码
        :return:
        """
        if self.task_type is CompileTask:
            Reporter(self.params).update_task_progress(InfoType.CompileSourceReLoad)
        elif self.task_type is AnalyzeTask:
            Reporter(self.params).update_task_progress(InfoType.AnalyzeSourceReLoad)
        elif self.task_type is DataHandleTask:
            Reporter(self.params).update_task_progress(InfoType.DataHandleSourceReLoad)

    def checkout_report(self):
        """
        进度上报：拉取代码
        :return:
        """
        if self.task_type is CompileTask:
            Reporter(self.params).update_task_progress(InfoType.CompileSourceCheckout)
        elif self.task_type is AnalyzeTask:
            Reporter(self.params).update_task_progress(InfoType.AnalyzeSourceCheckout)
        elif self.task_type is DataHandleTask:
            Reporter(self.params).update_task_progress(InfoType.DataHandleSourceCheckout)


class SourceManager(object):
    def __init__(self, params, task_type, tool, have_next=False, have_last=False):
        """
        资源管理构造函数
        :param params: 传入的参数信息
        :param task_type: task类型
        """
        self.task_type = task_type
        self.params = params
        self.tool = tool
        # 表明task所处的状态，用于控制数据传递
        self.have_next = have_next
        self.have_last = have_last
        self.inc_src = IncSourceMgr(self.params["scm_url"], self.tool.set_inc_source_type())
        self.src_loader = SourceDirLoader(params, task_type, tool, self.inc_src)

    def pre_task(self):
        """
        task前置函数，用于数据拉取与数据传递接收
        :return: 传递给task的参数
        """
        if self.task_type is CompileTask:
            return self._pre_compile()
        elif self.task_type is AnalyzeTask:
            return self._pre_analyze()
        elif self.task_type is DataHandleTask:
            return self._pre_result()
        raise SourceMgrError("task类型错误：%s" % str(self.task_type))

    def done_task(self, result):
        """
        task结果处理函数，用于进行数据传递发送与中间数据上报
        :param result:
        :return:
        """
        if self.task_type is CompileTask:
            return self._done_compile(result)
        elif self.task_type is AnalyzeTask:
            return self._done_analyze(result)
        elif self.task_type is DataHandleTask:
            return self._done_result(result)
        raise SourceMgrError("task类型错误：%s" % str(self.task_type))

    def _pre_compile(self):
        """
        编译前置资源操作：
        1. 确认是否有增量资源可以拉取
        2. 确认是否存在远程增量资源可以拉取
        3. 通过scm接口直接拉取代码
        :return: 加入source_dir,work_dir
        """
        logger.info("pre_compile start.")
        self.src_loader.load_source_dir()
        logger.info("pre_compile done.")
        return self.params

    def _pre_analyze(self):
        """
        1. 获取编译后的信息进行资源拉取
        2. 若无编译操作，则需要进行：
            1. 确认是否有增量资源可以拉取
            2. 确认是否存在远程增量资源可以拉取
            3. 通过scm接口直接拉取代码
        :return: 加入source_dir,work_dir
        """
        logger.info("pre_analyze start.")
        if self.params.get("tool_skip"):
            logger.info("满足skip条件,跳过pre_analyze步骤...")
            return self.params
        smi = SourceMiddleInfo(self.params)
        if self.have_last:
            pass
        elif smi.is_marked():
            smi.download()
        else:
            # 免编译工具执行
            self.src_loader.load_source_dir()
        logger.info("pre_analyze done.")
        return self.params

    def _pre_result(self):
        """
        结果处理前，不用做任何资源处理
        :return:
        """
        if self.have_last:
            pass
        else:
            # 复用本地缓存或重新拉取代码
            self.src_loader.load_source_dir()
        return self.params

    def _done_compile(self, result):
        """
        编译结束的资源操作：
        1. 加入本地增量资源数据库
        2. 加入增量资源数据站（取消）
        3. 向后续task传递完成编译的状态与路径信息
        :param result:
        :return:
        """
        logger.info("done_compile start.")
        # 第一步，加入本地增量资源数据库
        inc_path_dict = {}
        for key in self.tool.set_inc_source_path_list():
            inc_path_dict[key] = self.params[key]
        self.inc_src.insert_src_info(inc_path_dict)
        # 通过修改此处，让puppy支持只执行compile+datahandle
        self.params["result"] = result
        # 第二步， 向分析步骤传递完成编译的状态与路径信息
        mid_path_dict = {}
        for key in self.tool.set_mid_source_path_list():
            mid_path_dict[key] = self.params[key]
        if not self.have_next:
            smi = SourceMiddleInfo(self.params)
            logger.info("done_compile done.")
            return smi.upload(mid_path_dict)
        return self.params

    def _done_analyze(self, result):
        """
        免编译的工具可以缓存数据，用于增量分析
        :param result:
        :return:
        """
        logger.info("done_analyze start.")
        smi = SourceMiddleInfo(self.params)
        if not smi.is_marked():
            path_dict = {}
            for key in self.tool.set_inc_source_path_list():
                path_dict[key] = self.params[key]
            self.inc_src.insert_src_info(path_dict)
        self.params["result"] = result
        logger.info("done_analyze done.")
        return self.params

    def _done_result(self, result):
        """
        把结果信息拿出来上报即可，其他的去掉
        :param result:
        :return:
        """
        return result


class SourceDirLoader(object):
    """代码目录拉取、复用或更新"""
    def __init__(self, params, task_type, tool, inc_src):
        self.task_type = task_type
        self.params = params
        self.tool = tool
        self.inc_src = inc_src
        # 是否拉取子模块
        ignore_submodule_clone = self.params.get("ignore_submodule_clone")
        if ignore_submodule_clone:
            self.enable_submodules = False
        else:
            self.enable_submodules = True
        # 是否拉取git lfs, 如果环境变量为False，表示不拉取；如果为True、None或不存在都表示拉取
        lfs_flag = self.params.get("lfs_flag")
        if lfs_flag is False:
            self.enable_lfs = False
        else:
            self.enable_lfs = True

    def load_source_dir(self):
        logger.info("start __checkout_source_dir.")
        if self.params["task_scene"] == TaskScene.LOCAL:
            if "source_dir" in self.params:
                # 只要传入source_dir就必须使用，不传入source_dir才可以使用增量缓存
                if "normal" == self.tool.set_inc_source_type():
                    logger.info("本地项目，直接复用传入的source_dir.")
                    pass  # 直接复用本地资源
                else:
                    # logger.info('本地项目，非normal项目，执行scm.clean后复用sourcedir.')
                    # sm = SCMMgr(self.params)
                    # sm.get_scm_client().clean()
                    logger.info("本地项目，非normal项目，目前已确保是task队列首个执行，因此不做清理。")
            else:
                logger.info("本地项目，直接拉取或复用本地缓存资源.")
                self.__checkout_data()
        else:
            logger.info("常规项目，直接拉取或复用本地缓存资源.")
            self.__checkout_data()

        if self.params.get("source_dir", False):
            logger.info("load_source_dir done. source_dir insert env. sourcedir: %s" % self.params["source_dir"])
            os.environ["SOURCE_DIR"] = self.params["source_dir"]

        else:
            raise SourceMgrError("__checkout_source_dir error, please check!")

        # 启动上报代码行数线程,当前任务可以继续往下走,减少耗时
        CodeLineReporter(self.params).start()

    def __load_user_source_dir(self, user_source_dir):
        """
        如果用户通过环境变量CODEDOG_SOURCE_DIR指定了项目代码目录,直接复用该代码目录
        1. 如果目录已存在,更新代码
        2. 如果该目录不存在,创建目录,拉取代码
        :return:
        """
        logger.info("已设置CODEDOG_SOURCE_DIR环境变量,使用指定的代码目录: %s" % user_source_dir)
        user_source_dir = os.path.expanduser(user_source_dir)
        if os.path.exists(user_source_dir):  # 目录已存在,复用直接更新代码
            self.params["source_dir"] = user_source_dir
            # 上报进度
            SourceReporter(self.task_type, self.params).cache_report()
            self.__retry_update()
        else:  # 目录不存在,尝试创建目录并拉取代码
            try:
                # 创建一个空目录,作为代码存放地址,后面拉代码时检查到目录存在,就不会随机指定一个目录名
                logger.info("指定的代码目录(%s)不存在,开始创建目录..." % user_source_dir)
                os.makedirs(user_source_dir)
                self.params["source_dir"] = user_source_dir
            except Exception as err:
                # 创建目录失败,后面拉代码会随机指定一个目录名
                logger.error("创建目录失败(%s) failed: %s" % (user_source_dir, str(err)))

            # 重新拉取代码
            sm = SCMMgr(self.params)
            self.__retry_checkout(sm)

    def __checkout_data(self):
        """
        直接拉取或复用本地缓存资源
        :return:
        """
        # 从环境变量中获取CODEDOG_SOURCE_DIR（此时task环境变量尚未加载，只能从系统环境变量或进程环境变量中获取）
        user_src_dir = os.getenv("CODEDOG_SOURCE_DIR")
        if user_src_dir:
            self.__load_user_source_dir(user_src_dir)
        elif self.inc_src.inc_src_exist():
            # 上报进度
            SourceReporter(self.task_type, self.params).cache_report()
            path_dict = self.inc_src.get_src_info()
            for key in path_dict.keys():
                self.params[key] = path_dict[key]
            self.__retry_update()
        else:
            # 通过scm拉取代码文件
            scm_mgr = SCMMgr(self.params)
            self.__retry_checkout(scm_mgr)

    def __retry_update(self):
        """
        已有代码目录缓存,更新代码;如果失败,重新拉取;如果再失败,删除目录后重新拉取
        :return:
        """
        sm = SCMMgr(self.params)
        try:
            # 上报进度
            SourceReporter(self.task_type, self.params).update_report()
            # 如果未开启拉取子模块开关,先清理缓存代码目录中的子模块
            if self.params.get("ignore_submodule_clone", False) is True:
                logger.info("clean submodules before update source ...")
                sm.get_scm_client().clean_submodules()
            sm.get_scm_client().update(revision=self.params["scm_revision"],
                                       enable_submodules=self.enable_submodules,
                                       enable_lfs=self.enable_lfs)
        except ScmCommandError:
            logger.exception("update code failed, will retry to checkout after 30s ...")
            time.sleep(30)
            # 上报进度
            SourceReporter(self.task_type, self.params).update_retry_report()
            sm.get_scm_client().remove()
            self.__retry_checkout(sm)

    def __retry_checkout(self, scm_mgr):
        """
        拉取代码到一个新的目录;如果失败,删除代码目录再重新拉取
        :param scm_mgr:
        :return:
        """
        # 上报进度
        SourceReporter(self.task_type, self.params).checkout_report()

        interval = 30  # 重试间隔(单位: 秒)
        retry_max = 2  # 重试次数
        retry_cnt = 0  # 重试计数
        while True:
            try:
                scm_mgr.get_scm_client().checkout(
                    revision=self.params["scm_revision"],
                    enable_submodules=self.enable_submodules,
                    enable_lfs=self.enable_lfs
                )
                if retry_cnt != 0:
                    logger.info("checkout succeed after %d retries.", retry_cnt)
                return
            except ScmCommandError as err:
                logger.warning("checkout fails on error: %s" % str(err))
                if retry_cnt < retry_max:
                    # 先清理代码目录
                    if self.params["scm_type"] in ["git", "tgit"]:
                        PathMgr().rmpath(self.params["source_dir"])
                    elif self.params["scm_type"] == "svn":
                        scm_mgr.get_scm_client().cleanup()

                    # 准备重试
                    retry_cnt += 1
                    interval = interval * retry_cnt  # 重试间隔递增,第一次间隔30s，第二次60s
                    logger.warning("retry after %s seconds..." % interval)
                    time.sleep(interval)
                    continue
                else:
                    logger.warning("checkout still fails after %s retries!" % retry_cnt)
                    raise


class SourceMiddleInfo(object):
    """
    source管理类值传递处理类
    用于将主机ip，与资源路径进行传递
    """

    # 设置一个资源管理的标注字段，传入param
    SOURCE_MID_INFO = "transfer_info"

    def __init__(self, params):
        self.params = params

    def is_marked(self):
        if self.SOURCE_MID_INFO in self.params.keys():
            return True
        return False

    def upload(self, path_dict):
        transfer_info = TransferMgr().upload_file(path_dict)
        if not transfer_info:
            raise SourceMgrError("upload middle data error。 上传跨机器执行所需数据失败，请检查数据通路！")
        self.params[self.SOURCE_MID_INFO] = transfer_info
        return self.params

    def download(self):
        transfer_info = self.params[self.SOURCE_MID_INFO]
        TransferMgr().download_file(transfer_info)
        # transfer_info 格式参考task/transfermgr的注释
        # 将下载的内容载入params中
        path_list = transfer_info.get("path_list", [])
        for path_item in path_list:
            self.params[path_item["params_key_name"]] = os.path.join(DATA_DIR, path_item["rel_path"])
        return True


if __name__ == "__main__":
    pass
