# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
Job - base models
任务相关Model
"""

# 原生 import
import json
import logging
import os
import uuid
from datetime import timedelta

# 第三方 import
from django.conf import settings
from django.db import models
from django.utils import timezone

# 项目内 import
from apps.codeproj.models import Project
from apps.nodemgr.models import ExecTag, Node
from apps.scan_conf.models import Process
from util import errcode
from util.exceptions import CDErrorBase
from util.fileserver import file_server

logger = logging.getLogger(__name__)


class ScanTypeEnum(object):
    INCRESE = 1  # 增量扫描
    FULL = 2  # 全量扫描

    @classmethod
    def has_value(cls, value):
        return value in [cls.INCRESE, cls.FULL]


class BaseJob(models.Model):
    """job model 抽象基类
    """

    class StateEnum(object):
        WAITING = 0
        RUNNING = 1
        CLOSED = 2
        CLOSING = 3
        INITING = 4
        INITED = 5

    STATE_CHOICES = (
        (StateEnum.WAITING, "Waiting"),
        (StateEnum.INITING, "Initing"),
        (StateEnum.INITED, "Initialized"),
        (StateEnum.RUNNING, "Running"),
        (StateEnum.CLOSED, "Closed"),
        (StateEnum.CLOSING, "Closing")
    )

    scan_id = models.IntegerField(verbose_name="扫描id", null=True, blank=True)
    state = models.IntegerField(default=StateEnum.WAITING, choices=STATE_CHOICES, verbose_name="状态", db_index=True)
    initialized_time = models.DateTimeField(null=True, verbose_name="任务初始化完成时间", blank=True)
    start_time = models.DateTimeField(null=True, verbose_name="启动时间", blank=True)
    closing_time = models.DateTimeField(null=True, verbose_name="开始入库时间", blank=True)
    end_time = models.DateTimeField(null=True, verbose_name="结束时间", blank=True)
    expire_time = models.DateTimeField(null=True, verbose_name="超时时间", blank=True)
    last_beat_time = models.DateTimeField(null=True, verbose_name="最后一次心跳上报时间", blank=True)
    context_path = models.TextField(verbose_name="Context", null=True, blank=True)
    result_code = models.IntegerField(null=True, verbose_name="结果码", blank=True, db_index=True)
    result_msg = models.TextField(verbose_name="结果信息", null=True, blank=True)
    result_path = models.TextField(verbose_name="Result", null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", db_index=True)
    expected_end_time = models.DateTimeField(verbose_name="预期结束时间", null=True, blank=True)
    task_num = models.IntegerField(default=0, verbose_name="子任务数量")
    task_done = models.IntegerField(default=0, verbose_name="已完成子任务数")
    remarks = models.CharField(max_length=512, verbose_name="备注", blank=True, null=True)

    code_line_num = models.IntegerField(verbose_name="代码行数", blank=True, null=True)
    comment_line_num = models.IntegerField(verbose_name="注释行数", blank=True, null=True)
    blank_line_num = models.IntegerField(verbose_name="空白行数", blank=True, null=True)
    total_line_num = models.IntegerField(verbose_name="总行数", blank=True, null=True)
    filtered_code_line_num = models.IntegerField(verbose_name="过滤后的代码行数", blank=True, null=True)
    filtered_comment_line_num = models.IntegerField(verbose_name="过滤后的注释行数", blank=True, null=True)
    filtered_blank_line_num = models.IntegerField(verbose_name="过滤后的空白行数", blank=True, null=True)
    filtered_total_line_num = models.IntegerField(verbose_name="过滤后的总行数", blank=True, null=True)
    efficient_comment_line_num = models.IntegerField(verbose_name="有效注释行", blank=True, null=True)
    filtered_efficient_comment_line_num = models.IntegerField(verbose_name="过滤后的有效注释行", blank=True, null=True)
    created_from = models.CharField(max_length=32, verbose_name="创建渠道", blank=True, null=True)
    async_flag = models.BooleanField(default=False, verbose_name="异步启动标识", blank=True, null=True)
    client_flag = models.BooleanField(verbose_name="客户端创建标识", blank=True, null=True)
    creator = models.CharField(max_length=32, verbose_name="启动人", blank=True, null=True)
    ext_field = models.JSONField(verbose_name="扩展字段", null=True, blank=True)

    class Meta:
        abstract = True
        index_together = (
            ("create_time", "result_code"),
            ("start_time", "result_code"),
            ("end_time", "result_code"),
        )

    def get_project_id(self):
        raise NotImplementedError

    def add_field(self, field_info):
        """增加字段
        """
        if self.ext_field:
            for k, v in field_info.items():
                self.ext_field[k] = v
        else:
            self.ext_field = field_info
        self.save()

    def disable_redirect(self):
        """禁止重定向
        """
        self.add_field({"redirect": False})

    def check_redirect(self):
        """检查是否支持重定向
        不支持重定向时，会显式禁止
        """
        if self.ext_field and self.ext_field.get("redirect") is False:
            return False
        else:
            return True

    def disable_reinit(self):
        """禁止重新初始化
        """
        self.add_field({"reinit": False})

    def check_reinit(self):
        """检查是否支持重新初始化
        不支持重新初始化，会显式禁止
        """
        if self.ext_field and self.ext_field.get("reinit") is False:
            return False
        else:
            return True

    @property
    def waiting_time(self):
        """等待时间
        """
        if self.start_time:
            return self.start_time - self.create_time if self.start_time > self.create_time else timedelta(seconds=0)
        elif self.expire_time:
            return self.expire_time - self.create_time
        else:
            return timezone.now().replace(microsecond=0) - self.create_time

    @property
    def execute_time(self):
        """总执行时间
        """
        if not self.start_time:
            return None
        if self.end_time:
            return self.end_time - self.start_time
        elif self.expire_time:
            return self.expire_time - self.start_time
        else:
            now = timezone.now().replace(microsecond=0)
            return now - self.start_time if now > self.start_time else timedelta(seconds=0)

    @property
    def save_time(self):
        """结果保存时间
        """
        if not self.closing_time:
            return None
        if self.end_time:
            return self.end_time - self.closing_time
        else:
            return timezone.now().replace(microsecond=0) - self.closing_time

    @property
    def result_code_msg(self):
        """结果码描述
        """
        return errcode.interpret_code(self.result_code)

    @property
    def context(self):
        """任务参数下载
        """
        try:
            if os.path.isfile(self.context_path):
                with open(self.context_path, "r") as f:
                    return json.loads(f.read())
            else:
                content = file_server.get_file(self.context_path)
                return json.loads(content)
        except Exception as e:
            logger.exception(e)
            return None

    @context.setter
    def context(self, context):
        """任务参数上传
        """
        context_uuid = str(uuid.uuid1().hex)
        context_path = "jobdata/projects/%d/job%d/%s/job_context.json" % (self.get_project_id(), self.id, context_uuid)
        try:
            context_url = file_server.put_file(json.dumps(context), context_path, file_server.TypeEnum.TEMPORARY)
            self.context_path = context_url
        except Exception as e:
            logger.exception(e)
            raise CDErrorBase(errcode.E_SERVER_FILE_SERVICE_ERROR, "文件服务器异常")

    @property
    def result(self):
        """结果下载
        """
        try:
            result = file_server.get_file(self.result_path)
            return json.loads(result)
        except Exception as e:
            logger.exception(e)
            return None

    @result.setter
    def result(self, result):
        """结果上传
        """
        result_uuid = str(uuid.uuid1().hex)
        result_path = "jobdata/projects/%d/job%d/%s/result_data.json" % (self.get_project_id(), self.id, result_uuid)
        try:
            result_url = file_server.put_file(json.dumps(result), result_path, file_server.TypeEnum.TEMPORARY)
            self.result_path = result_url
        except Exception as e:  # 所有file server的异常
            logger.exception(e)
            raise CDErrorBase(errcode.E_SERVER_FILE_SERVICE_ERROR, "文件服务器异常")

    def result_for_display(self):
        """结果展示
        """
        return json.dumps(self.result, ensure_ascii=False, indent=1)

    def context_for_display(self):
        """参数展示
        """
        context = self.context
        if isinstance(context, dict) and "scm_password" in context:
            context["scm_password"] = "***"
        return json.dumps(context, ensure_ascii=False, indent=1)

    def __str__(self):
        return "%d" % self.id


class Job(BaseJob):
    """
    任务数据库定义
    """
    project = models.ForeignKey(Project, verbose_name="所属项目", on_delete=models.CASCADE)
    remarked_by = models.ForeignKey("auth.User", blank=True, null=True, related_name="+", on_delete=models.SET_NULL,
                                    verbose_name="备注人")
    archived = models.BooleanField(verbose_name="标记job是否已完成归档", blank=True, null=True)

    def get_project_id(self):
        return self.project.id


class TaskRunTime:

    @property
    def waiting_time(self):
        """等待时间
        """
        if self.start_time:
            return self.start_time - self.create_time if self.start_time > self.create_time else timedelta(seconds=0)
        elif self.end_time:
            return self.end_time - self.create_time if self.end_time > self.create_time else timedelta(seconds=0)
        else:
            waiting_time = timezone.now().replace(microsecond=0) - self.create_time
            if waiting_time.total_seconds() > 0:
                return waiting_time
            else:
                return timedelta(seconds=0)

    @property
    def execute_time(self):
        """执行时间
        """
        if not self.start_time:
            return None
        if self.end_time:
            return self.end_time - self.start_time
        else:
            execute_time = timezone.now().replace(microsecond=0) - self.start_time
            if execute_time.total_seconds() > 0:
                return execute_time
            else:
                return timedelta(seconds=0)


class BaseTask(models.Model, TaskRunTime):
    """Task 抽象基类"""

    class StateEnum(object):
        WAITING = 0
        RUNNING = 1
        CLOSED = 2
        CREATING = 3
        ACKING = 4

    STATE_CHOICES = (
        (StateEnum.CREATING, "Creating"),
        (StateEnum.WAITING, "Waiting"),
        (StateEnum.ACKING, "Acking"),
        (StateEnum.RUNNING, "Running"),
        (StateEnum.CLOSED, "Closed"))

    module = models.CharField(max_length=64, verbose_name="模块")
    task_name = models.CharField(max_length=64, verbose_name="名称")
    params_path = models.CharField(max_length=256, verbose_name="参数路径", null=True, blank=True)
    private = models.BooleanField(default=False, verbose_name="私有")
    result_code = models.IntegerField(null=True, verbose_name="结果码", blank=True)
    result_msg = models.TextField(default=None, verbose_name="结果信息", null=True, blank=True)
    result_path = models.TextField(verbose_name="结果路径", null=True, blank=True)
    create_version = models.CharField(max_length=56, verbose_name="创建版本号", null=True, blank=True)
    execute_version = models.CharField(max_length=56, verbose_name="执行版本号", null=True, blank=True)
    start_time = models.DateTimeField(null=True, verbose_name="启动时间", blank=True)
    end_time = models.DateTimeField(null=True, verbose_name="结束时间", blank=True)
    state = models.IntegerField(default=StateEnum.CREATING, choices=STATE_CHOICES, verbose_name="状态", db_index=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    register_time = models.DateTimeField(null=True, verbose_name="注册时间", blank=True)
    log_url = models.TextField(verbose_name="日志链接", null=True, blank=True)
    progress_rate = models.IntegerField(default=0, verbose_name="完成进度")
    last_beat_time = models.DateTimeField(null=True, verbose_name="心跳时间", blank=True, auto_now_add=True)

    class Meta:
        abstract = True
        index_together = (
            ("result_code", "create_time"),
            ("task_name", "result_code", "end_time"),
            ("task_name", "start_time"),
        )

    def get_job_id(self):
        raise NotImplementedError

    def get_project_id(self):
        raise NotImplementedError

    @property
    def result_code_msg(self):
        """结果码描述
        """
        return errcode.interpret_code(self.result_code)

    @property
    def task_params(self):
        """任务参数下载
        """
        try:
            if os.path.isfile(self.params_path):
                with open(self.params_path, "r") as f:
                    return json.loads(f.read())
            else:
                content = file_server.get_file(self.params_path)
                return json.loads(content)
        except Exception as e:
            logger.exception(e)
            return None

    @task_params.setter
    def task_params(self, params):
        """任务参数上传
        """
        param_uuid = str(uuid.uuid1().hex)
        params_path = "jobdata/projects/%d/job%d/%s/task_params_%d.json" % (
            self.get_project_id(), self.get_job_id(), param_uuid, self.id)
        try:
            params_url = file_server.put_file(json.dumps(params), params_path, file_server.TypeEnum.TEMPORARY)
            self.params_path = params_url
        except Exception as e:
            logger.exception(e)
            raise CDErrorBase(errcode.E_SERVER_FILE_SERVICE_ERROR, "文件服务器异常")

    def task_params_for_display(self):
        """展示的任务参数
        """
        task_params = self.task_params
        if isinstance(task_params, dict) and "scm_password" in task_params:
            task_params["scm_password"] = "***"

        return json.dumps(task_params, ensure_ascii=False, indent=1)

    @property
    def result(self):
        """下载结果
        """
        try:
            if os.path.isfile(self.result_path):
                with open(self.result_path, "r") as f:
                    return json.loads(f.read())
            else:
                content = file_server.get_file(self.result_path)
                return json.loads(content)
        except Exception as e:
            logger.exception(e)
            return None

    @result.setter
    def result(self, result):
        """上传结果
        """
        result_uuid = str(uuid.uuid1().hex)
        result_path = "jobdata/projects/%d/job%d/%s/task_result_%d.json" % (
            self.get_project_id(), self.get_job_id(), result_uuid, self.id)
        try:
            result_url = file_server.put_file(json.dumps(result), result_path, file_server.TypeEnum.TEMPORARY)
            self.result_path = result_url
        except Exception as e:
            logger.exception(e)
            raise CDErrorBase(errcode.E_SERVER_FILE_SERVICE_ERROR, "文件服务器异常")

    def result_for_display(self):
        """结果展示
        """
        if errcode.is_success(self.result_code):
            return json.dumps(self.result, ensure_ascii=False, indent=1)
        else:
            return self.result

    @property
    def left_time(self):
        if self.execute_time and 0 < self.progress_rate < 100:
            return self.execute_time * 100 / self.progress_rate

    def __str__(self):
        return "%s.%s" % (self.module, self.task_name)


class Task(BaseTask):
    """
    任务子任务数据库定义，即node节点实际取得并执行的任务
    """
    job = models.ForeignKey(Job, verbose_name="所属任务", on_delete=models.CASCADE)
    exec_tags = models.ManyToManyField(ExecTag, verbose_name="执行标签")
    tag = models.ForeignKey(ExecTag, on_delete=models.SET_NULL, verbose_name="唯一执行标签", null=True, blank=True,
                            related_name="tasks")
    node = models.ForeignKey(Node, verbose_name="执行节点", on_delete=models.SET_NULL, null=True,
                             blank=True)
    processes = models.ManyToManyField(Process, verbose_name="子进程", through="TaskProcessRelation")

    def get_job_id(self):
        return self.job.id

    def get_project_id(self):
        return self.job.project.id

    class Meta(BaseTask.Meta):
        unique_together = ("job", "task_name")


class BaseTaskProgress(models.Model):
    """TaskProgress 抽象基类"""
    message = models.CharField(max_length=512, verbose_name="进展信息")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    progress_rate = models.IntegerField(verbose_name="完成进度", null=True, blank=True)

    class Meta:
        abstract = True


class TaskProgress(BaseTaskProgress):
    """子任务进度表"""
    task = models.ForeignKey(Task, verbose_name="Task", on_delete=models.CASCADE)
    node = models.ForeignKey(Node, verbose_name="节点", on_delete=models.SET_NULL, null=True, blank=True)


class BaseTaskProcessRelation(models.Model, TaskRunTime):
    """TaskProcessRelation 抽象基类"""

    class StateEnum(object):
        WAITING = 0
        RUNNING = 1
        CLOSED = 2
        CREATING = 3
        ACKING = 4

    STATE_CHOICES = (
        (StateEnum.CREATING, "Creating"),
        (StateEnum.WAITING, "Waiting"),
        (StateEnum.ACKING, "Acking"),
        (StateEnum.RUNNING, "Running"),
        (StateEnum.CLOSED, "Closed"))

    priority = models.IntegerField(verbose_name="优先级", null=True, blank=True)  # 一个工具子进程的优先级，0为最高，为空时按照创建的先后顺序来
    state = models.IntegerField(default=StateEnum.WAITING, choices=STATE_CHOICES, verbose_name="状态")
    private = models.BooleanField(default=False, verbose_name="私有")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    start_time = models.DateTimeField(verbose_name="启动时间", null=True, blank=True)
    end_time = models.DateTimeField(verbose_name="结束时间", null=True, blank=True)
    result_code = models.IntegerField(verbose_name="结果码", null=True, blank=True)
    result_msg = models.TextField(default=None, verbose_name="结果信息", null=True, blank=True)
    result_url = models.TextField(verbose_name="结果路径", null=True, blank=True)
    log_url = models.TextField(verbose_name="日志链接", null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def result_code_msg(self):
        return errcode.interpret_code(self.result_code)


class TaskProcessRelation(BaseTaskProcessRelation):
    """子任务子进程表"""

    task = models.ForeignKey(Task, verbose_name="子任务", on_delete=models.CASCADE)
    process = models.ForeignKey(Process, verbose_name="任务子进程", on_delete=models.CASCADE)
    node = models.ForeignKey(Node, verbose_name="执行节点", on_delete=models.SET_NULL, null=True,
                             blank=True)  # 被执行的节点，删除节点不删除task

    class Meta:
        ordering = ["task__id", "priority"]
        unique_together = (
            ("task", "process"),
        )
        index_together = (
            ("node", "state"),
        )

    def __str__(self):
        return self.process.name


class TaskProcessNodeQueue(models.Model):
    """任务预先分配队列
    """
    id = models.BigAutoField(primary_key=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    task_process = models.ForeignKey(TaskProcessRelation, null=True, blank=True, on_delete=models.CASCADE)
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        index_together = (
            ("node", "task_process"),
        )


class KillingTask(models.Model):
    """终止任务记录
    """
    node = models.ForeignKey(Node, verbose_name="执行节点", on_delete=models.SET_NULL, null=True,
                             blank=True)
    task = models.ForeignKey(Task, verbose_name="Task", on_delete=models.CASCADE)
    killed_time = models.DateTimeField(null=True, verbose_name="终止时间", blank=True)
