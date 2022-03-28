# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
nodemgr - base serializer
"""
# python 原生import
import logging

# 第三方 import
from django.contrib.auth.models import User
from rest_framework import serializers

# 项目内 import
from apps.job.models import Task
from apps.nodemgr import models

logger = logging.getLogger(__name__)


class ExecTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExecTag
        fields = '__all__'


class NodeRegisterSerializer(serializers.Serializer):
    uuid = serializers.CharField(max_length=64, help_text="UUID")
    tag = serializers.SlugRelatedField(
        slug_field="name", queryset=models.ExecTag.objects.all(), required=False, allow_null=True)
    os_info = serializers.CharField(
        max_length=256, help_text="机器系统信息", required=False, allow_blank=True, allow_null=True)


class NodeStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NodeStatus
        fields = "__all__"
        read_only_fields = ["node"]


class NodeSerializer(serializers.ModelSerializer):
    manager = serializers.SlugRelatedField(
        queryset=User.objects.all(), slug_field="username")
    exec_tags = serializers.SlugRelatedField(
        queryset=models.ExecTag.objects.all(), slug_field="name", many=True)
    nodestatus = serializers.SerializerMethodField()

    def get_nodestatus(self, node):
        nodestatus = node.nodestatus_set.order_by("id").last()
        return NodeStatusSerializer(instance=nodestatus).data

    class Meta:
        model = models.Node
        fields = ["id", "name", "addr", "enabled", "last_beat_time", "state",
                  "uuid", "manager", "nodestatus", "exec_tags", "created_time",
                  "creator", "modified_time", "modifier", "deleted_time", "deleter"]
        read_only_fields = ["addr", "last_beat_time", "state", "uuid",
                            "created_time", "creator", "modified_time",
                            "modifier", "deleted_time", "deleter", "nodestatus"]


class NodeTaskSerializer(serializers.ModelSerializer):
    """节点任务序列化
    """
    project = serializers.SerializerMethodField()

    def get_project(self, task):
        project = task.job.project
        branch = project.branch
        repo_scm_url = project.repo.scm_url
        return {
            "id": project.id,
            "branch": branch,
            "scm_url": repo_scm_url
        }

    class Meta:
        model = Task
        fields = ["id", "project", "module", "task_name",
                  "result_code", "result_msg", "state", "job", "node", "result_code_msg"]
