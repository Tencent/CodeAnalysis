# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

'''
error number 定义
'''

# 成功
OK = 0

#: 节点端错误
# E_NODE = 200  # 2020-07-16 该错误类型不够明确,废弃

#: 任务执行错误
E_NODE_TASK = 201

#: 任务超时
E_NODE_TASK_EXPIRED = 202

#: 节点端SCM任务故障
E_NODE_TASK_SCM_FAILED = 203

#: 项目配置错误（通常指用户配置有误）
E_NODE_TASK_CONFIG = 204

#: 任务参数错误
E_NODE_TASK_PARAM = 205

#: 项目编译错误
E_NODE_TASK_BUILD = 210

#: 工具分析错误
E_NODE_TASK_ANALYZE = 211

#: 分析结果处理错误
E_NODE_TASK_DATAHANDLE = 212

#: Format错误
E_NODE_TASK_FORMAT = 213

#: Blame错误
E_NODE_TASK_BLAME = 214

#: Filter错误
E_NODE_TASK_FILTER = 215

#: 项目资源类错误
E_NODE_TASK_SOURCE = 216

#: 项目资源类错误
E_NODE_TASK_TRANSFER = 217

#: 与服务器通信的resfulapi错误
E_NODE_TASK_RESFULAPI = 218

#: 文件服务器传输错误
E_NODE_FILE_SERVER = 219

#: 节点配置错误（通常指客户端系统运行的配置有误）
E_NODE_CONFIG = 220

#: 压缩模块错误
E_NODE_ZIP = 221

#: 输入超时
E_NODE_Input_Timeout = 222

#: 输入超过重试次数
E_NODE_Input_Retry = 223

#: requests API 访问错误
E_NODE_REQUESTS_API = 224

#: 当前版本已经扫描过,无需扫描
E_NODE_SKIP_SCAN = 225

#: 自定义工具(第三方工具)执行异常
E_NODE_CUSTOM_TOOL = 226

#: 由于本次扫描的有一个任务失败,导致取消其他任务
E_NODE_TASK_CANCEL = 299
