# -*- coding: utf-8 -*-
#  Copyright (c) 2021-2024 THL A29 Limited
#  #
#  This source code file is made available under MIT License
#  See LICENSE for details
#  ==============================================================================


from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('codeproj', '0004_auto_20220608_2344'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='projectteam',
            managers=[
                ('active_pts', django.db.models.manager.Manager()),
            ],
        ),
    ]
