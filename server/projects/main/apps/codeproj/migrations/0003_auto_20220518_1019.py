# -*- coding: utf-8 -*-
#  Copyright (c) 2021-2024 THL A29 Limited
#  #
#  This source code file is made available under MIT License
#  See LICENSE for details
#  ==============================================================================


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codeproj', '0002_scanschemetemplate_need_compile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basescanscheme',
            name='scheme_key',
            field=models.CharField(blank=True, db_index=True, max_length=64, null=True, verbose_name='扫描方案key值'),
        ),
    ]
