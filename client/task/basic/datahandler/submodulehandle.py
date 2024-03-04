# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
用于对submodule文件进行判断处理
"""


import os
import logging
import threading

from queue import Queue
from multiprocessing import cpu_count

from task.scmmgr import SCMMgr
from util.envset import EnvSetting
from task.basic.datahandler.handlerbase import HandlerBase

logger = logging.getLogger(__name__)

NO_SUBMODULE_HANDLE = 0
NORMAL_SUBMODULE_HANDLE = 1
CCN_SUBMODULE_HANDLE = 2


class SubmoduleHandle(HandlerBase):
    def run(self, params):
        if not EnvSetting.SUBMODULE_MODE:
            return params

        # 当SUBMODULE_MODE为on时候，获取子模块文件信息
        if self.handle_type == NO_SUBMODULE_HANDLE:
            return params
        if self.handle_type == NORMAL_SUBMODULE_HANDLE:
            return self._normal_handle(params)
        if self.handle_type == CCN_SUBMODULE_HANDLE:
            return self._ccn_handle(params)

    def _normal_handle(self, params):
        """

        :param params:
        :return:
        """
        logger.info("start: submodule handle.")

        issues = params["result"]
        params["result"] = self._common_handle(issues, params)
        logger.info("finished: submodule handle.")
        return params

    def _ccn_handle(self, params):
        """
        由于结构不一样
        :param params:
        :return:
        """
        logger.info("start: ccn submodule handle.")
        issues = params["result"]["detail"]
        params["result"]["detail"] = self._common_handle(issues, params)
        logger.info("finished: ccn submodule handle.")
        return params

    def _common_handle(self, issues, params):
        """
        当SUBMODULE_MODE为on时候，获取子模块文件信息
        :param issues:
        :param params:
        :return:
        """
        # 初始化scm模块
        scm_mgr = SCMMgr(params)
        que = Queue()

        def filte_worker():

            while not que.empty():
                fileissue = que.get()
                path = fileissue.get("path", False)
                if not path:
                    que.task_done()
                    continue

                try:
                    # 将子仓库模块的issue字段放到版本库检查这里，主要是考虑到这里是处理文件且确认文件的过程
                    submodule_info = scm_mgr.get_submodule_info(path)
                    if submodule_info:
                        logger.info("submodule path: %s" % path)
                        logger.info("submodule info: %s" % submodule_info)
                        fileissue["scm_url"] = submodule_info["url"]
                        fileissue["scm_rev"] = submodule_info["rev"]
                        fileissue["rel_path"] = os.path.relpath(path, submodule_info["path"])
                except Exception as err:
                    logger.warning("submodule path: %s exception: %s" % (path, err))

                que.task_done()

        thread_num = cpu_count()
        for fileissue in issues:
            que.put(fileissue)
        for _ in range(thread_num):
            t = threading.Thread(target=filte_worker, name="filte_worker")
            t.daemon = True
            t.start()
        que.join()

        return issues

    @staticmethod
    def get_tool_handle_type_name():
        return "set_submodule_handle"
