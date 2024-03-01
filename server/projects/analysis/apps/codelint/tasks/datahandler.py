# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codelint - datahandler task
异步任务
"""

import logging

from django.db import connection

from apps.codelint.models import PackageRuleMap
from codedog.celery import celery_app
from util.webclients import MainClient

logger = logging.getLogger(__name__)


@celery_app.task
def clean_deleted_issuedetail(project_id):
    """清理已软删除的Issue详情
    :param project_id: int，项目编号
    """

    logger.info("[Project: %s] clean deleted issuedetail start..." % project_id)
    deleted_num = 0
    try:
        while True:
            with connection.cursor() as cursor:
                rowcount = cursor.execute("DELETE FROM codelint_issuedetail WHERE project_id=%s and "
                                          "deleted_time IS NOT NULL LIMIT 5000;", (project_id,))
                if rowcount == 0:
                    break
                deleted_num += rowcount
        logger.info("[Project: %s] clean deleted issuedetail num: %s" % (project_id, deleted_num))

    except Exception as err:
        logger.error("[Project: %s] batch clean deleted issuedetail failed: %s" % (project_id, err))
        logger.exception(err)
    logger.info("[Project: %s] clean deleted issuedetail finish..." % project_id)


@celery_app.task
def sync_checkpackage_rule_map():
    """向Main服务查询指定规则包和规则编号数据，并同步到Analysis Server数据库
    """
    logger.info("[Sync Checkpackage Rule Map] start to sync checkpackage rule map...")

    package_rule_map = {}
    pkg_ids = PackageRuleMap.objects.all().values_list("checkpackage_gid", flat=True).distinct()
    logger.info("[Sync Checkpackage Rule Map] checkpackage num: %s" % pkg_ids.count())
    for pkg_id in pkg_ids:
        package_rule_ids = []
        if package_rule_map.get(pkg_id):
            logger.info("[Sync Checkpackage Rule Map][Package: %s] get rule ids from cache" % pkg_id)
            package_rule_ids = package_rule_map[pkg_id]
        else:
            logger.info("[Sync Checkpackage Rule Map][Package: %s] get rule ids from main server" % pkg_id)
            try:
                package_rule_ids = MainClient().api("get_package_rule_ids", path_params=(pkg_id,), data=None)
                package_rule_map[pkg_id] = package_rule_ids
            except Exception as err:
                logger.exception("[Sync Checkpackage Rule Map][Package: %s] get rule id failed, exception: %s" % (
                    pkg_id, err))
        if not package_rule_ids:
            continue

        map_objs = []
        for rule_id in package_rule_ids:
            map_objs.append(PackageRuleMap(checkpackage_gid=pkg_id, checkrule_gid=rule_id))

        PackageRuleMap.objects.bulk_create(map_objs, ignore_conflicts=True)
        delete_pkg_rule_map = PackageRuleMap.objects.filter(checkpackage_gid=pkg_id).exclude(
            checkrule_gid__in=package_rule_ids)
        logger.info("[Package: %s] delete checkpackage rule map: %s" % (pkg_id, delete_pkg_rule_map.count()))
        delete_pkg_rule_map.delete()
    logger.info("[Sync Checkpackage Rule Map] finish to sync checkpackage rule map!")
