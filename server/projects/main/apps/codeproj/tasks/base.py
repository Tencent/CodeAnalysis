# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - base tasks
"""
# 原生 import
import logging
from datetime import datetime

# 第三方 import
from croniter import croniter
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone

# 项目内 import
from apps.codeproj import core, models
from apps.codeproj.core import ScanSchemeManager
from apps.job.models import Job
from codedog.celery import celery_app
from util import errcode
from util.operationrecord import OperationRecordHandler
from util.webclients import AnalyseClient

logger = logging.getLogger(__name__)


def _now():
    now = timezone.make_aware(datetime.now(), timezone.get_current_timezone())
    return now


@celery_app.task
def sync_pkg_rule_map():
    """启动AnalysisServer规则包与规则关系同步任务
    """
    logger.info("Start to drop expired table")
    result = AnalyseClient().api("sync_pkg_rule_map", data=None)
    logger.info("drop expired table result: %s" % result)


@celery_app.task
def check_project_active():
    """检查项目是否运行正常

    1. 检查项目近一个月是否有启动扫描，如果没有则标记并发送邮件通知给分支项目创建同学
    2. 检查定时项目近10次扫描是否存在SCM相关异常，如果有，则关闭定时任务
    """
    logger.info("开始检查项目是否运行正常")
    logger.info("1. 开始检查项目近一个月是否有启动扫描")
    projects = models.Project.objects.filter(status=models.Project.StatusEnum.ACTIVE)
    codedog_user, created = User.objects.get_or_create(username=settings.DEFAULT_USERNAME)
    current_time = _now()
    for project in projects:
        # 长期未成功执行扫描
        last_success_job = Job.objects.filter(project=project).order_by("-create_time").first()
        last_active_time = last_success_job.create_time if last_success_job else project.created_time
        if current_time - last_active_time > settings.PROJECT_DISACTIVE_TIMEOUT:
            logger.info("[Project: %d][Creator: %s] 项目失活，代码库地址: %s，上一次活跃时间为: %s" % (
                project.id, project.creator, project.scm_url, last_active_time))
            models.Project.objects.filter(id=project.id).update(
                status=models.Project.StatusEnum.DISACTIVE, modifier=codedog_user, modified_time=current_time)
            OperationRecordHandler.add_project_operation_record(
                project, "项目失活", codedog_user, message="项目于%s自动标记为失活" % current_time
            )
    logger.info("2. 开始检查开启定时扫描的项目近10次扫描是否存在SCM相关异常")
    project_schedules = models.ScanSchedule.objects.filter(
        enabled=True,
        project__status=models.Project.StatusEnum.ACTIVE,
        project__scan_scheme__status=models.ScanScheme.StatusEnum.ACTIVE
    ).exclude(scan_sched=None)

    for project_sched in project_schedules:
        project = project_sched.project
        result_codes = Job.objects.filter(project=project).order_by(
            "-create_time").values_list("result_code", flat=True)[:10]
        result_codes = list(set(result_codes))
        if len(result_codes) == 1 and errcode.is_scm_error(result_codes[0]):
            msg = "项目近10次扫描错误码均为%s，关闭定时扫描任务" % result_codes[0]
            logger.warning("[Project: %s] %s" % (project.id, msg))
            OperationRecordHandler.add_project_operation_record(
                project, "项目更新配置", codedog_user, message=msg
            )
            project_sched.enabled = False
            project_sched.save()


@celery_app.task
def push_scanscheme_template(scheme_ids, ref_scheme_id, username, **kwargs):
    """推送扫描方案模板到相关子方案
    """
    user, _ = User.objects.get_or_create(username=username)
    ref_scheme = models.ScanScheme.objects.get(id=ref_scheme_id)
    op_message = ScanSchemeManager.get_sync_message(ref_scheme, **kwargs)
    scan_scheme_message = []
    for scheme_id in scheme_ids:
        scan_scheme = models.ScanScheme.objects.get(id=scheme_id)
        ScanSchemeManager.sync_with_ref_scheme(scan_scheme=scan_scheme,
                                               ref_scheme=ref_scheme,
                                               user=user,
                                               **kwargs)
        OperationRecordHandler.add_scanscheme_operation_record(scan_scheme, "方案模板同步", username, op_message)
        scan_scheme_message.append("%s" % scan_scheme)
    ref_scheme_message = "%s，同步扫描方案：%s" % (op_message, "、".join(scan_scheme_message))
    OperationRecordHandler.add_scanscheme_operation_record(ref_scheme, "方案模板同步", username, ref_scheme_message)


@celery_app.task
def handle_scheduled_projects():
    """根据project的配置定时创建扫描
    筛选范围：
    1. 配置了定时任务
    2. 项目为活跃状态
    3. 扫描方案为活跃状态
    """
    # Todo
