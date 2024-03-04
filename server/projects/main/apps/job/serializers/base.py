# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
job - base serializer
"""
# python 原生import
import logging

# 第三方 import
from django.conf import settings
from rest_framework import serializers

# 项目内 import
from apps.authen.serializers.base_org import OrganizationSimpleSerializer
from apps.base.serializers import TimeDeltaSerializer
from apps.codeproj.models import Project
from apps.codeproj.serializers.base import ProjectTeamSimpleSerializer
from apps.job import models

logger = logging.getLogger(__name__)


class TaskBriefSerializer(serializers.ModelSerializer):
    """任务序列化
    """

    class Meta:
        model = models.Task
        fields = ["id", "module", "task_name", "progress_rate",
                  "state", "result_code", "result_msg", "result_path"]


class JobProjectSerializer(serializers.ModelSerializer):
    """任务项目信息序列化
    """
    repo_scm_url = serializers.CharField(source="repo.scm_url", help_text="代码库地址")
    organization = OrganizationSimpleSerializer(read_only=True, source="repo.organization")
    project_team = ProjectTeamSimpleSerializer(read_only=True, source="repo.project_team")

    class Meta:
        model = Project
        fields = ["id", "branch", "repo_id", "scan_scheme", "repo_scm_url", "organization", "project_team"]


class JobCodeLineSerializer(serializers.ModelSerializer):
    """任务代码行信息序列化
    """

    class Meta:
        model = models.Job
        fields = ["id", "state", "result_code", "result_msg", "code_line_num",
                  "comment_line_num", "blank_line_num", "total_line_num",
                  "efficient_comment_line_num", "filtered_efficient_comment_line_num"]
        read_only_fields = ["id", "state", "result_code", "result_msg"]


class JobSerializer(serializers.ModelSerializer):
    """任务详情序列化
    包含子任务信息
    """
    tasks = TaskBriefSerializer(source="task_set", many=True, read_only=True)
    project = JobProjectSerializer(read_only=True)
    waiting_time = TimeDeltaSerializer(read_only=True)
    execute_time = TimeDeltaSerializer(read_only=True)
    save_time = TimeDeltaSerializer(read_only=True)

    class Meta:
        model = models.Job
        fields = ["id", "scan_id", "create_time", "waiting_time", "start_time", "execute_time", "save_time", "project",
                  "end_time", "expire_time", "context_path", "task_num", "task_done", "tasks",
                  "state", "result_code", "result_code_msg", "result_msg", "result_path", "remarks", "remarked_by",
                  "code_line_num", "comment_line_num", "blank_line_num", "total_line_num", "efficient_comment_line_num",
                  "filtered_efficient_comment_line_num", "created_from", "creator"]


class JobCancelSerializer(serializers.Serializer):
    """取消任务参数序列化
    """
    remarks = serializers.CharField(max_length=512, help_text="取消备注")
    force = serializers.BooleanField(
        help_text="强制关闭（可能会影响数据入库）", default=False, allow_null=True, required=False)


class TaskSerializer(serializers.ModelSerializer):
    """子任务序列化
    """

    class Meta:
        model = models.Task
        fields = "__all__"


class JobInfoSimpleSerializer(serializers.ModelSerializer):
    """Job简单的info信息序列化
    """

    class Meta:
        model = models.Job
        fields = ["id", "project", "code_line_num", "comment_line_num", "blank_line_num",
                  "total_line_num", "state"]


class TaskProcessSerializer(serializers.ModelSerializer):
    process = serializers.SlugRelatedField(read_only=True, slug_field="name")

    class Meta:
        model = models.TaskProcessRelation
        fields = "__all__"


class ExcutableTaskSerializer(serializers.ModelSerializer):
    """提供给节点端执行的任务参数
    """
    task_params = serializers.JSONField()
    taskprocessrelation_set = TaskProcessSerializer(many=True, read_only=True)
    tag = serializers.SlugRelatedField(read_only=True, slug_field="name")
    task_version = serializers.CharField(
        source="create_version", read_only=True)

    class Meta:
        model = models.Task
        exclude = ["processes", "exec_tags", "result_code",
                   "result_msg", "result_path", "node", "params_path"]


class TaskInfoSerializer(serializers.ModelSerializer):
    """taskinfo序列化
    """
    tag = serializers.SlugRelatedField(help_text="关联节点标签", slug_field="name", read_only=True)
    node = serializers.SerializerMethodField(read_only=True)
    job = JobInfoSimpleSerializer(read_only=True)
    total_time = serializers.SerializerMethodField(read_only=True)

    def get_node(self, task):
        node = task.node
        return {
            "id": task.node_id,
            "name": node.name,
            "addr": node.addr
        } if node else None

    def get_total_time(self, task):
        if task.execute_time and task.waiting_time:
            return task.waiting_time + task.execute_time
        elif task.waiting_time:
            return task.waiting_time
        else:
            return None

    class Meta:
        model = models.Task
        fields = ["id", "job", "tag", "task_name", "node", "total_time",
                  "private", "result_code", "result_msg", "create_time",
                  "start_time", "end_time", "state", "result_code_msg",
                  "module", "execute_time"]


class TaskExceptionInfoSerializer(TaskInfoSerializer):
    """异常任务序列化，在TaskInfoSerializer基础上增加job_url
    """

    job_url = serializers.SerializerMethodField(read_only=True)

    def get_job_url(self, task):
        return "%s/jobs/%d/tasks?project_id=%d" % (settings.LOCAL_DOMAIN, task.job_id, task.job.project_id)

    class Meta:
        model = models.Task
        fields = ["id", "job", "tag", "task_name", "node", "total_time",
                  "private", "result_code", "result_msg", "create_time",
                  "start_time", "end_time", "state", "result_code_msg",
                  "module", "job_url"]


class JobClosedSerializer(serializers.Serializer):
    """任务结果参数序列化
    """
    result_code = serializers.IntegerField(help_text="结果码")
    result_path = serializers.CharField(
        help_text="结果路径", required=False, allow_blank=True, allow_null=True)
    result_msg = serializers.CharField(
        help_text="结果消息", allow_blank=True, allow_null=True)
    result_data = serializers.JSONField(
        help_text="统计结果，包含code_lint_info, code_metric_cc_info, code_metric_dup_info, code_metric_cloc_info等")


class TaskResultSerializer(serializers.Serializer):
    """任务结果序列化
    """
    task_version = serializers.CharField(max_length=56, help_text="任务的执行版本")
    result_code = serializers.IntegerField(help_text="结果码")
    result_data_url = serializers.CharField(help_text="结果路径", allow_null=True, allow_blank=True)
    result_msg = serializers.CharField(max_length=256, help_text="结果信息")
    log_url = serializers.CharField(help_text="日志链接", allow_null=True, allow_blank=True)
    processes = serializers.ListField(child=serializers.CharField(
        max_length=64, help_text="进程"), allow_null=True)


class TaskProgressSerializer(serializers.ModelSerializer):
    """任务进度序列化
    """

    def validate_progress_rate(self, value):
        """校验上报进度
        """
        if 0 > value or 100 < value:
            raise serializers.ValidationError("progress_rate 取值范围 0~100")
        return value

    def validate(self, attrs):
        """检查任务状态
        """
        if attrs["task"].state != models.Task.StateEnum.RUNNING:
            raise serializers.ValidationError({"task": "指定Task已经不在运行中"})
        return serializers.ModelSerializer.validate(self, attrs)

    class Meta:
        model = models.TaskProgress
        fields = "__all__"


class TaskResultSerializer(serializers.Serializer):
    task_version = serializers.CharField(max_length=56, help_text="任务的执行版本")
    result_code = serializers.IntegerField(help_text="结果码")
    result_data_url = serializers.CharField(help_text="结果路径", allow_null=True, allow_blank=True)
    result_msg = serializers.CharField(max_length=256, help_text="结果信息")
    log_url = serializers.CharField(help_text="日志链接", allow_null=True, allow_blank=True)
    processes = serializers.ListField(child=serializers.CharField(
        max_length=64, help_text="进程"), allow_null=True)
