# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - base core
"""

import json
import logging

from apps.codeproj.core.jobmgr import JobManager
from apps.job.core import JobCloseHandler
from apps.job.models import ScanTypeEnum
from apps.job.tasks.jobcheck import start_server_job
from util import errcode
from util.exceptions import CDErrorBase

logger = logging.getLogger(__name__)


def create_local_scan(project, creator, scan_data, created_from="codedog_client", **kwargs):
    """启动扫描

    1. 创建任务和Scan，然后返回job_id,scan_id
    2. 异步获取并更新任务参数
    3. 启动任务

    :param project: Project, 项目
    :param creator: str，创建人
    :param scan_data: dict，扫描数据
        {
            "force_create": True/False，表示是否强制启动
            "incr_scan": True/False，表示是否增量扫描
        }
    :param created_from: web, 创建来源
    :param kwargs:
        - client_flag: boolean, 客户端启动标识
    :return: int,int 任务编号和扫描编号
    """
    tag = scan_data.pop("tag", None)
    labels = scan_data.pop("labels", None)
    task_names = scan_data.pop("task_names", None)
    job_context = {
        "force_create": scan_data.get("force_create", False),
        "incr_scan": scan_data.get("incr_scan", True) is True,
        "created_from": created_from,
        "tag": str(tag) if tag else None,
        "scm_revision": scan_data.get("revision", None),
        "scm_last_revision": scan_data.get("last_revision", None),
        "labels": [label.name for label in labels] if labels else None,
    }
    job_context.update(**scan_data)
    job_manager = JobManager(project)
    logger.info("[Project: %s] 开始初始化任务，任务参数: %s" % (project.id, json.dumps(job_context)))
    scan_type = job_manager.get_scan_type(scan_data, job_context)
    job = job_manager.initialize_job(
        force_create=job_context["force_create"],
        creator=creator, created_from=created_from,
        client_flag=True
    )
    logger.info("[Project: %s] 初始化任务完成，任务编号: %s" % (project.id, job.id))
    try:
        job.context = job_context
        job.save()
        job_manager.create_waiting_scan_on_analysis_server(job, scan_type)
        task_infos = None
        if task_names:
            task_infos = job_manager.init_tasks(job, task_names)
        logger.info("[Project: %s] 创建任务完成: %s，关联扫描编号：%s" % (project.id, job.id, job.scan_id))
        return job.id, job.scan_id, task_infos
    except Exception as err:
        if isinstance(err, CDErrorBase):
            result_msg = err.msg
            result_code = err.code
        else:
            result_msg = "创建扫描异常: %s" % str(err)
            result_code = errcode.E_SERVER_JOB_CREATE_ERROR
        JobCloseHandler.revoke_job(job, result_code=result_code, result_msg=result_msg)
        raise


def create_server_scan(project, creator, scan_data, async_flag=True, **kwargs):
    """异步启动扫描

    1. 创建任务和Scan，然后返回job_id,scan_id
    2. 异步获取并更新任务参数
    3. 启动任务

    :param project: Project, 项目
    :param creator: str，创建人
    :param scan_data: dict，扫描数据
        {
            "force_create": True/False，表示是否强制启动
            "incr_scan": True/False，表示是否增量扫描
        }
    :param async_flag: boolean, 异步启动标识
    :param kwargs:
        - client_flag: boolean, 客户端启动标识
    :return: int,int 任务编号和扫描编号
    """
    tag = scan_data.pop("tag", None)
    labels = scan_data.pop("labels", None)
    job_context = {
        "force_create": scan_data.get("force_create", False),
        "incr_scan": scan_data.get("incr_scan", True) is True,
        "init_scan": scan_data.get("init_scan", False) or kwargs.get("init_scan", False),
        "created_from": scan_data.get("created_from", "tca_web"),
        "tag": str(tag) if tag else None,
        "scm_revision": scan_data.get("revision", None),
        "scm_last_revision": scan_data.get("last_revision", None),
        "labels": [label.name for label in labels] if labels else None,
    }
    job_context.update(**scan_data)
    job_manager = JobManager(project)
    logger.info("开始初始化任务，任务参数: %s" % json.dumps(job_context, indent=2))
    scan_type = job_manager.get_scan_type(scan_data, job_context)
    job = job_manager.initialize_job(
        force_create=job_context["force_create"],
        creator=creator, created_from=job_context["created_from"],
        async_flag=async_flag, client_flag=kwargs.get("client_flag", False)
    )
    try:
        job.context = job_context
        job.save()
        job_manager.create_waiting_scan_on_analysis_server(job, scan_type)
        if async_flag:
            start_server_job.delay(job.id)
        return job.id, job.scan_id
    except Exception as err:  # 访问analyse server异常时，取消任务
        if isinstance(err, CDErrorBase):
            result_msg = err.msg
            result_code = err.code
        else:
            result_msg = "创建扫描异常: %s" % str(err)
            result_code = errcode.E_SERVER_JOB_CREATE_ERROR
        JobCloseHandler.revoke_job(job, result_code=result_code, result_msg=result_msg)
        raise


def create_job(project, job_confs, creator=None, puppy_create=False, **kwargs):
    """
    使用获取的jobconfs来创建扫描任务
    """
    job_manager = JobManager(project)
    job_context = job_confs["job_context"]
    incr_scan = job_context.get("incr_scan", True)
    force_create = job_confs.get("force_create") or job_context.get("force_create", False)
    created_from = job_confs.get("created_from") or job_context.get("created_from") or "codedog_web"
    job_manager.check_job_scm_url(job_context)
    job = job_manager.initialize_job(force_create, creator, created_from)
    job = job_manager.update_job(job, job_confs)
    if kwargs.get("scan_type") is not None:
        scan_type = kwargs["scan_type"]
    else:
        scan_type = ScanTypeEnum.INCRESE if incr_scan else ScanTypeEnum.FULL
    scan = job_manager.create_scan_on_analysis_server(job, job_context, scan_type)
    job_context.update({"scan_id": scan["id"]})
    job_manager.insert_auth_into_job_context(job_context)
    job_manager.create_tasks(job, job_confs, puppy_create)
    return job.id, scan["id"]


def finish_job_from_client(job, project, job_confs, puppy_create=False, **kwargs):
    """
    使用获取的jobconfs来更新扫描任务
    """
    job_manager = JobManager(project)
    job_context = job_confs["job_context"]
    job_manager.check_job_scm_url(job_context)
    job = job_manager.update_job(job, job_confs)
    scan = job_manager.update_scan_revision_on_analysis_server(job, job_context)
    job_context.update({"scan_id": scan["id"]})
    job_manager.insert_auth_into_job_context(job_context)
    job_manager.create_tasks(job, job_confs, puppy_create)
    return job.id, scan["id"]
