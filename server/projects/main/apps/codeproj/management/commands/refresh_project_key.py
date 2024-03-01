# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""刷新项目key值
"""
import logging

# 第三方
from django.core.management.base import BaseCommand

# 项目内
from apps.codeproj.models import Project

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "refresh project key"

    def handle(self, *args, **options):
        ps = Project.everything.filter(project_key__isnull=True)
        num = ps.count()
        project_list = []
        count = 0
        logger.info("Start refresh project num: %s" % num)
        for p in ps:
            count += 1
            p.scan_path = "/" if not p.scan_path else p.scan_path
            p.project_key = p.gen_project_key(p.repo_id, p.scan_scheme_id, p.branch, p.scan_path)
            project_list.append(p)
            if len(project_list) == 1000:
                logger.info("Refresh project num: %s/%s" % (count, num))
                Project.objects.bulk_update(project_list, ["scan_path", "project_key"])
                project_list = []
        if project_list:
            Project.objects.bulk_update(project_list, ["scan_path", "project_key"])
        logger.info("Finish refresh project num: %s/%s" % (count, num))
