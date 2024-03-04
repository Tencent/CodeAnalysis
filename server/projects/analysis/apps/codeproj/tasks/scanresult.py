# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - scan result tasks
"""

# python 原生import
import os
import json
import shutil
import logging
from datetime import datetime, timedelta

# 第三方 import
from django.conf import settings
from django.utils.timezone import now, get_default_timezone

# 项目内 import
from codedog.celery import celery_app
from apps.codeproj import models, core
from apps.codelint import models as lint_models
from apps.codelint import serializers as lint_serializers
from apps.codemetric import models as metric_models
from apps.codemetric import serializers as metric_serializers
from util import errcode
from util.webclients import MainClient

logger = logging.getLogger(__name__)


RESULT_INFO_LIST = [
    ("code_lint_info", lint_models.LintScan,
     lint_serializers.LintScanClosedSerializer),
    ("code_metric_cc_info", metric_models.CyclomaticComplexityScan,
     metric_serializers.CyclomaticComplexityScanClosedSerializer),
    ("code_metric_dup_info", metric_models.DuplicateScan,
     metric_serializers.DuplicateScanClosedSerializer),
    ("code_metric_cloc_info", metric_models.ClocScan,
     metric_serializers.ClocScanClosedSerializer),
]


@celery_app.task
def put_scan_result(project_id, scan_id, data):
    """保存数据结果，data为 ProjectScanPutResultsSerializer 的 validated_data
    """
    scanresult_ctl = core.ScanResultController(project_id, scan_id)
    scanresult_ctl.init_controller()
    scan_result_path = scanresult_ctl.save_scan_result(data)
    _scan_callback(scan_id, scan_result_path)


def _scan_callback(scan_id, scan_result_path=None, **kwargs):
    """回调上报任务结果
    """
    scan = models.Scan.objects.get(id=scan_id)
    logger.info("[Project: %s][Job: %d][Scan: %d] 入库结束，开始执行回调" % (scan.project_id, scan.job_gid, scan.id))
    result_data = {}
    for key, model, serializer in RESULT_INFO_LIST:
        instance = model.objects.filter(scan=scan).first()
        if not instance:
            continue
        slz = serializer(instance=instance)
        result_data.update({key: slz.data})
    data = {
        "result_code": scan.result_code,
        "result_msg": scan.result_msg,
        "result_data": result_data,
        "result_path": scan_result_path
    }
    logger.info("[Project: %s][Job: %d][Scan: %d] 回调参数如下：" % (scan.project_id, scan.job_gid, scan.id))
    logger.info(json.dumps(data, indent=4))
    rsp = MainClient().api("job_closed", data=data, path_params=(scan.project_id, scan.job_gid))
    logger.info("[Project: %s][Job: %d][Scan: %d] 入库结束，回调结束，结果如下" % (
        scan.project_id, scan.job_gid, scan.id))
    logger.info(rsp)


@celery_app.task
def clean_job_data():
    """清除jobdata目录下过期的文件夹
    """
    job_data_base = os.path.join(settings.BASE_DIR, "tempdata")
    if not os.path.exists(job_data_base):
        return
    job_dir_list = os.listdir(job_data_base)
    count = 0
    for job_dir in job_dir_list:
        full_job_dir = os.path.join(job_data_base, job_dir)
        dir_mtime = os.stat(full_job_dir).st_mtime
        if now() - datetime.fromtimestamp(dir_mtime, tz=get_default_timezone()) > settings.CLEAN_DIR_TIMEOUT:
            if os.path.isdir(full_job_dir):
                try:
                    shutil.rmtree(full_job_dir)
                except Exception as e:
                    logger.exception("Unexpected Exception when deleting [%s]:%s" % (full_job_dir, e))
                    pass
                else:
                    logger.info("Directory %s deleted." % full_job_dir)
                    count += 1
    logger.info("%d directories in %s(%d sub dirs) deleted." % (count, job_data_base, len(job_dir_list)))


@celery_app.task
def clean_expired_scan():
    """清除超时的scan
    """
    logger.info("start to clean expired scan records...")
    yesterday = now() - timedelta(days=1)
    scans = models.Scan.objects.filter(scan_time__lte=yesterday, state=models.Scan.StateEnum.CLOSING)
    for scan in scans:
        logger.info("[Project: %d][Scan: %d] scan timeout, scan_time=%s" % (
            scan.project_id, scan.id, scan.scan_time))
        models.Scan.objects.filter(id=scan.id, state=models.Scan.StateEnum.CLOSING).update(
            state=models.Scan.StateEnum.CLOSED, result_code=errcode.E_SERVER_SCAN_TIMEOUT
        )
        _scan_callback(scan)
    logger.info("finish cleaning expired scan records")
