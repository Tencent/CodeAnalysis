# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
RunTaskMgr
"""

import os
import copy
import json
import logging
import time

from node.app import settings
from node.localtask.requestmodify import RequestModify
from node.localtask.localreport import LocalReport
from node.localtask.runtask import InOrderTasksRunner, ConcurrentTasksRuner
from node.localtask.serverquery import ServerQuery
from node.localtask.resultsender import ResultSender
from util import errcode
from util.exceptions import NodeError
from util.codecount.localcount import LocalCountLine
from node.localtask.scmrevision import ScmRevisionCheck
from node.localtask.codecounttask import CodeCountTask
from node.localtask.runtask import SingleTaskRuner, ResultCheck
from util.tooldisplay import ToolDisplay

logger = logging.getLogger(__name__)


class RunTaskMgr(object):
    def __init__(self, source_dir, total_scan, proj_id, job_id, repo_id, token, dog_server, server_url, job_web_url,
                 scm_client, scm_info, scm_auth_info, task_name_id_maps, remote_task_names, origin_os_env,
                 job_start_time, create_from, scan_history_url, report_file, org_sid, team_name, skip_processes):
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
        self._skip_processes = skip_processes

    def scan_project(self, execute_request_list, proj_conf):
        """
        根据参数对项目进行扫描
        :param execute_request_list: list, 当前可以在本地直接执行的任务参数列表
        :param proj_conf: dict, 项目配置
        :return:
        """
        codecount_handler = None
        proj_scan_result = []

        # 如果任务列表不为空,且没有任务需要发送到常驻节点执行,才需要统计代码行
        if execute_request_list and not self._remote_task_names:
            if self._source_dir:
                task_request = copy.deepcopy(execute_request_list[0])  # 深度copy,以免影响原字典数据
                task_request["task_name"] = "linecount"
                RequestModify.modify_local_task_request(task_request, self._task_name_id_maps, self._job_id,
                                                        self._scm_auth_info.ssh_file,
                                                        self._token, self._server_url, self._source_dir, self._scm_info,
                                                        self._scm_auth_info, self._create_from)
                codecount_handler = LocalCountLine(task_request)
                codecount_handler.start_thread()
            else:
                self._code_line_count = CodeCountTask.run_count_line_task(execute_request_list, self._task_name_id_maps,
                                                                          self._job_id,
                                                                          self._scm_auth_info,
                                                                          self._token, self._server_url,
                                                                          self._source_dir, self._scm_info,
                                                                          self._origin_os_env, self._create_from)

        for task_request in execute_request_list:
            # 完善task request字段
            RequestModify.modify_local_task_request(task_request, self._task_name_id_maps, self._job_id,
                                                    self._scm_auth_info.ssh_file, self._token,
                                                    self._server_url, self._source_dir, self._scm_info,
                                                    self._scm_auth_info, self._create_from)

        # 通过环境变量获取并发执行开关
        concurrent_task_env = os.getenv("TCA_CONCURRENT_SCAN")
        if concurrent_task_env == "False":
            proj_scan_succ, proj_scan_result, self._local_task_dirs, error_code, error_msg = InOrderTasksRunner(
                execute_request_list,
                self._origin_os_env,
                self._job_web_url,
                self._proj_id).run()
        else:
            # 默认启用工具并行执行
            proj_scan_succ, finished_task_results, error_code, error_msg = ConcurrentTasksRuner(execute_request_list,
                                                                                                self._origin_os_env,
                                                                                                self._job_web_url,
                                                                                                self._proj_id).run()
            proj_scan_result.extend(finished_task_results)
            for task_result in finished_task_results:
                task_dir = os.path.dirname(task_result.request_file)
                self._local_task_dirs.append(task_dir)

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
            # 如果有跳过的进程,需要等云端分析完成;同时要轮询server,看是否有私有进程需要执行
            if self._skip_processes:
                logger.info("以下工具进程将发送给云端分析:")
                for tool_display_name, tool_pro_list in self._skip_processes.items():
                    logger.info("%s : %s" % (tool_display_name, tool_pro_list))
                logger.info("云端分析正在进行中,请耐心等待,可查看分析进度: %s", self._job_web_url)

                # 查询并执行需要执行的私有进程
                self._wait_and_run_private_procs(self._proj_id, job_id)

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

    def _wait_and_run_private_procs(self, project_id, job_id):
        """
        轮询并执行私有子进程
        :param job_id:
        :return:
        """
        start_time = time.time()
        timeout = settings.LOCAL_TASK_EXPIRED
        while True:
            now_time = time.time()
            if now_time - start_time > timeout:
                raise NodeError(code=errcode.E_NODE_TASK_EXPIRED, msg=f"任务执行超时(超时限制: {timeout/3600}小时)")
            rt_data = self._dog_server.get_privete_task(self._org_sid, self._team_name, self._repo_id, project_id, job_id)
            if rt_data["state"] == 0:  # 需要等待远端进程完成
                time.sleep(settings.POLLING_INTERVAL)
                continue
            elif rt_data["state"] == 1:  # 有私有任务需要执行
                logger.info("获取到任务,开始处理 ...")
                task_list = rt_data["tasks"]
                for task_request in task_list:
                    RequestModify.modify_pri_task_request(task_request, self._token, self._server_url, self._source_dir,
                                                          self._scm_info, self._scm_auth_info, self._create_from)
                    # 执行单个任务分析
                    task = SingleTaskRuner(task_request, env=self._origin_os_env).run()
                    self._local_task_dirs.append(task_request["task_dir"])
                    # 上传结果
                    code, msg, log_url, data_url, execute_processes, node_task_version = ResultCheck.upload_task_result(task, self._proj_id)

                    # 上报结果给server
                    self._dog_server.send_task_result(task_request['task_params'], job_id, task.task_id, node_task_version, code, data_url, msg, log_url, execute_processes)

                    if task.code is None:
                        with open(task.response_file, 'r') as fp:
                            task_response = json.load(fp)
                            error_code = task_response['status']
                            error_msg = task_response['message']
                    else:
                        error_code = task.code
                        error_msg = task.msg
                    if error_code != 0:  # 有一个任务分析失败,抛异常
                        task_display_name = ToolDisplay.get_tool_display_name(task_request)
                        error_msg = f"任务({task_display_name})分析失败: {error_msg}\n请查看本地日志文件({task.task_log})"
                        error_msg += ",\n或前往 %s (点击异常子任务->下载进程日志)" % self._job_web_url
                        error_msg += "查看失败原因."

                        raise NodeError(code=error_code, msg=error_msg)
            elif rt_data["state"] == 2:  # 已经没有私有任务需要执行
                break
