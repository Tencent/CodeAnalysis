# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""Job的tasks模块
"""
# 原生 import
import logging
from datetime import timedelta

# 第三方 import
from django.conf import settings
from django.utils import timezone

# 项目内 import
from apps.job import core
from apps.job.models import Job, Task
from codedog.celery import celery_app
from util import errcode
from util.time import localnow


logger = logging.getLogger(__name__)


@celery_app.task
def start_server_job(job_id):
    """启动任务
    """
    # 判断当前任务的状态是否等待运行
    num = Job.objects.select_for_update().filter(
        id=job_id, state=Job.StateEnum.WAITING
    ).update(state=Job.StateEnum.INITING)
    if num <= 0:
        return
    job = Job.objects.get(id=job_id)
    try:
        from apps.codeproj.core import JobManager
        JobManager(job.project).start_job(job, job.context)
    except Exception as err:
        logger.exception("[Project: %d][Job: %d] start job failed: %s" % (job.project_id, job.id, err))


@celery_app.task
def monitor_initing_job():
    """监控当前初始化的任务

    任务初始化超时则重试，超时时间是20分钟
    """
    timeout_time = timezone.now() - timedelta(minutes=20)
    initing_job = Job.objects.filter(
        state__in=[Job.StateEnum.WAITING, Job.StateEnum.INITING],
        create_time__lte=timeout_time,
        async_flag=True
    )
    logger.info("当前有%d个任务初始化超时" % initing_job.count())
    for job in initing_job:
        # 当任务为初始化状态时，先重置再启动；如果为等待状态时，则直接启动
        if job.state == Job.StateEnum.INITING:
            num = Job.objects.select_for_update().filter(
                id=job.id, state=Job.StateEnum.INITING
            ).update(state=Job.StateEnum.WAITING)
            if num <= 0:
                continue
        logger.info("[Job: %s] 重置任务状态为等待状态，并重新初始化" % job.id)
        start_server_job.delay(job.id)


@celery_app.task
def monitor_running_job():
    """监控当前执行中的任务
    """
    running_job = Job.objects.filter(state=Job.StateEnum.RUNNING)
    logger.info("[PeriodicTasks]开始查询执行中的任务，当前运行中的任务数: %s" % running_job.count())
    for job in running_job:
        job = Job.objects.get(id=job.id)
        tasks = Task.objects.filter(job=job, state=Task.StateEnum.CLOSED)
        closed_task_num = tasks.count()
        # 任务数量等于任务关闭数，但不等于完成数
        if job.task_num == closed_task_num and job.task_done != job.task_num:
            logger.warning("[Job: %s] 任务数量和任务关闭数量[%d]不等于任务完成数量[%d]" % (
                job.id, closed_task_num, job.task_done))
            final_task = tasks.order_by("-end_time").first()
            logger.info("[Job: %s][Task: %s] 获取最后一个完成任务的结束时间: %s" % (
                job.id, final_task.id, final_task.end_time))
            if timezone.now() - final_task.end_time > timedelta(minutes=20):
                logger.info("[Job: %s] 刷新任务完成数，启动任务结果入库流程")
                job.task_done = job.task_num
                job.save()
                core.JobCloseHandler.close_job(job.id)


@celery_app.task
def monitor_closing_job():
    """监控当前入库中的任务
    """
    closing_job = Job.objects.filter(state=Job.StateEnum.CLOSING)
    logger.info("[PeriodicTasks]开始查询入库中的任务，当前入库中的任务数: %s" % closing_job.count())
    for job in closing_job:
        job = Job.objects.get(id=job.id)
        if job.save_time and job.save_time < settings.CLOSING_JOB_TIMEOUT:
            continue
        logger.info("[PeriodicTasks][Project: %s][Job: %s] job closing timeout" % (
            job.project_id, job.id))
        remarks = "Time out while closing."
        Job.objects.filter(id=job.id).update(
            result_code=errcode.E_SERVER_SCAN_TIMEOUT,
            result_msg=remarks,
            state=Job.StateEnum.CLOSED,
            expire_time=localnow(),
            remarks=remarks
        )
        core.JobCloseHandler.close_scan(job.id)


@celery_app.task
def handle_expired_job():
    """取消超时未结束的任务
    """
    unfinished_jobs = Job.objects.exclude(state=Job.StateEnum.CLOSED)
    logger.info("[PeriodicTasks]开始查询未关闭的超时任务，当前未关闭任务数: %s" %
                (unfinished_jobs.count()))
    now = timezone.now()
    for job in unfinished_jobs:
        job = Job.objects.get(id=job.id)
        if timezone.now() - job.create_time > settings.CLEAN_JOB_TIMEOUT:
            logger.info("[PeriodicTasks][Project: %s][Job: %s] job running timeout" % (
                job.project_id, job.id))
            core.JobCloseHandler.revoke_job(job, errcode.E_NODE_JOB_TIMEOUT,
                                            "Time out while %s" % job.get_state_display())
        else:
            private_tasks = job.task_set.exclude(state=Task.StateEnum.CLOSED).filter(
                private=True,
                last_beat_time__lt=now - settings.CLEAN_PRIVATE_JOB_TIMEOUT)
            if private_tasks:
                logger.info("[PeriodicTasks][Project: %s] revoking job[%d]" % (
                    job.project_id, job.id))
                core.JobCloseHandler.revoke_job(
                    job, errcode.E_NODE_JOB_BEAT_ERROR,
                    "本地分析任务被中断，请检查[%s]启动渠道，影响工具：%s" %
                    (job.created_from, ';'.join([str(t.task_name) for t in private_tasks])))

    # 筛选未完成且为客户端创建的运行中任务
    client_running_jobs = unfinished_jobs.filter(client_flag=True).exclude(state=Job.StateEnum.CLOSING)
    logger.info("[PeriodicTasks] 开始查询未上报心跳的客户端任务: %s" % client_running_jobs.count())
    for item in client_running_jobs:
        job = Job.objects.get(id=item.id)
        current_time = timezone.now()
        if job.last_beat_time and current_time - job.last_beat_time > settings.CLEAN_PRIVATE_JOB_TIMEOUT:
            logger.info("[PeriodicTasks][Project: %s]revoking job[%d] job lost beat: %s [Current: %s]" % (
                job.project_id, job.id, job.last_beat_time, current_time))
            core.JobCloseHandler.revoke_job(
                job, errcode.E_NODE_JOB_BEAT_ERROR,
                "本地分析任务被中断，请检查[%s]启动渠道并建议触发重试" % job.created_from)
        elif job.last_beat_time is None and current_time - job.create_time > settings.INIT_JOB_TIMEOUT:
            # 客户端创建任务后没有上报心跳
            logger.info("[PeriodicTasks][Project: %s] revoking job[%d] without beat time [Current: %s]" % (
                job.project_id, job.id, current_time))
            core.JobCloseHandler.revoke_job(job, errcode.E_NODE_JOB_BEAT_ERROR,
                                            "本地分析任务被中断，请检查[%s]启动渠道并建议触发重试" % job.created_from)

    unack_tasks = Task.objects.filter(state=Task.StateEnum.ACKING)
    logger.info("[PeriodicTasks]开始查询未确认的Task任务，当前未确认Task任务数: %s" % unack_tasks.count())
    for task in unack_tasks:
        if not task.register_time or timezone.now() - task.register_time > settings.CLEAN_PRIVATE_JOB_TIMEOUT:
            logger.info("[PeriodicTasks][Task: %s][Node: %s] task ack timeout" % (task.id, task.node.name))
            core.NodeTaskRegisterManager.reset_unack_task(task.id)
            core.NodeTaskRegisterManager.release_node(task.node_id)
