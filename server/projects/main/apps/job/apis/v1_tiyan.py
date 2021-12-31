# -*- coding: utf-8 -*-
"""Restful Api实现

V1 体验版
"""

# python 原生import
import logging

# 第三方 import
from rest_framework.renderers import JSONRenderer

# 项目内 import
from apps.job.apis import v1


logger = logging.getLogger(__name__)


class ProjectJobApiView(v1.ProjectJobApiView):
    """任务关闭接口
    使用对象：服务内部

    ### put
    应用场景：Job JobClosed 的回调
    """
    renderer_classes = [JSONRenderer]


class ProjectScanJobInitApiView(v1.ProjectScanJobInitApiView):
    """项目扫描初始化
    使用对象：节点

    ### GET
    应用场景：获取项目扫描配置的api，供节点端离线扫描使用

    ### POST
    应用场景：创建新的扫描任务，仅做初始化
    """
    renderer_classes = [JSONRenderer]


class ProjectJobFinishApiView(v1.ProjectJobFinishApiView):
    """项目本地扫描完成，上报结果
    使用对象：节点

    ### POST
    应用场景：上报本地扫描的任务结果
    """
    renderer_classes = [JSONRenderer]


class TaskProgressApiView(v1.TaskProgressApiView):
    """任务进程上报接口
    """
    renderer_classes = [JSONRenderer]


class TaskDetailApiView(v1.TaskDetailApiView):
    """
    put:
    上报task结果。结果格式：task_id, task_version, result_code, result_data, result_msg, log_url
    """
    renderer_classes = [JSONRenderer]


class JobApiView(v1.JobApiView):
    """
    get: 获取指定job的详情
    put: 修改job的字段内容
    """
    renderer_classes = [JSONRenderer]


class JobTasksBeatApiView(v1.JobTasksBeatApiView):
    """指定Task的心跳上报接口

    ### post
    应用场景：更新job下所有task的心跳时间
    """
    renderer_classes = [JSONRenderer]


class JobTasksApiView(v1.JobTasksApiView):
    """指定Job的task列表查询接口

    ### get
    应用场景：获取Job的Task列表
    """
    renderer_classes = [JSONRenderer]
