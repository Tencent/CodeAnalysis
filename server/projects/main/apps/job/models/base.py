# -*- coding: utf-8 -*-
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


class Job(models.Model):
    """
    任务数据库定义
    """

    class StateEnum(object):
        WAITING = 0
        RUNNING = 1
        CLOSED = 2
        CLOSING = 3
        # 2020-08-14 补充初始化状态
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
    project = models.ForeignKey(Project, verbose_name="所属项目", on_delete=models.CASCADE)
    scan_id = models.IntegerField(verbose_name="扫描id", null=True, blank=True)
    state = models.IntegerField(default=StateEnum.WAITING, choices=STATE_CHOICES, verbose_name="状态", db_index=True)
    initialized_time = models.DateTimeField(null=True, verbose_name="任务初始化完成时间", blank=True)
    start_time = models.DateTimeField(null=True, verbose_name="启动时间", blank=True)
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
    remarked_by = models.ForeignKey('auth.User', blank=True, null=True, related_name="+", on_delete=models.SET_NULL,
                                    verbose_name="备注人")

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

    class Meta:
        index_together = (
            ("create_time", "result_code"),
            ("start_time", "result_code"),
            ("end_time", "result_code"),
        )

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
        """执行时间
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
        context_path = "jobdata/projects/%d/job%d/%s/job_context.json" % (self.project.id, self.id, context_uuid)
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
        result_path = self.result_path or os.path.join(settings.BASE_DIR, "jobdata", "job%d" % self.id,
                                                       "result_data.json")
        try:
            if os.path.isfile(result_path):
                with open(result_path, "r") as f:
                    return json.loads(f.read())
            else:
                result = file_server.get_file(result_path)
                return json.loads(result)
        except Exception as e:
            logger.exception(e)
            return None

    @result.setter
    def result(self, result):
        """结果上传
        """
        result_uuid = str(uuid.uuid1().hex)
        result_path = "jobdata/projects/%d/job%d/%s/result_data.json" % (self.project.id, self.id, result_uuid)
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
            now = timezone.now().replace(microsecond=0)
            return now - self.create_time if now > self.create_time else timedelta(seconds=0)

    @property
    def execute_time(self):
        """执行时间
        """
        if not self.start_time:
            return None
        if self.end_time:
            return self.end_time - self.start_time
        else:
            now = timezone.now().replace(microsecond=0)
            return now - self.start_time if now > self.start_time else timedelta(seconds=0)


class Task(models.Model, TaskRunTime):
    """
    任务子任务数据库定义，即node节点实际取得并执行的任务
    """

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

    job = models.ForeignKey(Job, verbose_name="所属任务", on_delete=models.CASCADE)
    module = models.CharField(max_length=64, verbose_name="模块")
    task_name = models.CharField(max_length=64, verbose_name="名称")
    params_path = models.CharField(max_length=256, verbose_name="参数路径", null=True, blank=True)
    exec_tags = models.ManyToManyField(ExecTag, verbose_name="执行标签")
    tag = models.ForeignKey(ExecTag, on_delete=models.SET_NULL, verbose_name="唯一执行标签", null=True, blank=True,
                            related_name="tasks")
    node = models.ForeignKey(Node, verbose_name="执行节点", on_delete=models.SET_NULL, null=True,
                             blank=True)
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
    log_url = models.URLField(verbose_name="日志链接", null=True, blank=True)
    progress_rate = models.IntegerField(default=0, verbose_name="完成进度")
    processes = models.ManyToManyField(Process, verbose_name="子进程", through="TaskProcessRelation")
    last_beat_time = models.DateTimeField(null=True, verbose_name="心跳时间", blank=True, auto_now_add=True)

    class Meta:
        unique_together = ("job", "task_name")
        index_together = (
            ("result_code", "create_time"),
            ("task_name", "result_code", "end_time"),
            ("task_name", "start_time"),
        )

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
            self.job.project.id, self.job.id, param_uuid, self.id)
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
            self.job.project.id, self.job.id, result_uuid, self.id)
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

    def __str__(self):
        return "%s.%s" % (self.module, self.task_name)


class TaskProgress(models.Model):
    task = models.ForeignKey(Task, verbose_name="Task", on_delete=models.CASCADE)
    message = models.CharField(max_length=512, verbose_name="进展信息")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    node = models.ForeignKey(Node, verbose_name="节点", on_delete=models.SET_NULL, null=True, blank=True)
    progress_rate = models.IntegerField(verbose_name="完成进度", null=True, blank=True)


class TaskProcessRelation(models.Model, TaskRunTime):
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

    task = models.ForeignKey(Task, verbose_name="子任务", on_delete=models.CASCADE)
    process = models.ForeignKey(Process, verbose_name="任务子进程", on_delete=models.CASCADE)
    priority = models.IntegerField(verbose_name="优先级", null=True, blank=True)
    state = models.IntegerField(default=StateEnum.WAITING, choices=STATE_CHOICES, verbose_name="状态")
    private = models.BooleanField(default=False, verbose_name="私有")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    start_time = models.DateTimeField(verbose_name="启动时间", null=True, blank=True)
    end_time = models.DateTimeField(verbose_name="结束时间", null=True, blank=True)
    node = models.ForeignKey(Node, verbose_name="执行节点", on_delete=models.SET_NULL, null=True,
                             blank=True)
    result_code = models.IntegerField(verbose_name="结果码", null=True, blank=True)
    result_msg = models.TextField(default=None, verbose_name="结果信息", null=True, blank=True)
    result_url = models.TextField(verbose_name="结果路径", null=True, blank=True)
    log_url = models.URLField(verbose_name="日志链接", null=True, blank=True)

    @property
    def result_code_msg(self):
        return errcode.interpret_code(self.result_code)

    class Meta:
        ordering = ['task__id', 'priority']
        unique_together = (("task", "process"),)
        index_together = (("node", "state"),)

    def __str__(self):
        return self.process.name
