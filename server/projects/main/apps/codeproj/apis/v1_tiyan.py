# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - v1 apis for tiyan
"""

# 第三方 import

from rest_framework.renderers import JSONRenderer

# 项目内 import
from apps.codeproj.apis import v1


class ScanDirListApiView(v1.ScanDirListApiView):
    """扫描目录列表接口
    使用对象：节点

    ### GET
    应用场景：获取扫描目录列表
    >参数：无

    ### POST
    应用场景：新增扫描目录列表
    >参数：
    >> project: 项目id，需要与url中的project id一致

    >> dir_path: 目录，格式参考python fnmatch语法

    >> scan_type: 1表示包含（include），2表示过滤（exclude）
    """
    renderer_classes = [JSONRenderer]


class ProjectConfApiView(v1.ProjectConfApiView):
    """项目扫描配置接口
    使用对象：节点

    ### Get
    应用场景：获取项目的代码功能配置
    """
    renderer_classes = [JSONRenderer]


class ProjectScanJobConfApiView(v1.ProjectScanJobConfApiView):
    """获取项目扫描配置
    使用对象：节点

    ### GET
    应用场景：获取项目扫描配置的api，供节点端离线扫描使用

    ### POST
    应用场景：创建新的扫描任务
    参数：
    ```json
    {
        "tasks": [
            {
                "task_version": "1.0",
                "module_name": "codelint",
                "tag": "test",
                "processes": ["analyse","build","handledata"],
                "task_name": "pylint",
                "task_params": {
                    "scan_languages": [
                        "js"
                    ],
                    "scm_last_revision": "123"
                },
                "result_code": 0,
                "result_msg": 1,
                "result_data_url": "http://your-result-data-path",
                "log_url": "http://your-log-path",
                "finished_processes": ["build","analyse"],
                "private_processes": ["handledata"],
                "progress_rate": 90
            }
        ],
        "job_context": {
            "scm_revision": "346688",
            "scan_type": 1,
            "scm_url": "http://local-project-scm-host/local/scm/path",
            "scm_type": "svn",
            "project_id": 1,
            "incr_scan": true,
            "code_line_num": 12,
            "comment_line_num": 12,
            "blank_line_num": 12,
            "total_line_num": 12,
            "start_time": "2019-10-10 01:01:01",
            "time_format": "%Y-%m-%d %H:%M:%S",
            "created_from": "api",
        }
    }
    ```
    job_context中scm_revision, scm_url, scan_type为必填。

    scan_type: 扫描类型,仅作扫描标识处理.**1增量扫描，2全量扫描，3合流任务
    """
    renderer_classes = [JSONRenderer]


class ProjectScanDetailApiView(v1.ProjectScanDetailApiView):
    """项目指定扫描详情接口
    使用对象：节点

    ### Get
    应用场景：获取扫描结果
    """
    renderer_classes = [JSONRenderer]


class ProjectScanSchemeDefaultScanPathListApiView(v1.ProjectScanSchemeDefaultScanPathListApiView):
    """
    使用对象：节点

    ### Get
    应用场景：获取项目的默认过滤路径配置
    """
    renderer_classes = [JSONRenderer]
