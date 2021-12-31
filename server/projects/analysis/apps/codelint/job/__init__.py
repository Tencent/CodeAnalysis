# -*- coding: utf-8 -*-
"""
codelint - job
lint结果数据入库存储
"""

import logging

from .linthandler import LintResultHandler, LintResultSummaryHandler

logger = logging.getLogger(__name__)


def on_job_end(scan, task_results, **kwargs):
    """Lint结果入库
    """
    logger.info("[Project: %s][Scan: %s] 开始codelint入库..." % (scan.project_id, scan.id))
    task_result_num = len(task_results)
    logger.info("[Project: %s][Scan: %s] 共有%d个工具的结果需要入库" % (scan.project_id, scan.id, task_result_num))
    issue_detail_count = 0

    result_summary_handler = LintResultSummaryHandler(scan, task_results)
    current_time = result_summary_handler.get_current_time()
    if kwargs.get("reset") is True:
        logger.info("[Project: %s][Scan: %s] 当前扫描为重新存储入库，开始清理之前已存在的数据" % (scan.project_id, scan.id))
        result_summary_handler.reset_scan_result()
    result_summary_handler.start()

    for index, task_result in enumerate(task_results):
        logger.info("[Project: %s][Scan: %s][%d/%d] 开始入库工具%s的结果..." % (
            scan.project_id, scan.id, index + 1, task_result_num, task_result["name"]))
        result_handler = LintResultHandler(scan, task_result, current_time)
        result_handler.handle()
        issue_detail_count += result_handler.issue_detail_num
    result_summary_handler.after_saving_detail(issue_detail_count=issue_detail_count)
    result_summary_handler.finish()
    logger.info('[Project: %s][Scan: %s] 代码扫描结果入库完成！' % (scan.project_id, scan.id))
