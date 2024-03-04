# -*- coding: utf-8 -*-
#  Copyright (c) 2021-2024 THL A29 Limited
#  #
#  This source code file is made available under MIT License
#  See LICENSE for details
#  ==============================================================================


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codeproj', '0005_auto_20220608_2347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectteam',
            name='status',
            field=models.IntegerField(choices=[(1, '活跃'), (2, '禁用')], default=1, help_text='项目团队状态'),
        ),
    ]
