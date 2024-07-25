# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
历史数据清理脚本
用于清理已被删除且过期的历史数据，包括以下内容：
1、清除已经被软删除的project项目，及其关联的main库中的数据。
2、远程调用analysis服务，执行相关数据的软删除。

"""

import logging
from django.utils import timezone
from django.core.management.base import BaseCommand
from datetime import timedelta
from apps.codeproj import models
from util.webclients import AnalyseClient

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'clear deleted project'

    def add_arguments(self, parser):
        parser.add_argument('--expired_days', type=int, help='Set expired days', default=180)

    def handle(self, *args, **options):
        logger.info("执行历史数据清理功能")

        # 获取当前时间
        now = timezone.now()
        time = options['expired_days']
        if time < 0:
            logger.error("设置的天数不能为负数，请重新执行！")
            return

        # 过滤出 deleted_time 字段不为空且 time 字段与当前时间的差超过设定值的对象
        queryset = models.Project.everything.filter(
            deleted_time__lte=now - timedelta(days=time)
        )

        logger.info("正在清理main服务中已被删除且过期的历史数据......")
        for project in queryset:
            # 清除main服务中project的关联数据
            logger.info("清除项目id为 %d 的关联数据", project.id)
            AnalyseClient().api('delete_project', data=None, path_params=(project.id,))
            project.delete(permanent=True)

        # 在analysis服务中执行清理操作。
        logger.info(
            "数据清理完毕,共 %d 个项目，如需清理analysis服务中的相关数据，请到analysis服务中执行clear_analysis_data.py脚本！",
            queryset.count())
