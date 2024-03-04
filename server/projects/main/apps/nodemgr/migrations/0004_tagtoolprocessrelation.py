# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================


import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('scan_conf', '0005_checktool_image_url'),
        ('nodemgr', '0003_auto_20220615_2124'),
    ]

    operations = [
        migrations.CreateModel(
            name='TagToolProcessRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('checktool', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scan_conf.checktool',
                                                verbose_name='工具')),
                ('process', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scan_conf.process',
                                              verbose_name='进程')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nodemgr.exectag',
                                          verbose_name='标签')),
            ],
        ),
    ]
