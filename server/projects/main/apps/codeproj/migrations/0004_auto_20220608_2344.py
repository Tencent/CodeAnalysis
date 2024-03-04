# -*- coding: utf-8 -*-
#  Copyright (c) 2021-2024 THL A29 Limited
#  #
#  This source code file is made available under MIT License
#  See LICENSE for details
#  ==============================================================================


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codeproj', '0003_auto_20220518_1019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseproject',
            name='status',
            field=models.IntegerField(choices=[(1, '活跃'), (2, '失活'), (3, '归档中'), (4, '已归档')], default=1, verbose_name='项目状态'),
        ),
    ]
