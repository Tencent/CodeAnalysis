# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
job的核心管理接口
"""

# 原生 import
import json
import logging

# 第三方 import
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from django.utils import timezone
from django.utils.timezone import now
from rest_framework import serializers

# 项目内 import
from apps.codeproj.models import CodeLintInfo, CodeMetricCCInfo, CodeMetricClocInfo, \
    CodeMetricDupInfo, Organization, Project, ProjectTeam, Repository
from apps.job import models
from apps.nodemgr.models import Node, NodeToolProcessRelation
from util import errcode
from util.exceptions import CDErrorBase
from util.webclients import AnalyseClient

# 全局变量
logger = logging.getLogger(__name__)


class JobDispatchHandler(object):
    """任务分发处理
    """

    @classmethod
    def check_job_tag_disabled(cls, tag):
        """检查任务的标签是否有效
        """
        if tag.tag_type == models.ExecTag.TypeEnum.DISABLED:
            logger.info("[Tag: %s] tag is disabled" % tag.name)
            return True
        else:
            return False

    @classmethod
    def get_enable_nodes(cls, job, tag):
        """获取可执行的节点列表
        """
        project = job.project
        repo = project.repo
        team = repo.project_team
        org = repo.organization

        superusers = User.objects.filter(is_superuser=True)
        users = [user for user in repo.get_members(Repository.PermissionEnum.ADMIN)] + \
                [user for user in repo.get_members(Repository.PermissionEnum.USER)] + \
                [user for user in superusers]
        if team:
            users += [user for user in team.get_members(ProjectTeam.PermissionEnum.ADMIN)]
        if org:
            users += [user for user in org.get_members(Organization.PermissionEnum.ADMIN)]
        users = set(users)
        nodes = Node.objects.filter(manager__in=users, exec_tags=tag).exclude(enabled=Node.EnabledEnum.DISABLED)
        return nodes

    @classmethod
    def add_job_to_queue(cls, job):
        """根据分配规则，将job下相关的task和task_process分配到相应的node节点去：
           标签对应：任务的标签继承自项目标签，标签需要一一对应
           工具/子进程需要在Node的支持范围内
           Node管理员需要对Project有访问权限
        """
        task = job.task_set.all().first()
        if not task:
            return
        tag = task.tag
        if cls.check_job_tag_disabled(tag):
            message = "当前项目配置的运行环境标签[%s]已停用，请在扫描方案中调整\"运行环境标签\"后重新启动。" % tag.name
            logger.warning(message)
            JobCloseHandler.revoke_job(job, errcode.E_USER_CONFIG_NODE_ERROR, message)
            return

        logger.info("[Job: %s] start to add job to queue..." % job)
        # 1. Node管理员需要对Project有访问权限
        # 2. 标签对应
        nodes = cls.get_enable_nodes(job, tag)
        if not nodes:
            logger.warning("找不到符合运行环境标签[%s]且有权限的节点分配" % tag.name if tag else "None")
        queue_set = []
        none_node_tasks = []
        for task in job.task_set.exclude(state=models.Task.StateEnum.CLOSED):
            # 3. 工具支持
            tp_relations = models.TaskProcessRelation.objects.filter(task=task)
            for relation in tp_relations:
                if relation.private:
                    # 私有task不参与分配
                    continue
                node_ids = NodeToolProcessRelation.objects.filter(checktool__name=task.task_name,
                                                                  process=relation.process).values_list("node_id",
                                                                                                        flat=True)
                task_nodes = nodes.filter(id__in=node_ids)
                for node in task_nodes:
                    queue_set.append(models.TaskProcessNodeQueue(
                        task=task, task_process=relation, node=node))
                if not task_nodes:
                    none_node_tasks.append({"task": task, "process": relation})
            if not tp_relations:
                # 兼容无process的task
                node_ids = NodeToolProcessRelation.objects.filter(
                    checktool__name=task.task_name).values_list("node_id", flat=True)
                task_nodes = nodes.filter(id__in=node_ids)
                for node in task_nodes:
                    queue_set.append(models.TaskProcessNodeQueue(task=task, task_process=None, node=node))
                if not task_nodes:
                    none_node_tasks.append({"task": task, "process": None})
        models.TaskProcessNodeQueue.objects.bulk_create(queue_set, 1000)
        if none_node_tasks:
            none_node_task_str = ";".join(
                ["%s(%s)" % (item["task"].task_name, item["process"]) for item in none_node_tasks])

            message = "当前项目配置的运行环境标签[%s]没有机器资源可以运行工具[%s]，请在扫描方案中调整\"运行环境\"的标签后重新启动。" % (
                tag.name, none_node_task_str)
            logger.warning(message)
            JobCloseHandler.revoke_job(job, errcode.E_USER_CONFIG_NODE_ERROR, message)


class JobCloseHandler(object):
    """任务关闭处理
    """

    class CodeLintResultInfoSerializer(serializers.ModelSerializer):
        class Meta:
            model = CodeLintInfo
            fields = '__all__'
            read_only_fields = ['project']

    class CodeMetricCCResultInfoSerializer(serializers.ModelSerializer):
        class Meta:
            model = CodeMetricCCInfo
            fields = '__all__'
            read_only_fields = ['project']

    class CodeMetricDupResultInfoSerializer(serializers.ModelSerializer):
        class Meta:
            model = CodeMetricDupInfo
            fields = '__all__'
            read_only_fields = ['project']

    class CodeMetricClocResultInfoSerializer(serializers.ModelSerializer):
        class Meta:
            model = CodeMetricClocInfo
            fields = '__all__'
            read_only_fields = ['project']

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
            state=models.Job.StateEnum.CLOSING, result_code=None, closing_time=timezone.now())
        cls.close_scan(job_id, reset=True)

    @classmethod
    def after_job_closed(cls, job_id, result_code, result_msg, result_data=None, result_path=None):
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
        logger.info("[Job: %d] 关闭成功，result_code=%d, result_msg=%s。开始执行后续操作..." % (
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
            for key, model_cls, serializer in info_list:
                info_data = result_data.get(key) if result_data else None
                if info_data:
                    instance, _ = model_cls.objects.get_or_create(project=project)
                    slz = serializer(instance=instance, data=info_data)
                    if slz.is_valid():
                        slz.save()
                    else:
                        logger.error("%s save error: %s" % (key, slz.errors))
        job.result_path = result_path
        job.save()
        logger.info("[Job: %d] 任务回调执行结束。" % job_id)

    job_closed = after_job_closed

    @classmethod
    def revoke_job(cls, job, result_code, result_msg):
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
        logger.info("[Job: %s] revoke job, result: [%s]%s" % (job.id, result_code, result_msg))
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
                        result_msg='Job revoked: %s' % result_msg,
                        end_time=revoke_time)
            if nrow == 1:  # race condition
                # put this task to killingtask table
                if task.node:
                    logger.info("[Task: %s][Node: %s] revoke job, update node to free state" % (task.id, task.node))
                    node_id = task.node.id  # codepuppy 未上线_kill_task可能会导致继续给节点派发任务
                    Node.objects.filter(id=node_id).update(state=Node.StateEnum.FREE)
                    models.KillingTask.objects.create(node=task.node, task=task)
                    # 取消关联的task_process
                    cls.revoke_task_process_relation(task.id, task_result_code, result_msg, revoke_time)
                continue
            models.Task.objects.filter(id=task.id).update(
                state=models.Task.StateEnum.CLOSED,
                result_code=task_result_code,
                result_msg='Job revoked: %s' % result_msg,
                end_time=revoke_time)
            # 取消关联的task_process
            cls.revoke_task_process_relation(task.id, task_result_code, result_msg, revoke_time)

        job.closing_time = revoke_time
        job.result_code = result_code
        job.result_msg = result_msg
        job.state = models.Job.StateEnum.CLOSED
        job.expire_time = revoke_time
        job.save()

        scan_id = job.scan_id
        if scan_id:
            logger.info(
                "[Job: %s] request analyse server to close scan[%d] ..." % (job.id, scan_id))
            try:
                cls.close_scan(job.id)
            except CDErrorBase as e:
                logger.exception(e)
                JobCloseHandler.job_closed(job.id, errcode.E_SERVER, e.msg)
        else:
            logger.info("[Job: %s] job no scan to close, just close job ..." % job.id)
            JobCloseHandler.job_closed(job.id, errcode.OK, "")
        # 清理task节点队列数据
        JobCloseHandler.clean_closed_task_process_node(job)

    @classmethod
    def revoke_task_process_relation(cls, task_id, result_code, result_msg, revoke_time):
        """取消关联的task_process
        """
        models.TaskProcessRelation.objects.filter(task_id=task_id).exclude(
            state=models.TaskProcessRelation.StateEnum.CLOSED
        ).update(state=models.TaskProcessRelation.StateEnum.CLOSED,
                 result_code=result_code,
                 result_msg='Job revoked: %s' % result_msg,
                 end_time=revoke_time)

    @classmethod
    def clean_closed_task_process_node(cls, job):
        """清理已关闭的任务进程节点信息
        """
        logger.info("[Job: %s] 清理已执行完成的任务进程节点信息" % job.id)
        models.TaskProcessNodeQueue.objects.filter(task__job=job, task__state=models.Task.StateEnum.CLOSED).delete()

    @classmethod
    def close_scan(cls, job_id, **kwargs):
        """调用服务器接口关闭Analyse Server的scan
        """
        # 拼接参数
        job = models.Job.objects.get(id=job_id)
        if not job.scan_id:
            logger.error("[Job: %d] 无scan_id可以关闭..." % job_id)
            return
        data = {
            "job": {
                "context_url": job.context_path,
                "result_code": job.result_code or errcode.OK,  # 如无则为成功
                "result_msg": job.result_msg,
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
        if kwargs.get("reset") is True:
            data["reset"] = True
        if kwargs.get("sync"):
            data["sync_flag"] = True
        if kwargs.get("force"):
            data["force"] = True
        logger.info("调用AnalyseServer结束Scan，参数如下：")
        logger.info(json.dumps(data, indent=4))
        analyse_client = AnalyseClient()
        analyse_client.api("close_scan", data=data,
                           path_params=(job.project.id, job.scan_id))

    @classmethod
    def close_job(cls, job_id, reclose=False):
        """close job normally. this function needs to suport reentry.
        """
        logger.info("[Job: %s] start close_job ..." % job_id)
        job = models.Job.objects.get(id=job_id)
        scan_id = job.scan_id  # 部分情况下job_context中没有scanid
        logger.info("[Job: %s] get scan_id is %s" % (job_id, scan_id))
        logger.info("[Job: %s] checking task_done number (%d/%d)..." % (job_id, job.task_done, job.task_num))
        if job.task_num != job.task_done:  # not to closed yet
            logger.info("[Job: %s] check failed. task_done(%d) less than task_num(%d). end of close_job." % (
                job_id, job.task_done, job.task_num))
            return
        logger.info("[Job: %d] check pass." % job_id)

        # check if there is older job unclosed
        logger.info("[Job: %d] checking older job unclosed..." % job_id)
        try:
            older_jobs = models.Job.objects.filter(
                project=job.project, id__lt=job.id
            ).exclude(
                state=models.Job.StateEnum.CLOSED
            )
            if older_jobs:
                logger.info("[Job: %d] canceling %d older scan jobs..." % (job_id, older_jobs.count()))
                try:
                    for j in older_jobs:
                        if not j.check_redirect():
                            continue
                        logger.info("[Job: %d] canceling older job[%d]..." % (job_id, j.id))
                        result_msg = json.dumps(
                            {"job_id": job.id, "scan_id": scan_id, "msg": "plz check the other job's result"})
                        JobCloseHandler.revoke_job(j, errcode.CLIENT_REDIRECT, result_msg)
                except Exception as e:  # all exception
                    logger.error("[Job: %d] cancel older scan failed. end of close_job." % job.id)
                    logger.exception(e)
                    models.Job.objects.filter(id=job_id, state=models.Job.StateEnum.RUNNING) \
                        .update(result_msg="入库失败：有历史任务未完成入库")
                    return
            logger.info("[Job: %s] check pass." % job_id)
        except ObjectDoesNotExist:
            logger.info(
                "[Job: %s] check pass. scan.ObjectDoesNotExist no need to check." % job_id)
            pass

        if reclose:  # 支持重新入库
            models.Job.objects.filter(id=job_id, state=models.Job.StateEnum.CLOSED).update(
                state=models.Job.StateEnum.RUNNING)

        logger.info("[Job: %d] checking if other is closing job ..." % job_id)
        nrows = models.Job.objects.filter(
            id=job_id, state__in=[models.Job.StateEnum.WAITING, models.Job.StateEnum.RUNNING]) \
            .update(state=models.Job.StateEnum.CLOSING, closing_time=timezone.now())
        if nrows == 0:  # other is closing the job
            logger.info("[Job: %d] unable to close due to it's %s" %
                        (job_id, job.get_state_display()))
            return
        logger.info("[Job: %d] check pass." % job_id)
        job.result_code = errcode.OK
        if scan_id:
            logger.info(
                "[Job: %d] request analyse server to close scan[%d] ..." % (job_id, scan_id))
            try:
                cls.close_scan(job.id)
            except CDErrorBase as e:
                logger.exception(e)
                cls.job_closed(job.id, errcode.E_SERVER, e.msg)
        else:
            logger.info("[Job: %d] no scan to close, just close job ..." % job_id)
            cls.job_closed(job.id, errcode.OK, "")
        cls.clean_closed_task_process_node(job)
        logger.info("[Job: %d] close_job end." % job_id)

    @classmethod
    def save_task_result(cls, task_id, task_version, result_code, result_msg, result_data, log_url=None,
                         processes=None):
        """正常结束task
        """
        if result_msg:
            try:
                result_msg = result_msg.encode().decode("utf-8", errors="ignore")
            except Exception as err:
                logger.exception("[Task: %d] task msg wrong format, msg: %s, err: %s" % (task_id, result_msg, err))
                result_msg = ""

        if processes:
            # 存在processes，则优先入库
            qs = models.TaskProcessRelation.objects.filter(task_id=task_id,
                                                           process__name__in=processes,
                                                           state=models.TaskProcessRelation.StateEnum.RUNNING)
            nrow = qs.update(state=models.TaskProcessRelation.StateEnum.CLOSED,
                             end_time=now(),
                             result_code=result_code,
                             result_msg=result_msg,
                             result_url=result_data,  # 此处result_data是result url
                             log_url=log_url)
            logger.info("[Task: %s] 进程[%s]关闭数量: %s" % (task_id, processes, nrow))
            if nrow == 0:
                return

            tp_relations = models.TaskProcessRelation.objects.filter(task_id=task_id)
            running_processes = tp_relations.filter(state=models.TaskProcessRelation.StateEnum.RUNNING)
            waiting_processes = tp_relations.exclude(state=models.TaskProcessRelation.StateEnum.CLOSED)
            if running_processes.count() > 0 and nrow != tp_relations.count():
                logger.info("[Task: %s] 当前还有%s个进程正在运行: %s" % (
                    task_id, running_processes.count(), running_processes.values_list("process__name", flat=True)))
                task_state = models.Task.StateEnum.RUNNING
            elif waiting_processes.count() > 0 and nrow != tp_relations.count():
                logger.info("[Task: %s] 当前还有%s个进程处于等待状态: %s" % (
                    task_id, waiting_processes.count(), waiting_processes.values_list("process__name", flat=True)))
                task_state = models.Task.StateEnum.WAITING
            else:
                logger.info("[Task: %s] 当前%s个进程全部关闭: %s" % (
                    task_id, tp_relations.count(), tp_relations.values_list("process__name", flat=True)))
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
            logger.info("[Task: %d] task刷新结果: %s，task预期状态：%s, 实际状态：%s" % (
                task_id, nrow, task_state, task.state))
            if nrow == 1:
                job_id = task.job.id
                if task_state == models.Task.StateEnum.CLOSED:
                    nrow = models.Job.objects.filter(id=job_id).update(
                        task_done=F("task_done") + 1)
                    models.TaskProgress.objects.create(
                        task=task,
                        message="任务执行完毕",
                        progress_rate=100,
                        node=task.node
                    )
                    logger.info("[Job: %s][Task: %s] 关闭Task: %s" % (job_id, task_id, nrow))

        else:
            # 不存在processes，使用旧逻辑
            nrow = models.Task.objects.filter(id=task_id, state=models.Task.StateEnum.RUNNING) \
                .update(state=models.Task.StateEnum.CLOSED,
                        end_time=now(),
                        result_code=result_code,
                        result_msg=result_msg,
                        log_url=log_url,
                        execute_version=task_version)

            task = models.Task.objects.get(id=task_id)
            if nrow == 1:
                task.result = result_data
                task.save()
                job_id = task.job.id
                models.Job.objects.filter(id=job_id).update(
                    task_done=F("task_done") + 1)
                if task.node:  # 私有进程执行，可能不会记录node节点
                    Node.objects.filter(id=task.node.id, executor_used_num__gt=0).update(
                        executor_used_num=F('executor_used_num') - 1)
                    Node.objects.filter(id=task.node.id, state=Node.StateEnum.BUSY).update(
                        state=Node.StateEnum.FREE)

    @classmethod
    def check_closing_job(cls, job):
        """检查正在入库的任务
        """
        if not models.Job.objects.filter(id=job.id, state=models.Job.StateEnum.CLOSING).exists():
            return True
        try:
            response = AnalyseClient().api("scan_check", path_params=(job.project_id, job.scan_id,), data=None)
        except Exception as err:
            logger.exception("[Project: %s][Job: %s] scan check error, err: %s" % (job.project_id, job.id, err))
            return True
        if response.get("result") is True:
            return True
        logger.warning("[Project: %s][Job: %s] job closing check failed, reset job closing..." % (
            job.project_id, job.id))
        cls.reclose_job(job.id)
        return False


class NodeTaskRegisterManager(object):
    """节点任务注册
    """

    @classmethod
    def reset_unack_task(cls, task_id):
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

    @classmethod
    def update_task_state_with_running(cls, task_id, node_id):
        """更新task相关数据的状态
        1. 获取当前任务的进程
        2. 更新task进程的状态，调整为执行中
        3. 更新task的开始时间
        4. 更新job的执行状态
        """
        task = models.Task.objects.get(id=task_id)
        node = Node.objects.get(id=node_id)
        logger.info("[Task: %s] start running with node:%s(%s)" % (task_id, node.name, node.state))
        current_time = now()
        # 将task的process置为运行中的状态
        models.TaskProcessRelation.objects.filter(
            task_id=task_id,
            node_id=node_id,
            state=models.TaskProcessRelation.StateEnum.ACKING
        ).update(
            start_time=current_time, state=models.TaskProcessRelation.StateEnum.RUNNING
        )

        # 将task置为运行中的状态
        if not task.start_time:
            models.Task.objects.filter(id=task.id, start_time__isnull=True).update(start_time=current_time)

        # 将job置为运行中的状态
        if task.job.state in [models.Job.StateEnum.WAITING, models.Job.StateEnum.INITED]:
            nrows = models.Job.objects.filter(id=task.job.id, state__in=[
                models.Job.StateEnum.WAITING, models.Job.StateEnum.INITED
            ]).update(state=models.Job.StateEnum.RUNNING)
            if nrows > 0:
                models.Job.objects.filter(id=task.job_id, start_time__isnull=True).update(
                    start_time=current_time
                )

    @classmethod
    def release_node(cls, node_id):
        """更新节点状态，调整为空闲状态
        """
        models.Node.objects.filter(id=node_id, state=models.Node.StateEnum.BUSY).update(
            state=models.Node.StateEnum.FREE)

    @classmethod
    def clean_closed_task_process_node(cls, job):
        """清理已关闭的任务进程节点信息
        """
        logger.info("[Job: %s] 清理已执行完成的任务进程节点信息" % job.id)
        models.TaskProcessNodeQueue.objects.filter(task__job=job, task__state=models.Task.StateEnum.CLOSED).delete()

    @classmethod
    def set_node_busy_state(cls, node, **kwargs):
        """设置节点为忙碌状态
        """
        # 查询并占用节点，如果节点忙碌，则返回空
        if kwargs.get("free") is True:
            logger.info("[Node: %s] update node free state" % node)
            models.Node.objects.filter(id=node.id).update(state=models.Node.StateEnum.FREE)

        free_node = models.Node.everything.filter(id=node.id, state=models.Node.StateEnum.FREE).first()
        logger.debug("[Node: %s] filter free node %s" % (node, node.id))
        if not free_node:
            return False
        nrows = models.Node.everything.filter(
            id=free_node.id, state=models.Node.StateEnum.FREE
        ).update(state=models.Node.StateEnum.BUSY)
        logger.info("[Node: %s] update free node %s to busy state" % (free_node, free_node.id))
        if nrows == 1:  # Node已有任务在执行，并未put result
            return True
        else:
            return False

    @classmethod
    def get_killed_task(cls, node):
        """停止指定任务
        """
        # 返回被终止的任务
        killingtasks = models.KillingTask.objects.filter(
            node=node, killed_time__isnull=True)
        for kt in killingtasks:
            nrow = models.KillingTask.objects.filter(
                id=kt.id).update(killed_time=now())
            if nrow == 1:
                logger.info("%s task killed, release node %s" % (kt.task.id, node.name))
                cls.release_node(node.id)
                return {
                    "task_name": "_kill_task",
                    "task_params": {"task_id": kt.task.id}
                }
        return None

    @classmethod
    def update_task_process_state_with_running(cls, task, processes, node):
        """更新task相关数据的状态

        1. 更新task进程的状态，调整为执行中
        2. 更新task的开始时间
        3. 更新job的执行状态
        """
        logger.info("[Task: %s] start running with node:%s" % (task.id, node.name))
        current_time = now()
        # 将process置为运行中的状态
        models.TaskProcessRelation.objects.filter(task=task, process__in=processes).update(
            node=node, start_time=current_time, state=models.TaskProcessRelation.StateEnum.RUNNING)
        # 将task置为运行中的状态
        if not task.start_time:  # 避免多次读写数据库
            models.Task.objects.filter(id=task.id, start_time__isnull=True).update(start_time=current_time)
        # 将job置为运行中的状态
        if task.job.state in [models.Job.StateEnum.WAITING, models.Job.StateEnum.INITED]:  # 避免多次读写数据库
            nrows = models.Job.objects.filter(
                id=task.job.id,
                state__in=[models.Job.StateEnum.WAITING, models.Job.StateEnum.INITED]
            ).update(
                state=models.Job.StateEnum.RUNNING
            )
            if nrows > 0:
                models.Job.objects.filter(id=task.job_id, start_time__isnull=True).update(start_time=current_time)

    @classmethod
    def register_task(cls, node, occupy):
        """注册任务
        """
        # 获取当前节点队列下待运行的Task（取所有task的前50条和所有task中process为0的前50条）
        # 避免节点资源有限时，取到前50条均为datahandle进程的任务，导致新任务无法正常启动
        logger.debug("[Register Task][Node: %s] 开始注册工具任务" % node)
        task_queue = list(set(
            [item.task for item in models.TaskProcessNodeQueue.objects.filter(
                node=node, task__state=models.Task.StateEnum.WAITING)[:50]] +
            [item.task for item in models.TaskProcessNodeQueue.objects.filter(
                node=node, task__state=models.Task.StateEnum.WAITING, task_process__priority=0)[:20]] +
            [item.task for item in models.TaskProcessNodeQueue.objects.filter(
                node=node, task__state=models.Task.StateEnum.WAITING, task_process__priority=1)[:20]])
        )
        # 按task id排序
        task_queue.sort(key=lambda item: item.id)
        process_queue_ids = models.TaskProcessNodeQueue.objects.filter(
            node=node, task_process__state=models.TaskProcessRelation.StateEnum.WAITING
        ).values_list("task_process_id", flat=True)
        logger.debug("[Register Task][Node: %s] 获取节点可执行的工具进程：%s" % (node, len(task_queue)))

        task = None
        processes = []
        for t in task_queue:
            task_node = t.node
            if occupy:
                # 注册task，如果分配未果，需要重置为等待状态
                nrows = models.Task.objects.filter(id=t.id, state=models.Task.StateEnum.WAITING).update(
                    state=models.Task.StateEnum.ACKING, node=node,
                    register_time=now())  # TaskProcess结束后再把Task重新放回Waiting队列
                if nrows == 0:  # Task已经被其他节点抢占
                    continue
                logger.debug("[Register Task][Node: %s][Task: %s] 预分配成功" % (node, t.id))

            # 成功占用，获取当前占用Task的进程列表是否有需要运行的进程
            task_processes = models.TaskProcessRelation.objects.filter(task=t).order_by("priority")
            for task_process in task_processes:
                if task_process.state == models.TaskProcessRelation.StateEnum.CLOSED:
                    continue
                if task_process.state == models.TaskProcessRelation.StateEnum.RUNNING:  # 似乎这里是多余的
                    break
                if task_process.state == models.TaskProcessRelation.StateEnum.WAITING and \
                        task_process.id in process_queue_ids:
                    # 如果子进程在等待状态且在node列表中
                    processes.append(task_process.process)
                else:
                    # 为返回连续process，所以一旦有不满足条件则退出
                    break
            if not task_processes or processes:
                # 不存在子进程或者已分配到子进程
                task = t
                break
            # 分配未果，需要重置为等待状态
            if occupy:
                # 则重置任务为waiting状态
                models.Task.objects.filter(id=t.id, state=models.Task.StateEnum.ACKING).update(
                    state=models.Task.StateEnum.WAITING, node=task_node, register_time=None)

        if task:
            if occupy:
                logger.info("[Register Task][Node: %s][Task: %s] 分配成功" % (node, task.id))
                models.TaskProcessRelation.objects.filter(task=task, process__in=processes).update(
                    node=node, start_time=now(), state=models.TaskProcessRelation.StateEnum.ACKING)
            logger.info("[Register Task][Node: %s][Task: %s] 注册工具进程列表(%s)" % (
                node, task.id, ",".join([process.name for process in processes])))
        elif occupy:
            logger.debug("[Register Task][Node: %s] 获取不到任务，释放节点" % node)
            # 取不到任务则重新释放节点
            cls.release_node(node.id)
        return task, processes

    @classmethod
    def register_task_v1(cls, node, occupy):
        """注册任务（待废弃）
        """
        # 获取当前节点队列下待运行的Task（取所有task的前50条和所有task中process为0的前50条）
        # 避免节点资源有限时，取到前50条均为datahandle进程的任务，导致新任务无法正常启动
        task_queue = list(set(
            [item.task for item in models.TaskProcessNodeQueue.objects.filter(
                node=node, task__state=models.Task.StateEnum.WAITING)[:50]] +
            [item.task for item in models.TaskProcessNodeQueue.objects.filter(
                node=node, task__state=models.Task.StateEnum.WAITING, task_process__priority__in=[0, 1])[:50]]))
        process_queue_ids = models.TaskProcessNodeQueue.objects.filter(
            node=node, task_process__state=models.TaskProcessRelation.StateEnum.WAITING
        ).values_list("task_process_id", flat=True)

        task = None
        processes = []
        for t in task_queue:
            task_node = t.node
            if occupy:
                # 优先执行task，如果分配未果，需要重置为等待状态
                nrows = models.Task.objects.filter(id=t.id, state=models.Task.StateEnum.WAITING).update(
                    state=models.Task.StateEnum.RUNNING, node=node)  # TaskProcess结束后再把Task重新放回Waiting队列
                if nrows == 0:  # Task已经被其他节点抢占
                    continue
            # 成功占用
            # 获取queue_process中连续的task_process
            task_processes = models.TaskProcessRelation.objects.filter(task=t).order_by("priority")
            for task_process in task_processes:
                if task_process.state == models.TaskProcessRelation.StateEnum.CLOSED:
                    continue
                if task_process.state == models.TaskProcessRelation.StateEnum.RUNNING:  # 似乎这里是多余的
                    break
                if task_process.state == models.TaskProcessRelation.StateEnum.WAITING and \
                        task_process.id in process_queue_ids:
                    # 如果子进程在等待状态且在node列表中
                    processes.append(task_process.process)
                else:
                    # 为返回连续process，所以一旦有不满足条件则退出
                    break
            if not task_processes or processes:
                # 不存在子进程或者已分配到子进程
                task = t
                break
            # 分配未果，需要重置为等待状态
            if occupy:
                # 则重置任务为waiting状态
                models.Task.objects.filter(id=t.id, state=models.Task.StateEnum.RUNNING).update(
                    state=models.Task.StateEnum.WAITING, node=task_node)
        if task:
            if occupy:  # 将任务相关状态更新为运行中
                cls.update_task_process_state_with_running(task, processes, node)
            logger.debug("[Task: %s] task with processes(%s) got by node[%s]" % (
                task.id, ",".join([process.name for process in processes]), node))
        else:
            if occupy:
                # 取不到任务则重新释放节点
                cls.release_node(node.id)
        return task, processes


class PrivateTaskManager(object):
    """私有任务管理
    """

    class StateEnum:
        KEEP_WAITING = 0
        RUN_TASK = 1
        FINISH = 2

    state_choices = (
        (StateEnum.KEEP_WAITING, "keep waiting"),
        (StateEnum.RUN_TASK, "run task"),
        (StateEnum.FINISH, "finish"))

    @classmethod
    def get_private_task(cls, job):
        """获取私有任务
        """
        state = cls.StateEnum.KEEP_WAITING

        private_tasks = job.task_set.filter(private=True).exclude(state=models.Task.StateEnum.CLOSED)
        tasks = {}
        if not private_tasks:
            state = cls.StateEnum.FINISH
        else:
            for task in private_tasks:
                nrows = models.Task.objects.filter(id=task.id, state=models.Task.StateEnum.WAITING).update(
                    state=models.Task.StateEnum.RUNNING)
                if nrows == 0:
                    # 任务task已被占用
                    continue
                if not task.start_time:  # 避免多次读写数据库
                    models.Task.objects.filter(
                        id=task.id, start_time__isnull=True).update(start_time=now())
                execute_processes = []
                for process in task.taskprocessrelation_set.all().order_by("priority"):
                    if not execute_processes and process.state == models.TaskProcessRelation.StateEnum.CLOSED:
                        continue
                    elif models.TaskProcessRelation.objects.filter(
                            id=process.id, private=True,
                            state=models.TaskProcessRelation.StateEnum.WAITING) \
                            .update(state=models.TaskProcessRelation.StateEnum.RUNNING) > 0:  # 占用并执行task
                        logger.info("[Task: %s] 私有进程[%s]即将执行" %
                                    (task.id, process.id))
                        execute_processes.append(process.process)
                    else:
                        break
                if execute_processes:
                    state = cls.StateEnum.RUN_TASK
                    if job.state in [models.Job.StateEnum.WAITING, models.Job.StateEnum.INITED]:
                        nrows = models.Job.objects.filter(id=job.id, state__in=[
                            models.Job.StateEnum.WAITING, models.Job.StateEnum.INITED]).update(
                            state=models.Job.StateEnum.RUNNING)
                        if nrows > 0:
                            models.Job.objects.filter(id=job.id, start_time__isnull=True).update(
                                start_time=now()
                            )
                    tasks[task.id] = {"task": task, "execute_processes": execute_processes}
                else:
                    # 无可执行进程，释放任务
                    models.Task.objects.filter(id=task.id, state=models.Task.StateEnum.RUNNING).update(
                        state=models.Task.StateEnum.WAITING)
                    logger.info("[Task: %s] 无可执行进程，将任务重置为等待状态" % task.id)

        return {"state": state, "state_msg": dict(cls.state_choices)[state], "tasks": tasks}
