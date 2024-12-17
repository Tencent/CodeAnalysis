# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
RequestModify
"""
import os
import logging

from node.app import settings
from util.taskscene import TaskScene
from node.common.taskdirmgr import TaskDirCtl
from util.crypto import Crypto

logger = logging.getLogger(__name__)


class RequestModify(object):
    @staticmethod
    def add_params(task_request, job_context, scm_info, pre_cmd, build_cmd, project_path_filters, compare_branch):
        task_params = task_request.get("task_params")
        task_params["scm_initial_last_revision"] = job_context.get("scm_initial_last_revision")
        task_params["path_filters"] = project_path_filters
        task_params["scm_url"] = scm_info.scm_url
        task_params["scm_type"] = scm_info.scm_type
        task_params["project_id"] = job_context["project_id"]
        task_params["repo_id"] = job_context["repo_id"]
        task_params["team_name"] = job_context["team_name"]
        task_params["org_sid"] = job_context["org_sid"]

        # 使用本地设置的前置命令和编译命令
        if pre_cmd:
            task_params["pre_cmd"] = pre_cmd
        if build_cmd:
            task_params["build_cmd"] = build_cmd
        # MR参数
        if compare_branch:
            task_params['ignore_branch_issue'] = compare_branch
            task_params['ignore_merged_issue'] = True

    @staticmethod
    def modify_task_request(task_request, token, server_url, source_dir, scm_info, scm_auth_info, create_from):
        """
        向task_request中添加参数
        :param task_request: dict, 任务参数
        :return:
        """
        # 添加task_scene信息,标记任务运行场景
        task_request['task_params']['task_scene'] = TaskScene.LOCAL
        # 添加create_from参数
        task_request['task_params']['created_from'] = create_from
        # 将token, server_url放到task_params中,供task进度上报和代码行上报使用
        task_request['task_params']['token'] = Crypto(settings.PASSWORD_KEY).encrypt(token)
        task_request['task_params']['server_url'] = server_url
        # 添加 source_dir 和 scm_type
        if source_dir:
            task_request['task_params']['source_dir'] = source_dir
            task_request['task_params']['scm_type'] = scm_info.scm_type
        # 添加 scm_revision
        task_request['task_params']['scm_revision'] = scm_info.scm_revision
        # 添加 scm_username 和 scm_password
        task_request['task_params']['scm_username'] = scm_auth_info.username
        if scm_auth_info.password:
            task_request['task_params']['scm_password'] = Crypto(
                settings.PASSWORD_KEY).encrypt(scm_auth_info.password)
        else:
            task_request['task_params']['scm_password'] = scm_auth_info.password

    @staticmethod
    def modify_local_task_request(task_request, task_name_id_maps, job_id, ssh_file, token, server_url,
                                  source_dir, scm_info, scm_auth_info, create_from):
        """
        本地任务,向task_request中添加参数
        :param task_request:
        :return:
        """
        RequestModify.modify_task_request(task_request, token, server_url, source_dir, scm_info, scm_auth_info, create_from)
        # 添加 task_dir 信息
        task_name = task_request["task_name"]
        task_id = task_name_id_maps.get(task_name)
        task_dir, task_id = TaskDirCtl().acquire_task_dir(task_id)
        task_request['id'] = task_id
        task_request['task_dir'] = task_dir
        task_request['task_params']['task_id'] = task_id
        task_request["task_params"]['job_id'] = job_id

        # 添加本地的 ssh_file
        task_request['task_params']['ssh_file'] = ssh_file

    @staticmethod
    def modify_pri_task_request(task_request, token, server_url, source_dir, scm_info, scm_auth_info, create_from):
        """
        私有任务,向task_request中添加参数
        :param task_request:
        :return:
        """
        RequestModify.modify_task_request(task_request, token, server_url, source_dir, scm_info, scm_auth_info, create_from)

        # 在request中添加 task_dir 信息
        task_id = task_request["id"]
        task_dir, task_id = TaskDirCtl().acquire_task_dir(task_id)
        task_request['task_dir'] = task_dir
        task_request['task_params']['task_id'] = task_id
        task_request["task_params"]['job_id'] = task_request['job']

        if not os.path.exists(task_dir):
            os.makedirs(task_dir)
