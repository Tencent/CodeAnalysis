# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
服务: MainServer
环境: 开源环境通用配置
"""

from codedog.settings.base import *


# CodeDog开关配置
LOGIN_USER_TYPE = "codedog_user"


# CODEDOG用户审核开关
CODEDOG_USER_CHECK = True


# -*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-*-*-
# -*-*-*-*-*-*-*-*-*-*-*-     工程配置     -*-*-*-*-*-*-*-*-*-*-*-
# -*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-*-*-
DEBUG = os.environ.get("DEBUG_MODE", False)

ALLOWED_HOSTS = ["*"]

# 管理员列表
ADMINS = []

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "+n&#u&j(hgd!50-jh)qpc^cepe=6aip^1se%2%i_*f*ot)ur%3")

# 数据库配置，可参考django数据库配置
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("MYSQL_DATABASE"),
        "USER": os.environ.get("MYSQL_USER"),
        "PASSWORD": os.environ.get("MYSQL_PASSWORD"),
        "HOST": os.environ.get("MYSQL_HOST"),
        "PORT": os.environ.get("MYSQL_PORT")
    }
}


# -*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-*-*-
# -*-*-*-*-*-*-*-*-*-*-*-   服务交互配置    -*-*-*-*-*-*-*-*-*-*-*-
# -*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-*-*-

# 用于加解密密码的密钥，AES key must be either 16, 24, or 32 bytes long
PASSWORD_KEY = os.environ.get("PASSWORD_KEY")
# Server API key
API_TICKET_SALT = os.environ.get("API_TICKET_SALT")
API_TICKET_TOKEN = os.environ.get("API_TICKET_TOKEN")

# 文件服务器
FILE_SERVER = {
    "URL": os.environ.get("FILE_SERVER_URL"),
    "TOKEN": os.environ.get("FILE_SERVER_TOKEN"),
    "TYPE_PREFIX": os.environ.get("TYPE"),
}

# sentry日志上报
SENTRY_DSN = os.environ.get("SENTRY_URL")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration()]
    )


# Main server 接口
MAIN_SERVER_URL = os.environ.get("MAIN_SERVER_URL")
# Analyse Server 接口
ANALYSE_SERVER_URL = os.environ.get("ANALYSE_SERVER_URL")

# Scmproxy服务地址
SCMPROXY = os.environ.get("SCMPROXY_URL")
SCMPROXY_TIMEOUT = os.environ.get("SCMPROXY_TIMEOUT", 20)


REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")
REDIS_PASSWD = os.environ.get("REDIS_PASSWD")
REDIS_DBID = os.environ.get("REDIS_DBID")
CELERY_BROKER_URL = 'redis://:%s@%s:%s/%s' % (REDIS_PASSWD, REDIS_HOST, REDIS_PORT, REDIS_DBID)
redbeat_redis_url = CELERY_BROKER_URL


# CODEDOG 默认token
CODEDOG_TOKEN = os.environ.get("CODEDOG_TOKEN")
