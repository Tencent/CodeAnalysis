# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scan_conf', '0004_auto_20220905_2334'),
    ]

    operations = [
        migrations.AddField(
            model_name='checktool',
            name='image_url',
            field=models.CharField(blank=True, help_text='镜像地址', max_length=200, null=True),
        ),
    ]