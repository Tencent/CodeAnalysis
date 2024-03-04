# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
TaskProcessMgr
"""
import os
import logging

from node.toolloader.loadtool import ToolLoader, ToolConfigLoader
from util.exceptions import NodeError
from util import errcode
from node.common.userinput import UserInput
from util.textutil import StringMgr
from node.localtask.filtermgr import FilterManager
from node.localtask.taskprocessmgr import TaskProcessMgr
from node.localtask.setincrscan import IncrScanMgr
from node.localtask.initjob import JobInit
from node.localtask.scmauthcheck import ScmAuthCheck
from node.localtask.requestmodify import RequestModify
from util.tooldisplay import ToolDisplay
from node.localtask.scmrevision import ScmRevisionCheck
from util.logutil import LogPrinter

logger = logging.getLogger(__name__)


class TaskRequestGenerator(object):
    def __init__(self, dog_server, source_dir, total_scan, scm_info, scm_auth_info,
                 scm_client, report_file, server_url, scan_history_url, job_web_url,
                 exclude_paths, include_paths, pre_cmd, build_cmd, origin_os_env,
                 repo_id, proj_id, org_sid, team_name, create_from, compare_branch):
        self._total_scan = total_scan
        self._source_dir = source_dir
        self._scm_info = scm_info
        self._scm_client = scm_client
        self._report_file = report_file
        self._dog_server = dog_server
        self._server_url = server_url
        self._repo_id = repo_id
        self._proj_id = proj_id
        self._org_sid = org_sid
        self._team_name = team_name
        self._scan_history_url = scan_history_url
        self._job_web_url = job_web_url
        self._scm_info = scm_info
        self._scm_auth_info = scm_auth_info
        self._source_dir = source_dir
        self._ssh_file = scm_auth_info.ssh_file
        self._scm_username = scm_auth_info.username
        self._scm_password = scm_auth_info.password
        self._total_scan = total_scan
        self._create_from = create_from
        self._exclude_paths = exclude_paths
        self._include_paths = include_paths
        self._skip_processes = {}
        self._origin_os_env = origin_os_env
        self._pre_cmd = pre_cmd
        self._build_cmd = build_cmd
        self._remote_task_names = []
        self._compare_branch = compare_branch

    def generate_request(self, proj_conf):
        """
        根据项目配置信息生成任务参数列表
        :param proj_conf: 项目配置信息
        :return: 当前可直接执行的任务参数列表
        """
        job_context = proj_conf["job_context"]

        # 没有指定本地目录的情况下,scm_url为空,使用项目配置的scm_url
        if not self._scm_info.scm_url:
            self._scm_info.scm_url = job_context["scm_url"]
        # 没有指定本地目录的情况下,scm_type为空,使用项目配置的scm_type
        if not self._scm_info.scm_type:
            self._scm_info.scm_type = job_context["scm_type"]

        # 检查代码库的账号密码权限
        ScmAuthCheck(self._scm_info, self._scm_auth_info, self._source_dir).check_scm_authority()

        # 没有指定本地目录(self._source_dir=None)的情况下,scm_revision=None,使用远程仓库最新版本号
        if not self._scm_info.scm_revision:
            # 获取远端代码库的scm信息
            remote_scm_info = UserInput().get_remote_scm_info(scm_type=self._scm_info.scm_type,
                                                              scm_url=self._scm_info.scm_url,
                                                              source_dir=self._source_dir,
                                                              username=self._scm_username,
                                                              password=self._scm_password)
            self._scm_info.scm_revision = remote_scm_info.commit_revision

        task_list = proj_conf["tasks"]

        # 检查当前代码的版本号,判断是否需要扫描
        scm_revision_mgr = ScmRevisionCheck(self._dog_server, self._source_dir, self._total_scan, self._scm_info,
                                            self._scm_client, self._report_file, self._server_url,
                                            self._scan_history_url, self._job_web_url, self._repo_id, self._proj_id,
                                            self._org_sid, self._team_name)
        scm_revision_mgr.check_scm_revision(job_context, task_list)

        # 设置全量/增量扫描参数
        IncrScanMgr.set_incr_scan(proj_conf, self._total_scan)

        task_name_list = [task_request["task_name"] for task_request in task_list]
        if not task_name_list:
            raise NodeError(code=errcode.E_NODE_TASK_CONFIG, msg="任务列表为空,未开启任何检查项,请在扫描设置中开启代码检查或代码度量.")

        # 向server注册一个任务，并启动任务心跳
        job_id, job_heartbeat, task_name_id_maps = JobInit.init_job(self._org_sid, self._team_name, self._dog_server,
                                                                    self._total_scan, self._repo_id, self._proj_id,
                                                                    task_name_list, self._create_from)

        # 根据环境变量判断是否发送给节点执行
        remote_tasks_str = os.environ.get("CODEDOG_REMOTE_TASKS", None)
        if remote_tasks_str:
            logger.info("设置了环境变量CODEDOG_REMOTE_TASKS=%s" % remote_tasks_str)
            self._remote_task_names = StringMgr.str_to_list(remote_tasks_str)
            # 过滤掉不在扫描方案中的工具
            self._remote_task_names = [task_name for task_name in self._remote_task_names if
                                       task_name in task_name_list]
            if self._remote_task_names:
                logger.info("工具(%s)任务将发送到云端扫描." % self._remote_task_names)
            else:
                logger.warning("环境变量CODEDOG_REMOTE_TASKS指定的工具(%s)不在扫描方案中，不需要执行." % remote_tasks_str)

        # 如果未设置CODEDOG_REMOTE_TASKS,且设置了CODEDOG_REMOTE_SCAN环境变量为true|True,表示全部task都发到云端执行
        if not self._remote_task_names:
            remote_scan_env = os.getenv("CODEDOG_REMOTE_SCAN", "false")
            if remote_scan_env in ["true", "True"]:
                self._remote_task_names = task_name_list
                logger.info("设置了环境变量CODEDOG_REMOTE_SCAN, 所有任务(%s)将发送到云端扫描." % self._remote_task_names)

        local_task_names = list(set(task_name_list) - set(self._remote_task_names))
        # 如果不是所有任务都设置了发送给云端执行,即还有本地执行的任务,才需要本地拉取工具,且只拉取需要本地执行的工具
        custom_tools = []
        if local_task_names:
            # 判断如果有自定义工具，需要拉取 customscan 任务所需的工具库
            for tool_name in local_task_names:
                try:
                    __import__("tool." + tool_name)
                except ModuleNotFoundError:
                    # 记录自定义工具列表
                    custom_tools.append(tool_name)
                except:
                    # logger.exception("encounter error.")
                    pass
            # 从git拉取工具配置库,同时拉取公共工具
            ToolConfigLoader().load_tool_config()
            LogPrinter.info(f"Initing other tools ...")
            # 上面已经拉取了commone工具，此处不需要重复拉取，设置include_common=False
            # git拉取不输出日志，因为print输出会覆盖到logging日志
            ToolLoader(tool_names=local_task_names, task_list=task_list, custom_tools=custom_tools,
                       include_common=False).git_load_tools(print_enable=False)

        execute_request_list, self._skip_processes = self._get_execute_request_list(job_context, task_list, self._remote_task_names, custom_tools)

        return execute_request_list, self._skip_processes, job_id, job_heartbeat, task_name_id_maps, self._remote_task_names

    def _get_execute_request_list(self, job_context, task_list, remote_task_names, custom_tools):
        """获取本地执行的任务参数列表"""
        execute_request_list = []

        # 如果本地有指定过滤路径,与server配置的过滤路径合并使用
        if self._exclude_paths or self._include_paths:
            project_path_filters = FilterManager.get_local_filtered_paths(self._include_paths, self._exclude_paths,
                                                                          self._dog_server, self._repo_id,
                                                                          self._proj_id, self._org_sid, self._team_name,
                                                                          job_context["path_filters"])
        else:  # 否则，使用server上的配置的过滤路径
            project_path_filters = job_context["path_filters"]

        for task_request in task_list:
            task_name = task_request["task_name"]
            RequestModify.add_params(task_request, job_context, self._scm_info, self._pre_cmd,
                                     self._build_cmd, project_path_filters, self._compare_branch)
            task_params = task_request.get("task_params")
            task_display_name = ToolDisplay.get_tool_display_name(task_request)

            if task_name in remote_task_names:
                self._skip_processes[task_display_name] = task_request["processes"]
            else:
                supported_processes = TaskProcessMgr.get_supported_processes(self._origin_os_env,
                                                                             task_name, task_params, custom_tools)
                remote_procs = list(set(task_request["processes"]) - set(supported_processes))
                if remote_procs:
                    # raise NodeError(code=errcode.E_NODE_TASK_CONFIG, msg=f"当前环境不支持{task_name}工具步骤:{remote_procs}.")
                    logger.warning(f"当前环境不支持{task_name}工具步骤:{remote_procs}.")
                    self._skip_processes[task_display_name] = remote_procs

                if remote_task_names:
                    task_request["private_processes"] = supported_processes
                else:
                    execute_processes = TaskProcessMgr.get_execute_processes(task_display_name, supported_processes,
                                                                             task_request["processes"])
                    task_request["execute_processes"] = execute_processes
                    # 本地支持但是当前无法执行的进程,设置为私有进程
                    task_request["private_processes"] = list(set(supported_processes) - set(execute_processes))
                    # 有当前可执行的进程,才添加到待执行列表中
                    if execute_processes:
                        execute_request_list.append(task_request)
        return execute_request_list, self._skip_processes
