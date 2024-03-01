# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
error number 定义
"""

OK = 0
INCR_IGNORE = 1
CLIENT_REDIRECT = 2

# server端错误
E_SERVER = 100
E_SERVER_DB_CONN = 101
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

# 节点端错误
E_NODE = 200
E_NODE_TASK = 201
E_NODE_TASK_EXPIRED = 202
E_NODE_TASK_SCM_FAILED = 203
E_NODE_TASK_CONFIG = 204
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
E_NODE_TASK_CANCEL = 299

# 用户端错误
E_CLIENT = 300
E_CLIENT_CANCELED = 301
E_CLIENT_CONFIG_ERROR = 302
E_USER_CONFIG_BASIC_ERROR = 310  # 扫描方案配置错误
E_USER_CONFIG_LANG_ERROR = 311  # 扫描方案未配置语言
E_USER_CONFIG_NO_LINT_OR_METRIC = 312  # 扫描方案未启用代码扫描或代码度量
E_USER_CONFIG_NODE_ERROR = 313  # 扫描方案配置的标签或关联节点失效
E_USER_CONFIG_CODELINT_ERROR = 320  # 扫描方案代码扫描配置错误
E_USER_CONFIG_CODELINT_PKG_ERROR = 321  # 扫描方案的代码扫描未配置规则
E_USER_CONFIG_CODEMETRIC_ERROR = 330  # 扫描方案的代码度量未配置错误
E_USER_CONFIG_NO_OAUTH = 340  # 当前用户未OAuth授权

# E_SERVER请求错误
E_SERVER_BASE = 1000  # server端错误

E_SERVER_INVITE_CODE = 1010  # 邀请码错误
E_SERVER_INVITE_CODE_EXPIRED = 1011  # 邀请码过期

E_SERVER_PROJECT_TEAM_CREATE = 1020  # 项目组创建失败
E_SERVER_PROJECT_TEAM_EXIST = 1021  # 项目组已存在
E_SERVER_PROJECT_TEAM_CREATE_OUT_LIMIT = 1022  # 项目组创建超出限制
E_SERVER_PROJECT_TEAM_UPDATE = 1023  # 项目组更新失败

E_SERVER_LABEL_CREATE = 1030  # 标签创建失败
E_SERVER_LABEL_EXIST = 1031  # 标签已存在
E_SERVER_LABEL_CYCLE_REF = 1032  # 标签循环引用，父标签不可为自己

E_SERVER_REPOSITORY_CREATE = 1040  # 代码库创建失败
E_SERVER_REPOSITORY_EXIST = 1041  # 代码库已存在
E_SERVER_REPOSITORY_CREATE_OUT_LIMIT = 1042  # 代码库创建超出限制
E_SERVER_REPOSITORY_UPDATE = 1043  # 代码库更新失败
E_SERVER_CHECKER_PARAMS_CONFIG = 1050  # 任务参数配置更新异常
E_SERVER_ORGANIZATION_CREATE = 1060  # 团队创建失败
E_SERVER_ORGANIZATION_EXIST = 1061  # 团队已存在
E_SERVER_ORGANIZATION_CREATE_OUT_LIMIT = 1062  # 团队创建超出限制

E_SERVER_DRAG_TYPE_NOT_EXIST = 1070  # 排序类型不存在
E_SERVER_CHECKTOOL_LIB_EXIST = 1080  # 工具依赖已存在

E_SERVER_PROJECT = 1100
E_SERVER_PROJECT_CREATE = 1101

E_SERVER_SCAN = 1200
E_SERVER_SCAN_CREATE = 1201

E_SERVER_NODE = 1300
E_SERVER_NODE_REGISTER = 1301

E_SERVER_CONF = 1400  # 扫描配置异常
E_SERVER_CONF_TOOL_NOT_EXIST = 1401  # 扫描工具不存在异常

E_SERVER_TCMETRIC_SCAN = 1500  # TCMetric扫描异常
E_SERVER_TCMETRIC_SCAN_RERUN = 1501  # TCMetric扫描重启异常
E_SERVER_TCMETRIC_REPORT = 1550  # TCMetric扫描报告异常
E_SERVER_TCMETRIC_REPORT_NOT_EXIST = 1551  # TCMetric扫描报告不存在
E_SERVER_TCMETRIC_REPORT_CREATE = 1552  # TCMetric扫描报告创建失败

# UNKNOWN
UNKNOWN = -1

UNKNOWNRESULT = {
    "errno": UNKNOWN,
    "msg": ""
}

_OK_CHOICE = (
    (OK, "成功"),
    (INCR_IGNORE, "无需扫描"),
    (CLIENT_REDIRECT, "重定向到其他任务"),
)

OK_DICT = dict(_OK_CHOICE)

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

SERVER_ERROR_DICT = dict(_SERVER_ERROR_CHOICE)

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
    (E_NODE_JOB_BEAT_ERROR, "本地分析任务被中断"),
    (E_NODE_TASK_CANCEL, "其他task失败取消"),
)

NODE_ERROR_DICT = dict(_NODE_ERROR_CHOICE)

_CLIENT_ERROR_CHOICE = (
    (E_CLIENT, "用户取消或配置错误"),
    (E_CLIENT_CANCELED, "用户取消"),
    (E_CLIENT_CONFIG_ERROR, "配置错误"),
    (E_USER_CONFIG_BASIC_ERROR, "扫描方案配置错误"),
    (E_USER_CONFIG_LANG_ERROR, "扫描方案未配置语言"),
    (E_USER_CONFIG_NO_LINT_OR_METRIC, "扫描方案未启用代码扫描或代码度量"),
    (E_USER_CONFIG_NODE_ERROR, "扫描方案配置的标签或关联节点失效"),
    (E_USER_CONFIG_CODELINT_ERROR, "扫描方案的代码扫描配置错误"),
    (E_USER_CONFIG_CODELINT_PKG_ERROR, "扫描方案未配置扫描规则"),
    (E_USER_CONFIG_CODEMETRIC_ERROR, "扫描方案的代码度量配置错误"),
)

CLIENT_ERROR_DICT = dict(_CLIENT_ERROR_CHOICE)

EXCEPTION_TYPE = {
    "成功": [OK, INCR_IGNORE, CLIENT_REDIRECT],
    "平台服务异常": [E_SERVER],
    "基础文件服务异常": [E_SERVER_FILE_SERVICE_ERROR, E_NODE_FILE_SERVER],
    "客户端未明确异常": [E_NODE],
    "任务执行时异常": [E_NODE_TASK_DATAHANDLE, E_NODE_TASK_FORMAT, E_NODE_TASK_FILTER, E_NODE_TASK_ANALYZE],
    "任务执行超时": [E_NODE_TASK_EXPIRED],
    "SCM 异常": [E_NODE_TASK_SCM_FAILED],
    "工具编译时异常": [E_NODE_TASK_BUILD],
    "代码仓库Blame异常": [E_NODE_TASK_BLAME],
    "本地代码变更时资源异常": [E_NODE_TASK_SOURCE],
    "中间文件传输时资源异常": [E_NODE_TASK_TRANSFER],
    "API 请求异常": [E_NODE_TASK_RESFULAPI, E_NODE_REQUESTS_API],
    "客户端压缩异常": [E_NODE_ZIP],
    "任务取消或配置异常": [E_CLIENT, E_CLIENT_CANCELED, E_CLIENT_CONFIG_ERROR, E_NODE_TASK_PARAM, E_NODE_TASK_CONFIG,
                  E_NODE_JOB_BEAT_ERROR, E_USER_CONFIG_BASIC_ERROR, E_USER_CONFIG_LANG_ERROR,
                  E_USER_CONFIG_NO_LINT_OR_METRIC, E_USER_CONFIG_NODE_ERROR, E_USER_CONFIG_CODELINT_ERROR,
                  E_USER_CONFIG_CODELINT_PKG_ERROR, E_USER_CONFIG_CODEMETRIC_ERROR],
    "第三方工具执行异常": [E_NODE_TASK, E_NODE_LOCAL_SCAN],
}

SUCCESS_TYPE_KEY = "成功"

PLATFORM_TYPE_KEYS = ["API 请求异常", "客户端未明确异常", "平台服务异常", "任务执行时异常"]


def _get_display_name(choice, code):
    for (result_code, msg) in choice:
        if code == result_code:
            return msg
    return None


def interpret_code(code):
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


def is_scm_error(code):
    """
    判断错误码是否属于scm错误的范围
    """
    if 111 <= code <= 115:
        return True
    else:
        return False


def get_platform_type():
    """获取平台类型分类，包含平台、成功
    """
    codes = []
    platform_type_keys = ["成功", "中间文件传输时资源异常", "API 请求异常", "客户端未明确异常",
                          "客户端压缩异常", "平台服务异常", "任务执行时异常"]
    for key in EXCEPTION_TYPE:
        if key in platform_type_keys:
            codes.extend(EXCEPTION_TYPE[key])
    return codes
