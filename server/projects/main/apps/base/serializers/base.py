# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
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
