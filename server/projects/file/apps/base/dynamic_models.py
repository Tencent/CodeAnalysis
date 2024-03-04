# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""动态表格
"""

import logging
from copy import copy

from django.db import models
from django.db import router
from django.db import connections
from django.db.utils import OperationalError


logger = logging.getLogger(__name__)


class ModelSchemaEditor:
    """根据model查看所属的db，并初始化对应的连接
    """
    @classmethod
    def get_connection_with_model(cls, model):
        """根据model获取DB连接
        """
        db = router.db_for_write(model)
        return connections[db]

    @classmethod
    def get_db_tables(cls, connection):
        """查看当前连接DB的表格
        """
        with connection.cursor() as cursor:
            return [table_info.name for table_info in connection.introspection.get_table_list(cursor)]

    @classmethod
    def check_table_exist(cls, model):
        """判断表格是否存在
        """
        db_table = model._meta.db_table
        curr_conn = cls.get_connection_with_model(model)
        if db_table not in cls.get_db_tables(curr_conn):
            return False
        else:
            return True

    @classmethod
    def create_table(cls, new_model):
        """创建表格
        """
        curr_conn = cls.get_connection_with_model(new_model)
        if not cls.check_table_exist(new_model):
            try:
                with curr_conn.schema_editor() as editor:
                    editor.create_model(new_model)
            except OperationalError as err:
                if err.args[0] == 1050:  # Table already exists
                    logger.warning("<model: %s> table has created" % new_model.__name__)
                    return
                raise

    @classmethod
    def drop_table(cls, model):
        """删除表格
        """
        curr_conn = cls.get_connection_with_model(model)
        try:
            with curr_conn.schema_editor() as editor:
                editor.delete_model(model)
        except OperationalError as err:
            if err.args[0] == 1051:  # Table not exist
                logger.warning("<model: %s> table has dropped" % model.__name__)
                return
            raise


class BaseShardMixin(object):
    """基础分表
    """
    cache = {}

    @classmethod
    def shard(cls, shard_key=None, options=None):
        """分表
        """

    @classmethod
    def create_model(cls, sharding, options=None):
        """动态创建model
        """
        if sharding:
            model_name = cls.__name__ + str(sharding)
            table_name = "%s_%s" % (cls._meta.db_table, str(sharding))
            if cls.cache.get(model_name):
                return cls.cache[model_name]

        else:
            model_name = cls.__name__
            table_name = cls._meta.db_table

        class Meta:
            db_table = table_name
            unique_together = cls._meta.unique_together
            index_together = cls._meta.index_together

        if options is not None:
            for key, value in options.iteritems():
                setattr(Meta, key, value)

        attrs = {
            '__module__': cls.__module__,
            'Meta': Meta,
        }

        # 动态添加外键
        remote_fields = []
        for field in cls._meta.fields:
            attrs[field.name] = copy(field)
            # copy foreign key, rename 'related_name'
            if isinstance(field, models.ForeignKey):
                remote_field = copy(field.remote_field)
                if remote_field.related_name != "+":
                    remote_field.related_name = '%s_%s' % (remote_field.related_name, sharding)
                remote_field.field = attrs[field.name]
                attrs[field.name].remote_field = remote_field
                remote_fields.append(remote_field)
        ModelClass = type(model_name, (cls,), attrs)
        for remote_field in remote_fields:
            remote_field.to = ModelClass
        cls.cache[model_name] = ModelClass
        return ModelClass


class AppShardMixin(BaseShardMixin):
    """App动态分表
    """

    DEFAULT_TABLE = ""

    @classmethod
    def shard(cls, app):
        """
        根据App动态分表
        """
        _db_table = "%s_%s" % (cls._meta.db_table, app)
        new_model = cls.create_model(app)
        ModelSchemaEditor.create_table(new_model)
        return new_model

    @classmethod
    def default_model(cls):
        """默认表格
        """
        default_model = cls.create_model(cls.DEFAULT_TABLE)
        ModelSchemaEditor.create_table(default_model)
        return default_model
