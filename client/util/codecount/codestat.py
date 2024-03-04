# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
统计代码行数
"""


import os
import logging

from task.scmmgr import SCMMgr
from util.pathfilter import FilterPathUtil
from util.codecount.scc import SccHandler
from util.pathlib import PathMgr

logger = logging.getLogger(__name__)


class CodeLineCount(object):
    """
    代码行统计
    """
    def __init__(self, task_params, work_dir=None):
        self._task_params = task_params
        if work_dir:
            self._work_dir = work_dir
        else:
            task_dir = task_params.get('task_dir')
            logger.info("task params taskdir: %s" % task_dir)
            if task_dir:
                self._work_dir = task_dir
            else:
                self._work_dir = os.path.abspath(os.getcwd())

    def run(self):
        try:
            incr_scan = self._task_params['incr_scan']
            source_dir = self._task_params['source_dir']
            scc_handler = SccHandler(self._work_dir)
            filter_handler = FilterPathUtil(self._task_params)
            wanted_exts = scc_handler.get_scc_supported_ext()
            relpos = len(source_dir) + 1

            try:
                if incr_scan:
                    diffs = SCMMgr(self._task_params).get_scm_diff()
                    toscans = [os.path.join(source_dir, diff.path) for diff in diffs if
                               diff.path.lower().endswith(wanted_exts) and diff.state != 'del']
                    # filter include and exclude path
                    filtered_files = filter_handler.get_include_files(toscans, relpos)
                else:  # 全量扫描
                    if filter_handler.is_filter_empty():  # 过滤条件为空，filtered_files传空
                        filtered_files = None
                    else:
                        toscans = PathMgr().get_dir_files(source_dir, wanted_exts)
                        filtered_files = filter_handler.get_include_files(toscans, relpos)
                        if len(filtered_files) == len(toscans):  # 如果过滤后文件数和过滤前相同，filtered_files传空
                            filtered_files = None
            except:
                # 获取过滤后的文件时出现异常（比如增量扫描last revision不存在，无法得到diff文件列表），此时不计算过滤，按全量数据处理
                logger.exception("CodeLineCount get filtered files error, skip. set filtered_files=None.")
                filtered_files = None

            result = scc_handler.source_dir_stat(source_dir, filtered_files)
        except:
            # 出现异常，返回空数据
            logger.exception("count line encounter error, return empty data!")
            result = {
                "code_line_num": 0,
                "comment_line_num": 0,
                "blank_line_num": 0,
                "total_line_num": 0,
                "filtered_code_line_num": 0,
                "filtered_comment_line_num": 0,
                "filtered_blank_line_num": 0,
                "filtered_total_line_num": 0
            }
        # logger.info(">>> result: %s" % result)
        return result


if __name__ == '__main__':
    pass
