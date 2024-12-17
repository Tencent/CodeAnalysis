# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
CodeCountTask
"""

import json
import logging
from node.localtask.requestmodify import RequestModify
from node.localtask.runtask import SingleTaskRuner

logger = logging.getLogger(__name__)


class CodeCountTask(object):
    @staticmethod
    def run_count_line_task(request_list, task_name_id_maps, job_id, scm_auth_info, token, server_url, source_dir,
                            scm_info, origin_os_env, create_from):
        """
        统计代码行
        :param request_list:
        :return:
        """
        request = request_list[0].copy()  # 要用copy,以免影响原字典数据
        request["task_name"] = "linecount"
        request["processes"] = ["analyze"]
        request["execute_processes"] = ["analyze"]
        # 修正工具展示名称
        if "checktool" in request["task_params"]:
            request["task_params"]["checktool"]["display_name"] = "LineCount"
            request["task_params"]["checktool"]["show_display_name"] = True
        # 完善task request字段
        RequestModify.modify_local_task_request(request, task_name_id_maps, job_id,
                                                scm_auth_info.ssh_file,
                                                token, server_url, source_dir, scm_info,
                                                scm_auth_info, create_from)
        # 执行单个任务扫描
        logger.info("启动 linecount 工具统计代码行...")
        task = SingleTaskRuner(request, env=origin_os_env).run()
        with open(task.response_file, 'r') as fp:
            task_result = json.load(fp)
            # 代码行和scm数据保存在结果字典的"result"下的"result"字段中
            response_data = task_result["result"]["result"]
            code_line_count = response_data["code_line"]
            scm_info.scm_time = response_data["scm_info"]["scm_time"]
            if code_line_count:
                logger.info(f"本次分析代码行数: {code_line_count.get('filtered_total_line_num')}")
                logger.info(f"全量代码行数: {code_line_count.get('total_line_num')}")
        return code_line_count
