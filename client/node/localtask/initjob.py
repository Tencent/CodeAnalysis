# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
TaskProcessMgr
"""

from util.logutil import LogPrinter
from node.localtask.jobheartbeat import JobHeartBeat


class JobInit(object):
    @staticmethod
    def init_job(org_sid, team_name, dog_server, total_scan, repo_id, proj_id, task_name_list, create_from):
        """
        注册任务,并启动任务心跳
        :return:
        """
        # 向server注册一个任务
        incr_scan = False if total_scan else True
        init_data = {
            "force_create": True,
            "created_from": create_from,
            "incr_scan": incr_scan,
            "task_names": task_name_list
        }
        job_params = dog_server.init_job(repo_id, proj_id, init_data, org_sid, team_name)
        job_id = job_params["job"]
        task_name_id_maps = job_params["tasks"]

        # 启动任务心跳线程
        LogPrinter.info("Job starts ...")
        job_heartbeat = JobHeartBeat(org_sid, team_name, repo_id, proj_id, job_id, dog_server)
        job_heartbeat.start()
        return job_id, job_heartbeat, task_name_id_maps
