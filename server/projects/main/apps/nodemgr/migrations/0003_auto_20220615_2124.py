# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

import apps.base.basemodel
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('nodemgr', '0002_nodestatus_nodetoolprocessrelation'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='exectag',
            managers=[
                ('everything', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddField(
            model_name='exectag',
            name='created_time',
            field=models.DateTimeField(db_index=True, default=apps.base.basemodel.utcnow, verbose_name='创建时间'),
        ),
        migrations.AddField(
            model_name='exectag',
            name='creator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='创建人'),
        ),
        migrations.AddField(
            model_name='exectag',
            name='deleted_time',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='删除时间'),
        ),
        migrations.AddField(
            model_name='exectag',
            name='deleter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='删除人'),
        ),
        migrations.AddField(
            model_name='exectag',
            name='display_name',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='标签展示名称'),
        ),
        migrations.AddField(
            model_name='exectag',
            name='modified_time',
            field=models.DateTimeField(db_index=True, default=apps.base.basemodel.utcnow, verbose_name='最近修改时间'),
        ),
        migrations.AddField(
            model_name='exectag',
            name='modifier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='最近修改人'),
        ),
        migrations.AddField(
            model_name='exectag',
            name='org_sid',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='组织编号'),
        ),
        migrations.AddField(
            model_name='node',
            name='org_sid',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='组织编号'),
        ),
        migrations.AddField(
            model_name='node',
            name='related_managers',
            field=models.ManyToManyField(blank=True, related_name='related_managers', to=settings.AUTH_USER_MODEL, verbose_name='节点关注人员列表'),
        ),
    ]
