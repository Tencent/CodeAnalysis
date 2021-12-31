# -*- coding:utf-8 -*-
"""
Code Metric Result Data saving
"""
import logging

from .cchandler import CCResultHandler
from .duphandler import DupResultHandler
from .codecounthandler import CodeCountResultHandler
from .utils import download_and_load_json_file


logger = logging.getLogger(__name__)


CODEMETRIC_RESULT_HADNLER_DICT = {
    "lizard": CCResultHandler,
    "cpd": DupResultHandler,
    "codecount": CodeCountResultHandler
}


def on_job_end(scan, task_results, **kwargs):
    """task_results的格式如下:
        具体参见 apps.codeproj.serializers._ScanTaskSerializer 中的定义
        ［
            ｛
                module = serializers.CharField(max_length=32, help_text="任务所属模块")
                name = serializers.CharField(max_length=32, help_text="任务所属模块")
                execute_version = serializers.CharField(max_length=56, help_text="任务的执行版本")
                params_url = serializers.URLField(help_text="参数路径")
                result_code = serializers.IntegerField(help_text="结果码")
                result_msg = serializers.CharField(help_text="结果信息", allow_blank=True, allow_null=True)
                result_data_url = serializers.URLField(help_text="结果路径", allow_blank=True, allow_null=True)
                log_url = serializers.URLField(help_text="日志链接")
            },
            ...
        ]
    """
    logger.info("[CodeMetric][Project: %s][Scan: %s] start saving result, task num: %s" % (
        scan.project_id, scan.id, len(task_results)))
    for task_result in task_results:
        logger.info("[CodeMetric][Project: %s][Scan: %s][Tool: %s] saving result..." % (
            scan.project_id, scan.id, task_result["name"]))
        if not CODEMETRIC_RESULT_HADNLER_DICT.get(task_result["name"]):
            logger.error("[CodeMetric][Project: %s][Scan: %s][Tool: %s] not support tool result" % (
                scan.project_id, scan.id, task_result["name"]))
            continue
        CODEMETRIC_RESULT_HADNLER_DICT[task_result["name"]](scan, task_result).handle(**kwargs)
