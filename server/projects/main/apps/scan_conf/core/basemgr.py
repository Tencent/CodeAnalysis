# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - base core
"""
import logging

# 第三方
from django.db.models import Count, ForeignKey
from django.db import IntegrityError
from rest_framework.utils import model_meta
from rest_framework.exceptions import ParseError

# 项目内
from apps.scan_conf import models
from apps.scan_conf.api_filters import base as base_filters
from apps.base.basemodel import CDBaseModel

logger = logging.getLogger(__name__)


class ModelManager(object):
    """model manager
    用于辅助其他manager的create_or_update
    """

    @classmethod
    def create(cls, model, user=None, **kwargs):
        """创建对象
        :param model: Model Object, 对象
        :param user: User, 操作对象, 用于CDBaseModel保存creator
        :params kwargs: 创建model所需的参数
        :return: instance
        """
        try:
            ignore_conflict = kwargs.pop("ignore_conflict", False)
            instance, created = model.objects.get_or_create(**kwargs)
            if not created:
                if ignore_conflict:
                    return instance
                raise ParseError("已存在，请勿重复创建")
            if user and isinstance(instance, CDBaseModel):
                instance.creator = user
                instance.save()
            return instance
        except IntegrityError as e:
            logger.exception(e)
            raise ParseError("创建失败，%s" % e)
        except ParseError as e:
            raise ParseError(e)
        except Exception as e:
            logger.exception(e)
            raise ParseError("系统错误，创建失败，请联系平台管理员")

    @classmethod
    def update(cls, instance, user=None, **kwargs):
        """更新
        :param instance: model
        :param user: User, 操作对象，用于CDBaseModel更新modifier等
        :params kwargs: 其他参数
        :return: instance
        """
        info = model_meta.get_field_info(instance)

        # update
        m2m_fields = []
        for attr, value in kwargs.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            elif attr in info.fields or attr in info.relations:
                # 避免kwargs多余参数导致instance报错
                setattr(instance, attr, value)
        try:
            if user and isinstance(instance, CDBaseModel):
                instance.save(user=user)
            else:
                instance.save()
        except IntegrityError as e:
            logger.exception(e)
            raise ParseError("更新失败，%s" % e)
        except Exception as e:
            logger.exception(e)
            raise ParseError("系统错误，更新失败，请联系平台管理员")

        # m2m
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance

    @classmethod
    def create_or_update(cls, model, instance=None, user=None, **kwargs):
        """创建或更新
        :param model: Model Object, 对象
        :param instance: instance, 存在则为更新操作，否则为保存操作
        :param user: User, 操作人，
        :params kwargs: 其他参数，其中update_data表示更新参数
        :return: (instance, created)
        """
        update_data = kwargs.pop("update_data", {})
        if not instance:
            instance = cls.create(model, user, **kwargs)
            created = True
        else:
            created = False
        instance = cls.update(instance, user, **update_data)
        return instance, created


class FilterManger(object):
    """筛选项manager
    """
    @classmethod
    def format_fk_display_name(cls, model_field, user=None):
        """格式化外建显示名称"""
        if isinstance(model_field, models.CheckTool):
            # 兼容工具名称隐藏
            return model_field.get_show_name(user)
        return str(model_field)

    @classmethod
    def _get_filter(cls, queryset, field_maps, model, user=None):
        filter_map = {}
        for field, field_name in field_maps.items():
            # 获取字段model
            model_field = model
            for f in field_name.split("__"):
                if hasattr(model_field, '_meta'):
                    model_field = model_field._meta.get_field(f)
                else:
                    model_field = model_field.related_model._meta.get_field(f)
            choices = []
            # model_field.choices 可能为None
            field_choices = model_field.choices or []
            choices_dict = dict(field_choices)
            if field_choices:
                for choice in queryset.values(field_name).annotate(count=Count('id')):
                    if choice.get(field_name):
                        choices.append({"display_name": choices_dict[choice[field_name]],
                                        "value": choice[field_name],
                                        "count": choice["count"]})
            elif isinstance(model_field, ForeignKey):
                for choice in queryset.values(field_name).annotate(count=Count('id')):
                    row = model_field.related_model.objects.get(id=choice[field_name])
                    display_name = cls.format_fk_display_name(model_field=row, user=user)
                    choices.append({"display_name": display_name,
                                    "value": choice[field_name],
                                    "count": choice["count"]})
            # 去重
            temp = dict()
            for choice in choices:
                value = choice['value']
                count = choice['count']
                if value in temp:
                    temp[value]['count'] += count
                else:
                    temp[value] = choice
            choices = list(temp.values())
            filter_map.update({field: choices})
        return filter_map

    @classmethod
    def get_checktool_rules_filter(cls, queryset, user=None):
        """获取工具规则的filter map
        :param queryset: CheckRule queryset
        :return: filter_map
        """
        field_maps = {
            field: base_filters.CheckRuleFilter.base_filters[field].field_name
            for field in base_filters.CheckRuleFilter.Meta.fields
        }
        return cls._get_filter(queryset, field_maps, models.CheckRule, user=user)
    
    @classmethod
    def get_checkpackage_rules_filter(cls, queryset, filter_class=base_filters.PackageMapFilter, user=None):
        """获取规则包规则的filter map
        :param queryset: CheckRule queryset
        :return: filter_map
        """
        field_maps = {
            field: filter_class.base_filters[field].field_name
            for field in filter_class.Meta.fields
        }
        return cls._get_filter(queryset, field_maps, models.PackageMap, user=user)
