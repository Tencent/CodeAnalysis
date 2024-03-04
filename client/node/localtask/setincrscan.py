# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
IncrScanSet
"""


class IncrScanMgr(object):
    @staticmethod
    def set_incr_scan(proj_conf, total_scan):
        job_context = proj_conf["job_context"]
        task_list = proj_conf["tasks"]

        # 如果本地启动参数指定了全量扫描,设置全量扫描标记
        if total_scan:
            job_context["incr_scan"] = False

        for task_request in task_list:
            task_params = task_request["task_params"]

            if total_scan:
                task_params["incr_scan"] = False
                task_params["scm_last_revision"] = ""
            else:
                # 如果本地未指定全量扫描，根据server传递的task_params["incr_scan"]判断是否增量
                # 因为第一次扫描时，由于没有last_revision,无论用户是否指定全量，都需要全量扫描(这个逻辑由server判断)
                # 如果server判定是全量，更新为全量扫描
                if "incr_scan" in task_params:
                    if not task_params["incr_scan"]:
                        total_scan = True
                else:
                    # fix bug - task_params没有incr_scan字段,需要补充
                    task_params["incr_scan"] = True
