# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
本地任务执行器,只执行本地配置好的项目的扫描
"""
import json
import logging

from node.app import settings
from util import errcode
from util.crypto import Crypto
from util.exceptions import ResfulApiError
from util.scmurlmgr import BaseScmUrlMgr, ScmUrlMgr

logger = logging.getLogger(__name__)


class ResultSender(object):
    # 扫描方式：增量扫描 | 全量扫描
    SCAN_TYPE = {"incr_scan": 1, "total_scan": 2}  # 增量扫描  # 全量扫描

    def __init__(self, scm_info, total_scan, code_line_count, job_start_time, create_from, ssh_file,
                 dog_server, job_web_url, proj_id):
        self.scm_info = scm_info
        self._total_scan = total_scan
        self._code_line_count = code_line_count
        self._job_start_time = job_start_time
        self._create_from = create_from
        self._ssh_file = ssh_file
        self._dog_server = dog_server
        self._job_web_url = job_web_url
        self._proj_id = proj_id

    def send_result_to_server(self, repo_id, job_id, proj_conf, proj_scan_succ, proj_scan_result, org_sid, team_name):
        """上传扫描结果到server

        :param job_id: 任务id
        :param proj_conf: dict, 从server获取的项目配置信息
        :param proj_scan_succ: 整个项目扫描是否成功
        :param proj_scan_result: list, 项目扫描结果
        :return: job_id, scan_id
        """
        format_scm_url = self.scm_info.scm_url
        # 判断如果本地url是ssh鉴权方式
        ssh_scm_type = BaseScmUrlMgr.check_ssh_scm_type(self.scm_info.scm_url)
        # 转换为http格式(因为server端暂不支持ssh格式的url)
        if ssh_scm_type:
            scm_url_mgr = ScmUrlMgr(self.scm_info.scm_type).get_scm_url_mgr()
            format_scm_url = scm_url_mgr.ssh_to_http(self.scm_info.scm_url)
        proj_result = proj_conf
        proj_result["job_context"]["scm_url"] = format_scm_url
        proj_result["job_context"]["scm_revision"] = self.scm_info.scm_revision
        if self._total_scan:
            proj_result["job_context"]["scan_type"] = self.SCAN_TYPE["total_scan"]
        else:
            proj_result["job_context"]["scan_type"] = self.SCAN_TYPE["incr_scan"]

        # 增加本次扫描的代码统计量
        if self._code_line_count:
            proj_result["job_context"].update(self._code_line_count)

        # 增加本次扫描的代码版本对应的提交时间
        if self.scm_info.scm_time:
            proj_result["job_context"]["scm_time"] = self.scm_info.scm_time

        # 增加创建时间和来源
        proj_result["job_context"]["start_time"] = self._job_start_time
        proj_result["job_context"]["time_format"] = "%Y-%m-%d %H:%M:%S"
        proj_result["job_context"]["created_from"] = self._create_from

        for task_result in proj_scan_result:
            task_name = task_result.task_name
            request_file = task_result.request_file
            response_file = task_result.response_file
            log_url = task_result.log_url
            result_data_url = task_result.data_url
            with open(request_file, "r") as rf:
                task_request = json.load(rf)
            with open(response_file, "r") as rf:
                task_response = json.load(rf)
            result_code = task_response["status"]
            result_msg = task_response["message"]
            task_version = task_response["task_version"]

            for task in proj_result["tasks"]:
                if task["task_name"] == task_name:
                    task["result_code"] = result_code
                    task["result_msg"] = (
                        result_msg if len(result_msg) <= 256 else result_msg[:256]
                    )
                    task["result_data_url"] = result_data_url
                    task["log_url"] = log_url
                    task["finished_processes"], task["progress_rate"] = \
                        self.__calculate_succ_processes(result_code,
                                                        task_request["execute_processes"],
                                                        task["processes"])
                    task["task_version"] = task_version
                    # 增加执行时间
                    task["start_time"] = task_response.get("start_time")
                    task["end_time"] = task_response.get("end_time")
                    task["time_format"] = task_response.get("time_format")

        for task in proj_result["tasks"]:
            # 如果本次扫描失败(即存在一个任务失败)
            if not proj_scan_succ:
                if "result_code" not in task:
                    # 未执行的任务都设置为取消异常
                    task["result_code"] = errcode.E_NODE_TASK_CANCEL
                    task["result_msg"] = "其他任务异常,本次扫描取消."
                    task["result_data_url"] = None
                    task["log_url"] = None
                    task["finished_processes"] = task["processes"]
                    task["progress_rate"] = 100
                elif task["result_code"] == 0:
                    # 已执行且成功的任务,不管是否所有子进程已执行完,都设置进度为100%,因为不需要继续跑了
                    task["finished_processes"] = task["processes"]
                    task["progress_rate"] = 100
            else:  # 如果扫描未失败
                if "result_code" not in task:
                    # 未执行的任务,进度置为0
                    task["finished_processes"] = []
                    task["progress_rate"] = 0

            # 如果指定了ssh file,所有task的params中添加ssh_file,ssh_key,ssh_url字段
            if self._ssh_file:
                ssh_file_path = self._ssh_file
                with open(ssh_file_path, "r", encoding="utf-8") as rf:
                    text = rf.read()
                    ssh_key = Crypto(settings.PASSWORD_KEY).encrypt(text)
                    task["task_params"]["ssh_key"] = ssh_key
                    task["task_params"]["ssh_file"] = ssh_file_path
                    task["task_params"]["ssh_url"] = self.scm_info.scm_url

            task["task_params"]["scm_username"] = ""
            task["task_params"]["scm_password"] = ""
            task["task_params"]["use_source"] = True

        try:
            # 强制上传结果,支持并发任务
            proj_result["force_create"] = True
            job_id, scan_id = self._dog_server.send_proj_result(repo_id, self._proj_id, job_id,
                                                                proj_result, org_sid, team_name)
            return job_id, scan_id
        except ResfulApiError as err:
            err_msg = "上传扫描结果失败!\n%s" % err.msg
            err_msg += "\n请查看任务执行详情: %s" % self._job_web_url
            raise ResfulApiError(err_msg)

    def __calculate_succ_processes(self, result_code, execute_processes, all_processes):
        """
        计算task完成的进程和进度比例
        :param result_code: 任务结果码
        :param execute_processes: list, 执行的任务进程
        :param all_processes: 任务所有进程
        :return: (list, int), 完成的进程(list)和进度比例(1-100的整数)
        """
        if result_code == 0:
            succ_processes_len = len(execute_processes)
            all_processes_len = len(all_processes)
            finished_rate = int(100 * (succ_processes_len / all_processes_len))
            return execute_processes, finished_rate
        else:
            # 扫描失败,完成进程为该任务所有进程(包括不在execute_processes中的进程),进度为100(该任务已完成)
            return all_processes, 100
