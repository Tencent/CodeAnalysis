# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
apps.job.serializers.v3

定义：此处定义了供apis.py接口使用的Serializers
"""

from rest_framework import serializers

from apps.job import models
from apps.job.serializers import base
from apps.base.serializers import TimeDeltaSerializer


class TaskSerializeV3(serializers.ModelSerializer):
    class Meta:
        model = models.Task
        fields = ['id', 'module', 'task_name', 'progress_rate',
                  'state', 'result_code', 'result_msg', ]


class JobSimpleSerializerV3(serializers.ModelSerializer):
    class Meta:
        model = models.Job
        fields = ["id", "state", "result_code", "result_msg", "code_line_num",
                  "comment_line_num", "blank_line_num", "total_line_num"]
        read_only_fields = ["id", "state", "result_code", "result_msg"]


class JobSerializerV3(serializers.ModelSerializer):
    tasks = TaskSerializeV3(source="task_set", many=True, read_only=True)
    project = base.JobProjectSerializer(read_only=True)
    waiting_time = TimeDeltaSerializer(read_only=True)
    execute_time = TimeDeltaSerializer(read_only=True)
    save_time = TimeDeltaSerializer(read_only=True)

    class Meta:
        model = models.Job
        fields = ['id', 'scan_id', 'create_time', 'waiting_time', 'start_time', 'execute_time', 'save_time', 'project',
                  'end_time', 'expire_time', 'task_num', 'task_done', 'tasks', 'state', 'result_code',
                  'result_code_msg', 'result_msg', 'remarks', 'remarked_by', 'code_line_num', 'comment_line_num',
                  'blank_line_num', 'total_line_num', 'created_from', 'creator']

