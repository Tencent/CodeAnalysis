# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
util - error code enum
"""

OK = 0
CLIENT_REDIRECT = 2

#: server端错误
E_SERVER = 100
E_SERVER_DB_CONN = 101
E_SERVER_CLS_CONN = 102
E_SERVER_SCM = 110
E_SERVER_SCM_AUTH_ERROR = 111
E_SERVER_SCM_NOT_FOUND = 112
E_SERVER_SCM_UNTRUSTED_SERVER = 113
E_SERVER_SCM_FORBIDDEN_ACCESS = 114
E_SERVER_SCM_PARAMS_ERROR = 115
E_SERVER_FILE_SERVICE_ERROR = 116
E_SERVER_JOB_CREATE_ERROR = 120
E_SERVER_JOB_INIT_ERROR = 121
E_SERVER_JOB_MIGRATE_ERROR = 122
E_SERVER_SCAN_TIMEOUT = 199

#: 节点端错误
E_NODE = 200
E_NODE_TASK = 201  # 任务执行错误
E_NODE_TASK_EXPIRED = 202  # 任务超时
E_NODE_TASK_SCM_FAILED = 203
E_NODE_TASK_CONFIG = 204  # 项目配置错误
E_NODE_TASK_PARAM = 205
E_NODE_TASK_BUILD = 210
E_NODE_TASK_ANALYZE = 211
E_NODE_TASK_DATAHANDLE = 212
E_NODE_TASK_FORMAT = 213
E_NODE_TASK_BLAME = 214
E_NODE_TASK_FILTER = 215
E_NODE_TASK_SOURCE = 216
E_NODE_TASK_TRANSFER = 217
E_NODE_TASK_RESFULAPI = 218
E_NODE_FILE_SERVER = 219
E_NODE_ZIP = 221
E_NODE_INPUT_TIMEOUT = 222
E_NODE_INPUT_RETRY = 223
E_NODE_REQUESTS_API = 224
E_NODE_SKIP_SCAN = 225
E_NODE_LOCAL_SCAN = 226
E_NODE_JOB_TIMEOUT = 297
E_NODE_JOB_BEAT_ERROR = 298
E_NODE_TASK_CANCEL = 299  # 其他task失败取消

# ： 用户端错误
E_CLIENT = 300
E_CLIENT_CANCELED = 301
E_CLIENT_CONFIG_ERROR = 302
# E_CLIENT_REDIRECT = 303

# UNKNOWN
UNKNOWN = -1

UNKNOWNRESULT = {
    "errno": UNKNOWN,
    "msg": ""
}

_OK_CHOICE = (
    (OK, "成功"),
    (CLIENT_REDIRECT, "重定向到其他任务"),
)

_SERVER_ERROR_CHOICE = (
    (E_SERVER, "服务异常"),
    (E_SERVER_SCM, "SCM服务异常"),
    (E_SERVER_SCM_AUTH_ERROR, "SCM鉴权失败"),
    (E_SERVER_SCM_NOT_FOUND, "SCM信息不存在"),
    (E_SERVER_SCM_UNTRUSTED_SERVER, "SCM不被信任"),
    (E_SERVER_SCM_FORBIDDEN_ACCESS, "SCM无权限"),
    (E_SERVER_SCM_PARAMS_ERROR, "SCM参数错误"),
    (E_SERVER_FILE_SERVICE_ERROR, "第三方依赖文件服务器异常"),
    (E_SERVER_JOB_CREATE_ERROR, "任务创建异常"),
    (E_SERVER_JOB_INIT_ERROR, "任务初始化异常"),
    (E_SERVER_JOB_MIGRATE_ERROR, "任务迁移导致异常")
)

_NODE_ERROR_CHOICE = (
    (E_NODE, "节点未知异常"),
    (E_NODE_TASK, "任务执行异常"),
    (E_NODE_TASK_EXPIRED, "任务执行超时"),
    (E_NODE_TASK_SCM_FAILED, "节点端SCM任务故障"),
    (E_NODE_TASK_CONFIG, "配置错误"),
    (E_NODE_TASK_PARAM, "任务参数错误"),
    (E_NODE_TASK_BUILD, "编译失败"),
    (E_NODE_TASK_ANALYZE, "工具分析错误"),
    (E_NODE_TASK_DATAHANDLE, "分析结果处理错误"),
    (E_NODE_TASK_FORMAT, "任务Format错误"),
    (E_NODE_TASK_BLAME, "任务Blame错误"),
    (E_NODE_TASK_FILTER, "任务Filter错误"),
    (E_NODE_TASK_SOURCE, "项目资源类错误"),
    (E_NODE_TASK_TRANSFER, "项目资源类错误"),
    (E_NODE_TASK_RESFULAPI, "节点端与服务器通信错误"),
    (E_NODE_FILE_SERVER, "文件服务器传输错误"),
    (E_NODE_ZIP, "节点端压缩模块错误"),
    (E_NODE_INPUT_TIMEOUT, "节点端输入超时"),
    (E_NODE_INPUT_RETRY, "节点端输入超过重试次数"),
    (E_NODE_REQUESTS_API, "节点端请求错误"),
    (E_NODE_SKIP_SCAN, "当前版本已经扫描过，无需扫描"),
    (E_NODE_LOCAL_SCAN, "节点端本地扫描错误"),
    (E_NODE_JOB_TIMEOUT, "节点端任务执行超时"),
    (E_NODE_JOB_BEAT_ERROR, "节点端任务心跳上报错误"),
    (E_NODE_TASK_CANCEL, "其他task失败取消"),
)

_CLIENT_ERROR_CHOICE = (
    (E_CLIENT, "用户取消或配置错误"),
    (E_CLIENT_CANCELED, "用户取消"),
    (E_CLIENT_CONFIG_ERROR, "配置错误"),
)


def _get_display_name(choice, code):
    for (result_code, msg) in choice:
        if code == result_code:
            return msg
    return None


def interpret_code(code):
    """展示错误码文本
    """
    if code is None:
        return None
    code = int(code)
    if 0 <= code < 100:
        return _get_display_name(_OK_CHOICE, code) or "成功"
    elif 100 <= code < 200:
        return _get_display_name(_SERVER_ERROR_CHOICE, code) or "未知服务异常"
    elif 200 <= code < 300:
        return _get_display_name(_NODE_ERROR_CHOICE, code) or "未知节点异常"
    elif 300 <= code < 400:
        return _get_display_name(_CLIENT_ERROR_CHOICE, code) or "未知使用异常"
    else:
        return "未知异常"


def is_success(code):
    """
    判断错误码是否属于成功的范围
    """
    if 0 <= code < 100:
        return True
    else:
        return False


def is_server_error(code):
    """
    判断错误码是否属于服务端错误的范围
    """
    if 100 <= code < 200:
        return True
    else:
        return False


def is_node_error(code):
    """
    判断错误码是否属于节点端错误的范围
    """
    if 200 <= code < 300:
        return True
    else:
        return False


def is_client_error(code):
    """
    判断错误码是否属于用户端错误的范围
    """
    if 300 <= code < 400:
        return True
    else:
        return False


def is_client_redirect(code):
    """
    判断错误码是否属于重定向类型
    """
    if code == CLIENT_REDIRECT:
        return True
    else:
        return False
