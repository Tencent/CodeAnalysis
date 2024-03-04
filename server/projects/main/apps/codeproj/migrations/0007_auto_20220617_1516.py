# -*- coding: utf-8 -*-
#  Copyright (c) 2021-2024 THL A29 Limited
#  #
#  This source code file is made available under MIT License
#  See LICENSE for details
#  ==============================================================================


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codeproj', '0006_auto_20220615_2124'),
    ]

    operations = [
        migrations.AddField(
            model_name='basescanscheme',
            name='ignore_branch_issue',
            field=models.CharField(blank=True, help_text='过滤参考分支引入的问题', max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='basescanscheme',
            name='ignore_merged_issue',
            field=models.BooleanField(default=False, verbose_name='过滤其他分支合入的问题'),
        ),
        migrations.AddField(
            model_name='basescanscheme',
            name='ignore_submodule_clone',
            field=models.BooleanField(default=False, verbose_name='是否忽略子模块clone，默认为False（不忽略）'),
        ),
        migrations.AddField(
            model_name='basescanscheme',
            name='ignore_submodule_issue',
            field=models.BooleanField(default=True, verbose_name='是否忽略子模块问题，默认为True（忽略）'),
        ),
        migrations.AddField(
            model_name='basescanscheme',
            name='lfs_flag',
            field=models.BooleanField(blank=True, default=True, null=True, verbose_name='是否开启拉取代码时默认拉取lfs文件，默认为True（开启）'),
        ),
    ]
