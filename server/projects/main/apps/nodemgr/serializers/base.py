# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
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
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework import serializers

# 项目内 import
from apps.authen.serializers.base_org import OrganizationSimpleSerializer
from apps.job.models import Task
from apps.nodemgr import models

logger = logging.getLogger(__name__)


class ExecTagSerializer(serializers.ModelSerializer):
    org_info = OrganizationSimpleSerializer(read_only=True)

    class Meta:
        model = models.ExecTag
        fields = '__all__'


class NodeIDRelatedField(serializers.PrimaryKeyRelatedField):
    """节点ID序列化
    """

    def __init__(self, **kwargs):
        self.queryset = models.Node.objects.all()
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        query_fields = None
        user = self.context.get("request").user
        if not user.is_superuser:
            query_fields = Q(manager=user) | Q(related_managers=user)
        try:
            if query_fields:
                return self.queryset.get(pk=data).get(query_fields)
            else:
                return self.queryset.get(pk=data)
        except ObjectDoesNotExist:
            self.fail('does_not_exist', pk_value=data)
        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(data).__name__)


class NodeRegisterSerializer(serializers.Serializer):
    uuid = serializers.CharField(max_length=64, help_text="UUID")
    org_sid = serializers.CharField(max_length=64, help_text="团队编号", required=False,
                                    allow_null=True, allow_blank=True)
    tag = serializers.SlugRelatedField(
        slug_field="name", queryset=models.ExecTag.objects.all(), required=False, allow_null=True)
    os_info = serializers.CharField(
        max_length=256, help_text="机器系统信息", required=False, allow_blank=True, allow_null=True)


class NodeStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NodeStatus
        fields = "__all__"
        read_only_fields = ["node"]


class NodeProcessesBatchUpdateSerializer(serializers.Serializer):
    """节点进程批量序列化
    """
    node_ids = serializers.ListField(child=NodeIDRelatedField(help_text="节点编号"))
    processes = serializers.JSONField(help_text="节点进程配置")


class NodeSerializer(serializers.ModelSerializer):
    """节点序列化
    """
    manager = serializers.SlugRelatedField(
        queryset=User.objects.all(), slug_field="username")
    related_managers = serializers.SlugRelatedField(
        queryset=User.objects.all(), slug_field="username", many=True, required=False,
        allow_null=True, allow_empty=True)
    exec_tags = serializers.SlugRelatedField(
        queryset=models.ExecTag.objects.all(), slug_field="name", many=True)
    exec_tag_details = ExecTagSerializer(source="exec_tags", many=True, read_only=True)
    org_info = OrganizationSimpleSerializer(read_only=True)
    nodestatus = serializers.SerializerMethodField()

    def get_nodestatus(self, node):
        nodestatus = node.nodestatus_set.order_by("id").last()
        return NodeStatusSerializer(instance=nodestatus).data

    class Meta:
        model = models.Node
        fields = ["id", "name", "addr", "enabled", "last_beat_time", "state", "related_managers",
                  "uuid", "manager", "nodestatus", "exec_tags", "created_time", "org_sid", "org_info",
                  "creator", "modified_time", "modifier", "deleted_time", "deleter", "exec_tag_details"]
        read_only_fields = ["addr", "last_beat_time", "state", "uuid",
                            "created_time", "creator", "modified_time",
                            "modifier", "deleted_time", "deleter", "nodestatus", "org_info", "exec_tag_details"]


class NodeBatchUpdateSerializer(serializers.Serializer):
    """节点批量更新序列化
    """
    node_ids = serializers.ListField(child=NodeIDRelatedField(help_text="节点编号"))
    related_managers = serializers.SlugRelatedField(
        queryset=User.objects.all(), slug_field="username", many=True,
        allow_null=True, allow_empty=True, required=False)
    exec_tags = serializers.SlugRelatedField(
        queryset=models.ExecTag.objects.all(), slug_field="name", many=True,
        allow_null=True, allow_empty=True, required=False)
    enabled = serializers.ChoiceField(
        choices=models.Node.ENABLED_CHOICES, required=False, help_text="节点状态")


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
            "repo_id": project.repo_id,
            "scm_url": repo_scm_url
        }

    class Meta:
        model = Task
        fields = ["id", "project", "module", "task_name",
                  "result_code", "result_msg", "state", "job", "node", "result_code_msg"]
