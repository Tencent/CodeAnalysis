# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
RunTaskMgr
"""

import copy
import logging

from node.app import settings
from node.localtask.requestmodify import RequestModify
from node.localtask.localreport import LocalReport
from node.localtask.runtask import InOrderTasksRunner
from node.localtask.serverquery import ServerQuery
from node.localtask.resultsender import ResultSender
from util import errcode
from util.exceptions import NodeError
from util.codecount.localcount import LocalCountLine
from node.localtask.scmrevision import ScmRevisionCheck
from node.localtask.codecounttask import CodeCountTask

logger = logging.getLogger(__name__)


class RunTaskMgr(object):
    def __init__(self, source_dir, total_scan, proj_id, job_id, repo_id, token, dog_server, server_url, job_web_url,
                 scm_client, scm_info, scm_auth_info, task_name_id_maps, remote_task_names, origin_os_env,
                 job_start_time, create_from, scan_history_url, report_file, org_sid, team_name):
        self._source_dir = source_dir
        self._total_scan = total_scan
        self._proj_id = proj_id
        self._job_id = job_id
        self._repo_id = repo_id
        self._token = token
        self._dog_server = dog_server
        self._server_url = server_url
        self._job_web_url = job_web_url
        self._scm_client = scm_client
        self._scm_info = scm_info
        self._scm_auth_info = scm_auth_info
        self._task_name_id_maps = task_name_id_maps
        self._remote_task_names = remote_task_names
        self._origin_os_env = origin_os_env
        self._job_start_time = job_start_time
        self._create_from = create_from
        self._scan_history_url = scan_history_url
        self._report_file = report_file
        self._org_sid = org_sid
        self._team_name = team_name
        self._local_task_dirs = []
        self._code_line_count = {}

    def scan_project(self, execute_request_list, proj_conf):
        """
        根据参数对项目进行扫描
        :param execute_request_list: list, 当前可以在本地直接执行的任务参数列表
        :param proj_conf: dict, 项目配置
        :return:
        """
        codecount_handler = None

        # 如果任务列表不为空,且没有任务需要发送到常驻节点执行,才需要统计代码行
        if execute_request_list and not self._remote_task_names:
            if self._source_dir:
                task_request = copy.deepcopy(execute_request_list[0])  # 深度copy,以免影响原字典数据
                RequestModify.modify_local_task_request(task_request, self._task_name_id_maps, self._job_id,
                                                        self._scm_auth_info.ssh_file,
                                                        self._token, self._server_url, self._source_dir, self._scm_info,
                                                        self._scm_auth_info)
                codecount_handler = LocalCountLine(task_request)
                codecount_handler.start_thread()
            else:
                self._code_line_count = CodeCountTask.run_count_line_task(execute_request_list, self._task_name_id_maps,
                                                                          self._job_id,
                                                                          self._scm_auth_info,
                                                                          self._token, self._server_url,
                                                                          self._source_dir, self._scm_info,
                                                                          self._origin_os_env)

        for task_request in execute_request_list:
            # 完善task request字段
            RequestModify.modify_local_task_request(task_request, self._task_name_id_maps, self._job_id,
                                                    self._scm_auth_info.ssh_file, self._token,
                                                    self._server_url, self._source_dir, self._scm_info,
                                                    self._scm_auth_info)

        proj_scan_succ, proj_scan_result, self._local_task_dirs, error_code, error_msg = InOrderTasksRunner(
            execute_request_list,
            self._origin_os_env,
            self._job_web_url,
            self._proj_id).run()

        if proj_scan_succ:
            # 判断扫描前后scm revision是否匹配,如果扫描过程中代码版本有更新,则任务失败
            scm_revision_mgr = ScmRevisionCheck(self._dog_server, self._source_dir, self._total_scan, self._scm_info,
                                                self._scm_client, self._report_file, self._server_url,
                                                self._scan_history_url, self._job_web_url, self._repo_id, self._proj_id,
                                                self._org_sid, self._team_name)
            is_revision_same, error_msg = scm_revision_mgr.is_revision_unchanged()
            if not is_revision_same:
                logger.error(error_msg)
                # 重置error_code
                raise NodeError(code=errcode.E_NODE_TASK_CONFIG, msg=error_msg)

        # 获取统计代码行线程的执行结果
        if codecount_handler:
            self._code_line_count = codecount_handler.get_result()

        # 上传扫描结果给server,在server端注册开启一个job任务
        result_sender = ResultSender(self._scm_info, self._total_scan, self._code_line_count,
                                     self._job_start_time, self._create_from, self._scm_auth_info.ssh_file,
                                     self._dog_server, self._job_web_url, self._proj_id)
        job_id, scan_id = result_sender.send_result_to_server(self._repo_id, self._job_id, proj_conf, proj_scan_succ,
                                                              proj_scan_result, self._org_sid, self._team_name)

        if proj_scan_succ:
            # 从server端查询本次扫描结果
            query_timeout = settings.POLLING_TMEOUT
            scan_result = ServerQuery.query_result(self._dog_server, self._server_url, self._repo_id, self._proj_id,
                                                   scan_id, query_timeout, self._org_sid, self._team_name,
                                                   self._job_web_url, True)

            LocalReport.output_report(scan_result, self._report_file)
        else:
            scan_result = {
                "status": "error",
                "error_code": error_code,
                "url": self._job_web_url,
                "text": "扫描失败",
                "description": error_msg,
                "scan_report": {}
            }
            LocalReport.output_report(scan_result, self._report_file)
