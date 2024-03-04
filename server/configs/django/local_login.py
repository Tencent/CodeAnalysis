# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
服务: LoginServer
"""
import os
from datetime import timedelta

from .open_base import *

DEBUG = True if os.environ.get("LOGIN_DEBUG_MODE") == "true" else False

# Notice：默认的SECRET_KEY仅测试用途，如在正式环境部署请重新生成
# 生成方式：
# 步骤一：执行 python 命令
# 步骤二：输入代码： from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())
# 步骤三：获取执行输出，拷贝替换下方的SECRET_KEY
SECRET_KEY = os.environ.get("LOGIN_SECRET_KEY", "iht%_(ixb)w&sedrh2t-ydxnre)uy+=_hv4v^8m@19p27r6sz_")

# 数据库配置，可参考django数据库配置
DATABASES = {
    "default": {
       "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("LOGIN_DB_NAME", "codedog_login"),
        "USER": os.environ.get("LOGIN_DB_USER"),
        "PASSWORD": os.environ.get("LOGIN_DB_PASSWORD"),
        "HOST": os.environ.get("LOGIN_DB_HOST"),
        "PORT": os.environ.get("LOGIN_DB_PORT"),
        # "OPTIONS": {"charset": "utf8mb4"}
    }
}

pub_key = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDtuJtwo+ZkqAA7ZKNdzcQM1N+r
anRqpNE+R4MKfzCa4uKURK9z7cG6DQT6ihpdSYw36iaMIRMYUM7SsismpYYe68q3
98nXivMpCDOeO3VC91Y8DU/9058smPswwr6kYFU/TZIDAUqb+H6T5DSbKnl7WZqx
UdWbyBDJ9R9QeSy0owIDAQAB
-----END PUBLIC KEY-----"""

private_key = """-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQDtuJtwo+ZkqAA7ZKNdzcQM1N+ranRqpNE+R4MKfzCa4uKURK9z
7cG6DQT6ihpdSYw36iaMIRMYUM7SsismpYYe68q398nXivMpCDOeO3VC91Y8DU/9
058smPswwr6kYFU/TZIDAUqb+H6T5DSbKnl7WZqxUdWbyBDJ9R9QeSy0owIDAQAB
AoGBAMqsoQH5Cx34SjJZDBuWqjaSa5wW5+hgWvFxQNz7MbJsC+eDY98/7vIz1XHR
usacRQsK/BBuxnvtsVfbhYSujNg9Xu26LqK4A2mCDiD5RY8pjP+bTpcDZ3Jv4+2Q
MC3HQm9h8m7e+Q+K13YMbnlZrJpcYHvff3uZroDhYlIkYVCZAkEA+P0qTWVRrY6a
a+NmNdCd8WHyAh+E4kOiMEAyNGIUL97aRh+IEvrwMXKd0d7cc4B0ObhadwCpz6DP
+sCp9s55/QJBAPRqN9K8sCs5sXvosjoJWPCVrWVAAw6MvmjK/KGbD88vDP2nBy2X
5gBsO0FO6ivKnGUdGQ2Nvu4YnGOYfvm7Wx8CQQDphbfZIv+6AZc/POWt711S+QPb
jeg5tik1i+AKVTqNszuQrR4YfxYrqk3uelDUW1OmlwrxtcOOIkst6Oj/u6OZAkBZ
NSuKzzO9kyEkiJoEdMTxiq/u9J4pAVW+CdiLY30xsYqcSgpkqbxZCyfVfmgZ86mB
fk1WlRXK8VCjSVWO8MMhAkA9G6/KN+M6M1Ugn8jocqUHFUfYxqvGlnt4LKVrXrr4
YccaAieToIOQXUIzjrL6gZhFQUiTtC5rm/joHaLs/sa6
-----END RSA PRIVATE KEY-----"""

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,

    "ALGORITHM": "RS256",
    "VERIFYING_KEY": pub_key,
    "SIGNING_KEY": private_key,

    "AUTH_HEADER_TYPES": ("CodeDog",),
    "USER_ID_FIELD": "uid",
    "USER_ID_CLAIM": "user_id",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",

    "JTI_CLAIM": "jti",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",

    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=60),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}

OAUTH_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=1),
    "AUTH_HEADER_TYPES": ("Oauth",),
    "VERIFYING_KEY": pub_key,
    "SIGNING_KEY": private_key,
}

# 用于加解密密码的密钥
PASSWORD_KEY = os.environ.get("PASSWORD_KEY")

# Server API key
API_TICKET_SALT = os.environ.get("API_TICKET_SALT")
API_TICKET_TOKEN = os.environ.get("API_TICKET_TOKEN")

# Login默认的管理员账号
TCA_DEFAULT_ADMIN = os.environ.get("TCA_DEFAULT_ADMIN")
TCA_DEFAULT_PASSWORD = os.environ.get("TCA_DEFAULT_PASSWORD")
