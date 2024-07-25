# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
历史数据清理脚本
用于清理已被删除且过期的历史数据，包括以下内容：
1、分批次清理数据量较大的表。
2、剩余少量数据进行关联删除。
3、清理scan、project。

"""

import logging
from django.core.management.base import BaseCommand
from django.db import connection
from apps.codeproj import models as codeprojmodels
from apps.codemetric import models as codemetricmodels
from apps.codelint import models as codelinmodels
from time import sleep

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'clear analysis data'

    def add_arguments(self, parser):
        parser.add_argument('--batch', type=int, help='Set batch size', default=1000)
        parser.add_argument('--sleeptime', type=int, help='Set sleep time/s', default=1)

    def handle(self, *args, **options):
        logger.info("执行历史数据清理功能")
        # 获取每一批次删除数据的条数，及批量删除间隔的休眠时间
        batch = options['batch']
        sleeptime = options['sleeptime']

        # 过滤出 deleted_time 字段不为空的对象
        projectSet = codeprojmodels.Project.everything.filter(
            deleted_time__isnull=False
        )
        # (1) 先删除和project关联且数据量大的表，不包括scan和project本身
        for project in projectSet:
            # 分层次进行删除
            # 1、codemetric_duplicateblock 表  对应DuplicateBlock 类
            self.clearDataByModel(codemetricmodels.DuplicateBlock._meta.db_table, batch, project.id, sleeptime)

            # 2、codemetric_duplicatefile 表  对应  DuplicateFile 类
            self.clearDataByModel(codemetricmodels.DuplicateFile._meta.db_table, batch, project.id, sleeptime)

            # 3、codemetric_duplicateissue  表  对应 DuplicateIssue 类
            self.clearDataByModel(codemetricmodels.DuplicateIssue._meta.db_table, batch, project.id, sleeptime)

            # 4、codemetric_clocfile 表  对应 ClocFile 类
            self.clearDataByModel(codemetricmodels.ClocFile._meta.db_table, batch, project.id, sleeptime)

            # 5、codemetric_clocdir 表  对应 ClocDir 类
            self.clearDataByModel(codemetricmodels.ClocDir._meta.db_table, batch, project.id, sleeptime)

            # 6、codelint_issuedetail 表 对应 IssueDetail 类
            self.clearDataByModel(codelinmodels.IssueDetail._meta.db_table, batch, project.id, sleeptime)

            # 7、codelint_issue 表  对应  Issue 类
            self.clearDataByModel(codelinmodels.Issue._meta.db_table, batch, project.id, sleeptime)

            # 8、codemetric_cyclomaticcomplexity 表 对应 CyclomaticComplexity 类
            self.clearDataByModel(codemetricmodels.CyclomaticComplexity._meta.db_table, batch, project.id, sleeptime)

        # (2) 删除 scan和project 及其关联的剩余少量数据
        # codeproj_project 通过id获取
        for project in projectSet:
            project.delete(permanent=True)

        logger.info("过期历史数据全部删除完毕！")

    def clearDataByModel(self, table, batch, id, sleeptime):
        cursor = connection.cursor()

        # 统计要删除的数据条数
        countquery = f"select count(project_id) from {table} where project_id = {id}"
        countparams = []
        cursor.execute(countquery, countparams)
        count = cursor.fetchone()[0]
        cur = 0

        logger.info("开始删除project id为 %d 关联的 %s 表数据共 %d 条", id, table, count)
        query = f"delete from {table} where project_id = {id} limit {batch}"
        params = []
        while cur < count:
            cursor.execute(query, params)
            cur += cursor.rowcount
            logger.info("数据正在进行删除 %d/%d", cur, count)
            sleep(sleeptime)
        logger.info("当前部分数据删除完毕！")

        # 关闭游标和连接
        cursor.close()
