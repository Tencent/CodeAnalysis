# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
本地扫描统计代码行线程
"""


import os
import time
import json
import psutil
import threading

from node.toolloader.loadtool import ToolLoader
from util.pathlib import PathMgr
from task.initparams import InitParams
from util.codecount.codestat import CodeLineCount
from util.logutil import LogPrinter
from node.common.processmgr import ProcMgr


class CountLineThread(threading.Thread):
    """
    统计代码行线程
    """
    def __init__(self, event, task_params, work_dir, result_path):
        """
        构造函数
        :param event:
        :param task_params:
        :param result_path:
        :return:
        """
        threading.Thread.__init__(self)
        self._thread_event = event
        self._task_params = task_params
        self._work_dir = work_dir
        self._result_path = result_path

    def run(self):
        # self._thread_event.set()
        try:
            LogPrinter.info("Start to count code lines...")
            # 删除旧结果文件
            if os.path.exists(self._result_path):
                PathMgr().rmpath(self._result_path)

            # 修改任务参数，确保代码量统计到准确的diff文件范围
            InitParams.prepare_params_about_path_filters(self._task_params)

            # 加载codecount工具环境变量,即加载cloc命令需要的环境变量(cloc是通用工具,已经在之前拉取过,不需要重复拉取)
            ToolLoader(tool_names=["codecount"], include_common=True).set_tool_env()

            code_line_data = CodeLineCount(self._task_params, self._work_dir).run()

            with open(self._result_path, "w") as wf:
                json.dump(code_line_data, wf, indent=2)
        except Exception as err:
            LogPrinter.error("linecount raise error: %s" % err)
            raise
        finally:
            self._thread_event.clear()


class LocalCountLine(object):
    def __init__(self, task_request):
        self._params = task_request["task_params"]
        self._task_dir = task_request["task_dir"]
        self._result_filepath = os.path.join(self._task_dir, "codeline_data.json")
        self._thread_event = threading.Event()

    def start_thread(self):
        """
        启动代码行统计线程
        :return:
        """
        # 启动一个线程,统计代码行
        self._thread_event.set()
        count_line_tread = CountLineThread(self._thread_event, self._params, self._task_dir, self._result_filepath)
        count_line_tread.start()

    def get_result(self):
        """
        获取代码行统计结果
        :return:
        """
        LogPrinter.info("Get code line data...")
        max_wait_time = 60 * 5  # 超时限制 5 min
        sleep_interval = 10      # 每10秒判断一次
        count_time = 0           # 计时器

        stat_result = None
        while self._thread_event.is_set():
            LogPrinter.info("代码统计任务仍在执行,等待任务结束...(等待超时5min)")
            time.sleep(sleep_interval)
            count_time += sleep_interval
            # 如果累计时间大于等于日志打印间隔,打印日志,并重置累计时间
            if count_time >= max_wait_time:
                LogPrinter.info("代码行统计超时,不再等待统计结果...")
                self._thread_event.clear()   # 中止掉代码统计任务线程
                # scc进程可能未正常退出，增加杀进程逻辑
                self.kill_scc_process()
                break

        if os.path.exists(self._result_filepath):
            with open(self._result_filepath, 'r') as fp:
                stat_result = json.load(fp)
                if stat_result:
                    LogPrinter.info(f"本次分析代码行数: {stat_result.get('filtered_total_line_num')}")
                    LogPrinter.info(f"全量代码行数: {stat_result.get('total_line_num')}")
        else:
            LogPrinter.warning("%s结果文件不存在,未获取到代码行统计数据." % self._result_filepath)

        return stat_result

    def kill_scc_process(self):
        scc_workdir = PathMgr().format_path(self._task_dir)
        pids = psutil.pids()
        for pid in pids:
            try:
                # 运行时候可能刚好有个进程退出，导致出现找不到进程错误
                # 2020/4/28 windows的进程命令不一样，并且杀进程时候不一定三个子进程已经起起来
                p = psutil.Process(pid)
                # children = p.children()
                # LogPrinter.info(f"pid: {pid}")
                # LogPrinter.info(f"pname: {p.name()}")
                if p.name().lower().startswith("scc") and " ".join(p.cmdline()).find(scc_workdir) != -1:
                    LogPrinter.info(f"find and kill scc process, pid: {pid}, "
                                    f"pname: {p.name()}, cmdline: {' '.join(p.cmdline())}")
                    ProcMgr().kill_proc_famliy(pid)
            except Exception as e:
                LogPrinter.warning("kill scc process failed: %s" % str(e))
