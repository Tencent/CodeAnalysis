# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
base - base serializers
"""
from rest_framework import serializers

from apps.base.models import OperationRecord
from apps.authen.serializers.base import UserSimpleSerializer


class TimeDeltaSerializer(serializers.Serializer):
    """秒数序列化
    """

    def to_representation(self, instance):
        return str(instance.total_seconds())


class OnlySuperAdminReadField(serializers.Field):
    """仅超级管理员可见的字段
    """

    def __init__(self, **kwargs):
        kwargs['read_only'] = True
        super().__init__(**kwargs)

    def to_representation(self, value):
        request = self.context.get("request")
        if request and request.user and request.user.is_staff:
            return value
        else:
            return ""


class ChoicesField(serializers.Field):
    def __init__(self, choices, **kwargs):
        self._choices = dict(choices)
        super(ChoicesField, self).__init__(**kwargs)

    def to_representation(self, obj):
        return self._choices[obj]

    def to_internal_value(self, data):
        try:
            return list(self._choices.keys())[list(self._choices.values()).index(data)]
        except ValueError:
            raise serializers.ValidationError("选项值只可为：%s" % '; '.join(
                [str(i) for i in self._choices.values()]))


class CDBaseModelSerializer(serializers.ModelSerializer):
    creator = UserSimpleSerializer(read_only=True)
    created_time = serializers.StringRelatedField()
    modifier = UserSimpleSerializer(read_only=True)
    modified_time = serializers.StringRelatedField()
    deleter = UserSimpleSerializer(read_only=True)
    deleted_time = serializers.StringRelatedField()


class OperationRecordSerializer(serializers.ModelSerializer):
    """操作记录序列化
    """
    class Meta:
        model = OperationRecord
        fields = '__all__'
