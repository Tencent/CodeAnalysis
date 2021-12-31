# -*- encoding: utf-8 -*-
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

from task.model.compile import CompileTask
from task.model.analyze import AnalyzeTask
from task.model.datahandle import DataHandleTask
from util.exceptions import SourceMgrError
from task.basic.incsourcemgr import IncSourceMgr
from node.app import settings

DATA_DIR = settings.DATA_DIR

logger = logging.getLogger(__name__)


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
        :return: 加入source_dir,work_dir
        """
        logger.info("pre_compile start.")
        self.__checkout_source_dir()
        logger.info("pre_compile done.")
        return self.params

    def _pre_analyze(self):
        """
        :return: 加入source_dir,work_dir
        """
        logger.info("pre_analyze start.")
        if self.params.get("tool_skip"):
            logger.info("满足skip条件,跳过pre_analyze步骤...")
            return self.params
        if self.have_last:
            pass
        else:
            self.__checkout_source_dir()
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
            self.__checkout_source_dir()
        return self.params

    def _done_compile(self, result):
        """
        编译结束的资源操作：
        1. 加入本地增量资源数据库
        2. 向后续task传递完成编译的状态与路径信息
        :param result:
        :return:
        """
        logger.info("done_compile start.")
        # 加入本地增量资源数据库
        inc_path_dict = {}
        for key in self.tool.set_inc_source_path_list():
            inc_path_dict[key] = self.params[key]
        self.inc_src.insert_src_info(inc_path_dict)
        # 通过修改此处，让puppy支持只执行compile+datahandle
        self.params["result"] = result
        return self.params

    def _done_analyze(self, result):
        """
        免编译的工具可以缓存数据，用于增量扫描
        :param result:
        :return:
        """
        self.params["result"] = result
        logger.info("done_analyze done.")
        return self.params

    def _done_result(self, result):
        """

        :param result:
        :return:
        """
        return result

    def __checkout_source_dir(self):
        logger.info("start __checkout_source_dir.")

        if self.params.get("source_dir", False):
            logger.info("__checkout_source_dir done. source_dir insert env. sourcedir: %s" % self.params["source_dir"])
            os.environ["SOURCE_DIR"] = self.params["source_dir"]
        else:
            raise SourceMgrError("__checkout_source_dir error, please check!")


if __name__ == "__main__":
    pass
