# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
任务进度上报管理

新增进度上报方法:
   1.在InfoType类中增加一个上报信息实例,比如Sourceload
   2.调用Reporter类的update_task_progress方法进行上报
        reporter = Reporter(request).update_task_progress(InfoType.Sourceload)
        reporter.update_task_progress(InfoType.Sourceload)
"""


import logging
import collections

from node.app import settings, persist_data
from util.api.dogserver import RetryDogServer
from util.crypto import Crypto
from util.taskscene import TaskScene
from node.quicktask.quickscan import QuickScan

logger = logging.getLogger(__name__)

# 上报信息格式,包含message(str),percent(int)
ReportInfo = collections.namedtuple("ReportInfo", ["message", "percent"])


class InfoType(object):
    """进度上报信息类型,只包含上报信息类变量
       统一管理所有进度上报信息,新增的在这里更新
    """
    # 任务初始化阶段
    TaskStart = ReportInfo("开始执行子任务", 1)
    LoadTool = ReportInfo("更新扫描工具", 2)
    # 编译阶段
    CompileCacheSource = ReportInfo("编译阶段: 应用缓存数据", 10)
    CompileSourceUpdate = ReportInfo("编译阶段: 开始更新代码", 12)
    CompileSourceReLoad = ReportInfo("编译阶段: 代码更新失败，重新拉取代码", 15)
    CompileSourceCheckout = ReportInfo("编译阶段: 开始拉取代码", 16)
    CompileTask = ReportInfo("编译阶段: 开始项目编译", 20)
    # 分析阶段
    AnalyzeCacheSource = ReportInfo("分析阶段: 应用缓存数据", 40)
    AnalyzeSourceUpdate = ReportInfo("分析阶段: 开始更新代码", 42)
    AnalyzeSourceReLoad = ReportInfo("分析阶段: 代码更新失败，重新拉取代码", 45)
    AnalyzeSourceCheckout = ReportInfo("分析阶段: 开始拉取代码", 46)
    AnalyzeTask = ReportInfo("分析阶段: 开始项目分析", 50)
    # 结果处理阶段
    DataHandleCacheSource = ReportInfo("结果处理阶段: 应用缓存数据", 70)
    DataHandleSourceUpdate = ReportInfo("结果处理阶段: 执行代码更新", 72)
    DataHandleSourceReLoad = ReportInfo("结果处理阶段: 代码更新失败，重新拉取代码", 75)
    DataHandleSourceCheckout = ReportInfo("结果处理阶段: 开始拉取代码", 76)
    DataHandleTask = ReportInfo("结果处理阶段: 开始处理结果", 80)
    FormatTask = ReportInfo("结果处理阶段: 结果格式化", 85)
    FilterTask = ReportInfo("结果处理阶段: 前置过滤", 88)
    BlameTask = ReportInfo("结果处理阶段: 责任人获取", 90)
    PostFilterTask = ReportInfo("结果处理阶段: 后置过滤", 95)
    # 任务收尾阶段
    SendResult = ReportInfo("上传结果", 98)
    TaskDone = ReportInfo("子任务执行结束", 100)


class Reporter(object):
    """任务进度上报类
    """
    def __init__(self, task_params):
        self._task_params = task_params
        self._task_scene = task_params.get('task_scene', None)

    def update_task_progress(self, info):
        """向server上报,更新任务执行进度

        :param info: 上报信息Info实例
        :return:
        """
        # test任务无需上报,直接返回
        if self._task_scene and self._task_scene in [TaskScene.TEST]:
            return
        if QuickScan.is_quick_scan():
            return
        try:
            # 从param中获取server_url
            server_url = self._task_params.get("server_url", None)
            # 从param中获取token并解密
            encrypted_token = self._task_params.get("token", None)
            token = Crypto(settings.PASSWORD_KEY).decrypt(encrypted_token)

            dog_server = RetryDogServer(server_url, token).get_api_server(retry_times=0)
            # 非节点模式,NODE_ID字段传参为None
            node_id = persist_data.get('NODE_ID') if self._task_scene == TaskScene.NORMAL else None
            dog_server.update_task_progress(self._task_params,
                                            node_id,
                                            info.message,
                                            info.percent)
        except Exception as err:
            logger.exception('Update_task_progress fail. upload msg:%s', info.message)
