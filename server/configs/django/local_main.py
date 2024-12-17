# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
服务: MainServer
"""
import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

from codedog.settings.open_base import *
from corsheaders.defaults import default_headers

# -*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-*-*-
# -*-*-*-*-*-*-*-*-*-*-*-     工程配置     -*-*-*-*-*-*-*-*-*-*-*-
# -*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-*-*-
# Debug模式
DEBUG = True if os.environ.get("MAIN_DEBUG_MODE") == "true" else False

ALLOWED_HOSTS = ["*"]

# 管理员列表
ADMINS = []

# Notice：默认的SECRET_KEY仅测试用途，如在正式环境部署请重新生成
# 生成方式：
# 步骤一：执行 python 命令
# 步骤二：输入代码： from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())
# 步骤三：获取执行输出，拷贝替换下方的SECRET_KEY
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("MAIN_SECRET_KEY", "lh+6y8pyf16bbor*)p=kp=p(cg615+y+5nnin$l(n%os$8z^v%")

# 设置默认主键类型，适配django3.2
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# 数据库配置，可参考django数据库配置
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("MAIN_DB_NAME", "codedog_main"),
        "USER": os.environ.get("MAIN_DB_USER"),
        "PASSWORD": os.environ.get("MAIN_DB_PASSWORD"),
        "HOST": os.environ.get("MAIN_DB_HOST"),
        "PORT": os.environ.get("MAIN_DB_PORT"),
        # "OPTIONS": {"charset":"utf8mb4"},
    }
}

# CELERY broker
REDIS_HOST = os.environ.get("MAIN_REDIS_HOST")
REDIS_PORT = os.environ.get("MAIN_REDIS_PORT")
REDIS_PASSWD = os.environ.get("MAIN_REDIS_PASSWD")
REDIS_DBID = os.environ.get("MAIN_REDIS_DBID", 1)

if REDIS_PASSWD:
    CELERY_BROKER_URL = "redis://:%s@%s:%s/%s" % (REDIS_PASSWD, REDIS_HOST, REDIS_PORT, REDIS_DBID)
else:
    CELERY_BROKER_URL = "redis://%s:%s/%s" % (REDIS_HOST, REDIS_PORT, REDIS_DBID)

redbeat_redis_url = CELERY_BROKER_URL

# sentry日志上报
SENTRY_DSN = os.environ.get("MAIN_SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration()]
    )

# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-
# CodeDog运行环境配置
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-
HTTPS_CLONE_FLAG = True if os.environ.get("HTTPS_CLONE_FLAG") == "true" else False

# -*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-*-*-
# -*-*-*-*-*-*-*-*-*-*-*-   服务交互配置    -*-*-*-*-*-*-*-*-*-*-*-
# -*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-*-*-

# 用于加解密密码的密钥
PASSWORD_KEY = os.environ.get("PASSWORD_KEY")
NODE_TICKET_SALT = os.environ.get("NODE_TICKET_SALT") or PASSWORD_KEY
# Server API key
API_TICKET_SALT = os.environ.get("API_TICKET_SALT")
API_TICKET_TOKEN = os.environ.get("API_TICKET_TOKEN")

# 本站域名，用于生成访问链接
LOCAL_DOMAIN = os.environ.get("LOCAL_DOMAIN", "")

# CODEPUPPY 默认token
CODEDOG_TOKEN = os.environ.get("CODEDOG_TOKEN")

# Web Server, 用于本地扫描
WEB_SERVER_URL = os.environ.get("WEB_SERVER_URL", "http://127.0.0.1")
# Main server，用于本地扫描
MAIN_SERVER_URL = os.environ.get("MAIN_SERVER_URL", "http://127.0.0.1:8001")
# Analyse Server 接口
ANALYSE_SERVER_URL = os.environ.get("ANALYSE_SERVER_URL", "http://127.0.0.1:8002")
# Login服务地址
LOGIN_SERVER_URL = os.environ.get("LOGIN_SERVER_URL", "http://127.0.0.1:8003")
# Scmproxy服务地址
SCMPROXY = os.environ.get("SCMPROXY", "http://127.0.0.1:8009")
SCMPROXY_TIMEOUT = os.environ.get("SCMPROXY_TIMEOUT", 300)

# 文件服务器
FILE_SERVER = {
    "URL": os.environ.get("FILE_SERVER_URL", "http://127.0.0.1:8000/files/"),
    # "TOKEN": os.environ.get("FILE_SERVER_TOKEN"),
    "TYPE_PREFIX": os.environ.get("FILE_SERVER_TYPE", "public")
}

# 登录鉴权公钥
# Notice：默认的公钥仅测试用途，如在正式环境部署请重新生成
AUTHORIZATION_PUBKEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDtuJtwo+ZkqAA7ZKNdzcQM1N+r
anRqpNE+R4MKfzCa4uKURK9z7cG6DQT6ihpdSYw36iaMIRMYUM7SsismpYYe68q3
98nXivMpCDOeO3VC91Y8DU/9058smPswwr6kYFU/TZIDAUqb+H6T5DSbKnl7WZqx
UdWbyBDJ9R9QeSy0owIDAQAB
-----END PUBLIC KEY-----"""
