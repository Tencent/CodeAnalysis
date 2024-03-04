# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================


from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('authen', '0003_auto_20220518_1019'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='organization',
            managers=[
                ('active_orgs', django.db.models.manager.Manager()),
            ],
        ),
    ]
