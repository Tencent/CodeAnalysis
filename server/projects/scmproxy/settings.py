# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""ScmProxyServer 配置文件
"""

import os
from os.path import abspath, dirname, join

# RPC Server 地址和端口号
HOST = os.environ.get("SCMPROXY_HOST", "0.0.0.0")
PORT = int(os.environ.get("SCMPROXY_PORT", 80))

# 磁盘允许的最小空间
MIN_REMAIN_SIZE = int(os.environ.get("SCMPROXY_MIN_REMAIN_SIZE", 20 * 1 << 30))  # 20G, << 符号比 * 优先级高

# 源码目录保留时间
SOURCE_RETAIN_TIME = int(os.environ.get("SCMPROXY_SOURCE_RETAIN_TIME", 14 * 24 * 60 * 60))

# 源码目录保留时间
TEMPFILE_RETAIN_TIME = int(os.environ.get("SCMPROXY_TEMPFILE_RETAIN_TIME", 1 * 24 * 60 * 60))

# 项目根路径
BASE_DIR = dirname(abspath(__file__))

# 源码存放路径
SOURCE_DIR = join(BASE_DIR, "sourcedirs")

# 日志默认存放目录
LOG_DIR = join(BASE_DIR, 'logs')

# 临时目录
TEMP_DIR = join(BASE_DIR, ".proxy_temp")

# 代理配置
PROXY_ENVS = {
    "GIT_SSL_NO_VERIFY": '1'  # Git不检查HTTPS证书
}

# Sentry
SENTRY_URL = os.environ.get("SCMPROXY_SENTRY_URL", "")
