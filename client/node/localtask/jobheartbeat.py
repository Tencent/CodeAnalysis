# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
job任务的心跳进程
应用场景:
localscan扫描时,如果有进程需要发送到server端公共机器执行,此时启动一个job心跳,告诉server本地客户端进程在线.
避免本地退出,而server无感知,一直等待本地客户端取私有进程任务的死等情况.
"""

import time
import logging
import threading

logger = logging.getLogger(__name__)


class JobHeartBeatThread(threading.Thread):
    """
    任务心跳线程,通过JobHeartBeat管理类调用
    """
    def __init__(self, event, org_sid, team_name, repo_id, project_id, job_id, server):
        threading.Thread.__init__(self)
        self._event = event
        self._org_sid = org_sid
        self._team_name = team_name
        self._repo_id = repo_id
        self._project_id = project_id
        self._job_id = job_id
        self._server = server
        self._sleep_interval = 8  # 每 8 秒上报一次心跳

    def run(self):
        while self._event.is_set():
            try:
                self._server.job_heart_beat(self._org_sid, self._team_name, self._repo_id, self._project_id, self._job_id)
            except Exception as err:
                logger.exception(f"job heartbeat error: {str(err)}")
            time.sleep(self._sleep_interval)


class JobHeartBeat(object):
    """
    任务心跳管理类
    """
    def __init__(self, org_sid, team_name, repo_id, project_id, job_id, dog_server):
        """
        初始化
        :param job_id:
        :param dog_server:
        :return:
        """
        self._org_sid = org_sid
        self._team_name = team_name
        self._repo_id = repo_id
        self._project_id = project_id
        self._job_id = job_id
        self._dog_server = dog_server
        self._event = threading.Event()  # 通过event事件控制心跳线程退出

    def start(self):
        """
        启动心跳线程
        :return:
        """
        self._event.set()
        JobHeartBeatThread(self._event, self._org_sid, self._team_name, self._repo_id,
                           self._project_id, self._job_id, self._dog_server).start()

    def stop(self):
        """
        停止心跳线程
        :return:
        """
        # 清除线程信号标记,心跳线程即可退出
        self._event.clear()
