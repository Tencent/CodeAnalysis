# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
服务: AnalysisServer
"""
import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

from codedog.settings.open_base import *

# -*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-*-*-
# -*-*-*-*-*-*-*-*-*-*-*-     工程配置     -*-*-*-*-*-*-*-*-*-*-*-
# -*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-*-*-

ALLOWED_HOSTS = ["*"]

# Debug模式
DEBUG = True if os.environ.get("ANALYSIS_DEBUG_MODE") == "true" else False

# 管理员列表
ADMINS = []

# Notice：默认的SECRET_KEY仅测试用途，如在正式环境部署请重新生成
# 生成方式：
# 步骤一：执行 python 命令
# 步骤二：输入代码： from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())
# 步骤三：获取执行输出，拷贝替换下方的SECRET_KEY
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("ANALYSIS_SECRET_KEY", "25n=e*_e=4q!ert$4u#9v&^2n+)_#mi7&7ll@x29@j=w=k^q@^")

# 设置默认主键类型，适配django3.2
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# 数据库配置，可参考django数据库配置
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("ANALYSIS_DB_NAME", "codedog_analysis"),
        "USER": os.environ.get("ANALYSIS_DB_USER"),
        "PASSWORD": os.environ.get("ANALYSIS_DB_PASSWORD"),
        "HOST": os.environ.get("ANALYSIS_DB_HOST"),
        "PORT": os.environ.get("ANALYSIS_DB_PORT"),
        # "OPTIONS": {"charset":"utf8mb4"},
    }
}

# CELERY broker
REDIS_HOST = os.environ.get("ANALYSIS_REDIS_HOST")
REDIS_PORT = os.environ.get("ANALYSIS_REDIS_PORT")
REDIS_PASSWD = os.environ.get("ANALYSIS_REDIS_PASSWD")
REDIS_DBID = os.environ.get("ANALYSIS_REDIS_DBID", 0)
if REDIS_PASSWD:
    CELERY_BROKER_URL = 'redis://:%s@%s:%s/%s' % (REDIS_PASSWD, REDIS_HOST, REDIS_PORT, REDIS_DBID)
else:
    CELERY_BROKER_URL = 'redis://%s:%s/%s' % (REDIS_HOST, REDIS_PORT, REDIS_DBID)

# sentry日志上报
SENTRY_DSN = os.environ.get("ANALYSIS_SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration()]
    )


# -*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-*-*-
# -*-*-*-*-*-*-*-*-*-*-*-   服务交互配置    -*-*-*-*-*-*-*-*-*-*-*-
# -*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-*-*-


# API Ticket
API_TICKET_SALT = os.environ.get("API_TICKET_SALT")
API_TICKET_TOKEN = os.environ.get("API_TICKET_TOKEN")

# 本站域名，用于生成访问链接
LOCAL_DOMAIN = os.environ.get("LOCAL_DOMAIN", "")

# Main Server 接口
MAIN_SERVER_URL = os.environ.get("MAIN_SERVER_URL", "http://127.0.0.1:8001")

# 文件服务器
FILE_SERVER = {
    "URL": os.environ.get("FILE_SERVER_URL", "http://127.0.0.1:8000/files/"),
    # "TOKEN": os.environ.get("FILE_SERVER_TOKEN"),
    "TYPE_PREFIX": os.environ.get("FILE_SERVER_TYPE", "public")
}
