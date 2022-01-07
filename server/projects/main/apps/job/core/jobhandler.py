# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
job - jobhandler core
"""

# 原生 import
import json
import logging

# 第三方 import
from django.db.models import F
from django.utils.timezone import now
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

# 项目内 import
from apps.job import models
from apps.nodemgr.models import Node
from apps.codeproj.models import Project, CodeLintInfo, \
    CodeMetricCCInfo, CodeMetricDupInfo, CodeMetricClocInfo

from util import errcode
from util.webclients import AnalyseClient
from util.exceptions import CDErrorBase

from codedog.celery import celery_app

# 全局变量
logger = logging.getLogger(__name__)


def reset_unack_task(task_id):
    """重置未确认的任务
    """
    logger.info("[Task: %s] 重置超时未确认的Task" % task_id)
    models.Task.objects.filter(id=task_id, state=models.Task.StateEnum.ACKING).update(
        state=models.Task.StateEnum.WAITING, register_time=None
    )
    models.TaskProcessRelation.objects.filter(
        task_id=task_id, state=models.TaskProcessRelation.StateEnum.ACKING
    ).update(
        state=models.TaskProcessRelation.StateEnum.WAITING, node=None, start_time=None
    )


def close_scan(job_id):
    """调用服务器接口关闭Analyse Server的scan
    """
    # 拼接参数
    job = models.Job.objects.get(id=job_id)
    if not job.scan_id:
        logger.error("job[%d] 无scan_id可以关闭..." % job_id)
        return
    data = {
        "job": {
            "context_url": job.context_path,
            "result_code": job.result_code or errcode.OK,  # 如无则为成功
            "result_msg": job.result_msg
        },
        "tasks": [{
            "module": task.module,
            "name": task.task_name,
            "execute_version": task.execute_version,
            "params_url": task.params_path,
            "result_code": task.result_code,
            "result_msg": task.result_msg,
            "result_data_url": task.result_path,
            "log_url": task.log_url
        } for task in job.task_set.all()]
    }
    logger.info("调用AnalyseServer结束Scan，参数如下：")
    logger.info(json.dumps(data, indent=4))
    analyse_client = AnalyseClient()
    analyse_client.api("close_scan", data=data,
                       path_params=(job.project.id, job.scan_id))


def revoke_task_process_relation(task_id, result_code, result_msg, revoke_time):
    """取消关联的task_process
    """
    models.TaskProcessRelation.objects.filter(task_id=task_id).exclude(
        state=models.TaskProcessRelation.StateEnum.CLOSED
    ).update(state=models.TaskProcessRelation.StateEnum.CLOSED,
             result_code=result_code,
             result_msg="Job revoked: %s" % result_msg,
             end_time=revoke_time)


def revoke_job(job, result_code, result_msg):
    """revoke job. this function need to support reentry

    note: careful of race condition
    """
    job_id = job.id
    nrows = models.Job.objects.filter(
        id=job_id, state__in=[
            models.Job.StateEnum.WAITING, models.Job.StateEnum.RUNNING,
            models.Job.StateEnum.INITING, models.Job.StateEnum.INITED]
    ).update(state=models.Job.StateEnum.CLOSING)
    if nrows == 0:
        return

    job = models.Job.objects.get(id=job_id)
    revoke_time = now()
    for task in job.task_set.exclude(state=models.Task.StateEnum.CLOSED):
        # 判断当前结果码是否客户端异常码，如果是则调整为任务取消码（299）
        task_result_code = result_code
        if errcode.is_node_error(task_result_code):
            task_result_code = errcode.E_NODE_TASK_CANCEL

        nrow = models.Task.objects \
            .filter(id=task.id, state=models.Task.StateEnum.RUNNING) \
            .update(state=models.Task.StateEnum.CLOSED,
                    result_code=task_result_code,
                    result_msg="Job revoked: %s" % result_msg,
                    end_time=revoke_time)
        if nrow == 1:  # race condition
            # put this task to killingtask table
            if task.node:
                models.KillingTask.objects.create(node=task.node, task=task)
                # 取消关联的task_process
                revoke_task_process_relation(task.id, task_result_code, result_msg, revoke_time)
            continue
        models.Task.objects \
            .filter(id=task.id) \
            .update(state=models.Task.StateEnum.CLOSED,
                    result_code=task_result_code,
                    result_msg="Job revoked: %s" % result_msg,
                    end_time=revoke_time)
        # 取消关联的task_process
        revoke_task_process_relation(task.id, task_result_code, result_msg, revoke_time)

    job.result_code = result_code
    job.result_msg = result_msg
    job.state = models.Job.StateEnum.CLOSED
    job.expire_time = revoke_time
    job.save()

    scan_id = job.scan_id
    if scan_id:
        logger.info(
            "job[%d] request analyse server to close scan[%d] ..." % (job.id, scan_id))
        try:
            close_scan(job.id)
        except CDErrorBase as e:
            logger.exception(e)
            JobCloseHandler.job_closed(job.id, errcode.E_SERVER, e.msg)
    else:
        logger.info("job[%d] no scan to close, just close job ..." % job.id)
        JobCloseHandler.job_closed(job.id, errcode.OK, "")


class JobCloseHandler(object):
    """任务关闭处理
    """

    class CodeLintResultInfoSerializer(serializers.ModelSerializer):
        class Meta:
            model = CodeLintInfo
            fields = "__all__"
            read_only_fields = ["project"]

    class CodeMetricCCResultInfoSerializer(serializers.ModelSerializer):
        class Meta:
            model = CodeMetricCCInfo
            fields = "__all__"
            read_only_fields = ["project"]

    class CodeMetricDupResultInfoSerializer(serializers.ModelSerializer):
        class Meta:
            model = CodeMetricDupInfo
            fields = "__all__"
            read_only_fields = ["project"]

    class CodeMetricClocResultInfoSerializer(serializers.ModelSerializer):
        class Meta:
            model = CodeMetricClocInfo
            fields = "__all__"
            read_only_fields = ["project"]

    @classmethod
    def reclose_job(cls, job_id):
        """重新关闭任务
        """
        logger.info("[Job: %s] 重新关闭任务并入库" % job_id)
        job = models.Job.objects.filter(id=job_id).first()
        if not job:
            logger.info("[Job: %s] 任务不存在" % job_id)
            return
        data = {
            "state": models.Job.StateEnum.RUNNING,
        }
        try:
            AnalyseClient().api("update_scan", data, path_params=(job.project_id, job.scan_id,))
        except Exception as err:
            logger.exception("[Job: %s] 更新扫描任务状态失败: %s" % (job_id, err))
            return
        models.Job.objects.filter(id=job_id).update(
            state=models.Job.StateEnum.RUNNING, result_code=None)
        close_scan(job_id)

    @classmethod
    def job_closed(cls, job_id, result_code, result_msg, result_data=None, result_path=None):
        """任务结束之后的回调，更新project相关的记录
        """
        logger.info("[Job: %d]job开始执行scan结束回调..." % job_id)
        nrow = models.Job.objects.filter(id=job_id).exclude(state=models.Job.StateEnum.CLOSED) \
            .update(state=models.Job.StateEnum.CLOSED,
                    result_code=result_code,
                    result_msg=result_msg,
                    end_time=now())
        if nrow == 0:
            logger.info("[Job: %d] 已经关闭，无需再次关闭。" % job_id)
            return
        logger.info("[Job: %d] 关闭成功，result_code = %d, result_msg = %s。开始执行后续操作..." % (
            job_id, result_code, result_msg))
        job = models.Job.objects.get(id=job_id)
        project = job.project
        logger.info("[Job: %d] 开始激活失活项目..." % job_id)
        # 失活项目重新激活
        if project.status == Project.StatusEnum.DISACTIVE:
            project.status = Project.StatusEnum.ACTIVE
            project.save()
        # 更新项目状态/统计信息
        if errcode.is_success(result_code):
            # 更新扫描成功统计信息
            logger.info("[Job: %s] 任务成功，记录统计信息(如下)..." % job_id)
            logger.info(json.dumps(result_data, indent=4))
            info_list = [("code_lint_info", CodeLintInfo,
                          cls.CodeLintResultInfoSerializer),
                         ("code_metric_cc_info", CodeMetricCCInfo,
                          cls.CodeMetricCCResultInfoSerializer),
                         ("code_metric_dup_info", CodeMetricDupInfo,
                          cls.CodeMetricDupResultInfoSerializer),
                         ("code_metric_cloc_info", CodeMetricClocInfo,
                          cls.CodeMetricClocResultInfoSerializer), ]
            for key, model, serializer in info_list:
                info_data = result_data.get(key) if result_data else None
                if info_data:
                    instance, _ = model.objects.get_or_create(project=project)
                    slz = serializer(instance=instance, data=info_data)
                    if slz.is_valid():
                        slz.save()
                    else:
                        logger.error("%s save error: %s" % (key, slz.errors))
        job.result_path = result_path
        job.save()
        logger.info("[Job: %d] job回调执行结束。" % job_id)


@celery_app.task
def close_job(job_id, reclose=False):
    """close job normally. this function needs to suport reentry.

    note: be careful of race condition
    """
    logger.info("job[%d] start close_job ..." % job_id)
    job = models.Job.objects.get(id=job_id)
    scan_id = job.scan_id
    logger.info("job[%d] get scan_id is %s" % (job_id, scan_id))
    logger.info("job[%d] checking task_done number (%d/%d)..." % (job_id, job.task_done, job.task_num))
    if job.task_num != job.task_done:  # not to closed yet
        logger.info("job[%d] check failed. task_done(%d) less than task_num(%d). end of close_job." % (
            job_id, job.task_done, job.task_num))
        return
    logger.info("job[%d] check pass." % job_id)

    # check if there is older job unclosed
    logger.info("job[%d] checking older job unclosed..." % job_id)
    try:
        older_jobs = models.Job.objects.filter(
            project=job.project, id__lt=job.id).exclude(state=models.Job.StateEnum.CLOSED)
        if older_jobs:
            logger.info("job[%d] canceling %d older scan jobs..." %
                        (job_id, older_jobs.count()))
            try:
                for j in older_jobs:
                    logger.info(
                        "job[%d] canceling older job[%d]..." % (job_id, j.id))
                    result_msg = json.dumps(
                        {"job_id": job.id, "scan_id": scan_id, "msg": "plz check the other job's result"})
                    revoke_job(j, errcode.CLIENT_REDIRECT, result_msg)
            except Exception as e:  # all exception
                logger.error(
                    "job[%d] cancel older scan failed. end of close_job." % job.id)
                logger.exception(e)
                models.Job.objects.filter(id=job_id, state=models.Job.StateEnum.RUNNING) \
                    .update(result_msg="入库失败：有历史任务未完成入库")
                return
        logger.info("job[%d] check pass." % job_id)
    except ObjectDoesNotExist:
        logger.info(
            "job[%d] check pass. scan.ObjectDoesNotExist no need to check." % job_id)
        pass

    if reclose:  # 支持重新入库
        models.Job.objects.filter(id=job_id, state=models.Job.StateEnum.CLOSED).update(
            state=models.Job.StateEnum.RUNNING)

    logger.info("job[%d] checking if other is closing job ..." % job_id)
    nrows = models.Job.objects.filter(
        id=job_id, state__in=[models.Job.StateEnum.WAITING, models.Job.StateEnum.RUNNING]).update(
        state=models.Job.StateEnum.CLOSING)
    if nrows == 0:  # other is closing the job
        logger.info("job[%d] unable to close due to it's %s" %
                    (job_id, job.get_state_display()))
        return
    logger.info("job[%d] check pass." % job_id)

    job.result_code = errcode.OK
    if scan_id:
        logger.info(
            "job[%d] request analyse server to close scan[%d] ..." % (job_id, scan_id))
        try:
            close_scan(job.id)
        except CDErrorBase as e:
            logger.exception(e)
            JobCloseHandler.job_closed(job.id, errcode.E_SERVER, e.msg)
    else:
        logger.info("job[%d] no scan to close, just close job ..." % job_id)
        JobCloseHandler.job_closed(job.id, errcode.OK, "")
    logger.info("job[%d] close_job end." % job_id)


def save_task_result(task_id, task_version, result_code, result_msg, result_data, log_url=None, processes=None):
    """正常结束task
    """
    if result_msg:
        try:
            result_msg = result_msg.encode().decode("utf-8", errors="ignore")
        except Exception as err:
            logger.exception("[Task: %d] task msg wrong format, msg: %s, err: %s" % (task_id, result_msg, err))
            result_msg = ""

    qs = models.TaskProcessRelation.objects.filter(
        task_id=task_id, process__name__in=processes, state=models.TaskProcessRelation.StateEnum.RUNNING)
    nrow = qs.update(state=models.TaskProcessRelation.StateEnum.CLOSED,
                     end_time=now(),
                     result_code=result_code,
                     result_msg=result_msg,
                     result_url=result_data,
                     log_url=log_url)
    logger.info("task[%d] 进程[%s]关闭结果: %s" % (task_id, processes, nrow))
    if nrow == 0:
        return
    tp_relations = models.TaskProcessRelation.objects.filter(
        task_id=task_id)
    if tp_relations.filter(state=models.TaskProcessRelation.StateEnum.RUNNING):
        task_state = models.Task.StateEnum.RUNNING
    elif tp_relations.exclude(state=models.TaskProcessRelation.StateEnum.CLOSED):
        task_state = models.Task.StateEnum.WAITING
    else:
        task_state = models.Task.StateEnum.CLOSED
    nrow = models.Task.objects.filter(
        id=task_id,
        state__in=[models.Task.StateEnum.WAITING,
                   models.Task.StateEnum.RUNNING]
    ).update(
        state=task_state,
        end_time=now(),
        result_code=result_code,
        result_msg=result_msg,
        result_path=result_data,
        log_url=log_url,
        execute_version=task_version
    )
    task = models.Task.objects.get(id=task_id)
    logger.info("task[%d] task刷新结果: %s，task当前状态：%s" %
                (task_id, nrow, task.state))
    if nrow == 1:
        job_id = task.job.id
        if task_state == models.Task.StateEnum.CLOSED:
            models.Job.objects.filter(id=job_id).update(
                task_done=F("task_done") + 1)
            models.TaskProgress.objects.create(
                task=task,
                message="任务执行完毕",
                progress_rate=100,
                node=task.node
            )
        if task.node:
            Node.objects.filter(id=task.node.id, state=Node.StateEnum.BUSY).update(
                state=Node.StateEnum.FREE)
