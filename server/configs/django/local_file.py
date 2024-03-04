# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
服务: FTPServer
"""
import os

DEBUG = True if os.environ.get("FILE_DEBUG_MODE") == "true" else False

# Notice：默认的SECRET_KEY仅测试用途，如在正式环境部署请重新生成
# 生成方式：
# 步骤一：执行 python 命令
# 步骤二：输入代码： from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())
# 步骤三：获取执行输出，拷贝替换下方的SECRET_KEY
SECRET_KEY = os.environ.get("FILE_SECRET_KEY", "4uf)0sfdth1bn7t450_6)_^+pcx4qa8_nw5l1!g3gp%0loq5p^")

# 服务域名
SITE_URL = os.environ.get("FILE_SITE_URL")

# sentry 上报路径， 如希望独立上报后台异常，可换用其他 sentry dsn
SENTRY_DSN = os.environ.get("FILE_SENTRY_DSN")

# 数据库配置
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("FILE_DB_NAME", "codedog_file"),
        "USER": os.environ.get("FILE_DB_USER"),
        "PASSWORD": os.environ.get("FILE_DB_PASSWORD"),
        "HOST": os.environ.get("FILE_DB_HOST"),
        "PORT": os.environ.get("FILE_DB_PORT"),
        # "OPTIONS": {"charset":"utf8mb4"},
    },
}

# 存储引擎配置
# 本地存储
STORAGE = {
    "CLIENT": os.environ.get("FILE_STORAGE_CLIENT", "LOCAL"),  # 存储方式
    "OPTIONS": {
        "DEFAULT_STORAGE_ROOT_DIR": os.environ.get("FILE_STORAGE_DIR", "data/ftp/"),  
    }
}

# COS
# STORAGE = {
#     "CLIENT": os.environ.get("FILE_STORAGE_CLIENT", "COS"),  # 存储方式
#     "OPTIONS": {
#         "TENCENT_COS_APPID": os.environ.get("TENCENT_COS_APPID", ""),
#         "TENCENT_COS_SECRETID": os.environ.get("TENCENT_COS_SECRETID", ""),
#         "TENCENT_COS_SECRETKEY": os.environ.get("TENCENT_COS_SECRETKEY", ""),
#         "TENCENT_COS_REGION": os.environ.get("TENCENT_COS_REGION", ""),
#         "TENCENT_COS_ROOT_BUCKET": os.environ.get("TENCENT_COS_ROOT_BUCKET", "bucket-appid"),
#     }
# }

# MINIO
# STORAGE = {
#     "CLIENT": os.environ.get("FILE_STORAGE_CLIENT", "MINIO"),  # 存储方式
#     "OPTIONS": {
#         "MINIO_ENTRYPOINT": os.environ.get("FILE_MINIO_ENTRYPOINT"),  # MinIO平台地址（API地址，非Console地址）
#         "MINIO_ACCESS_KEY": os.environ.get("FILE_MINIO_ACCESS_KEY"),  # MinIO登录账号
#         "MINIO_SECRET_KEY": os.environ.get("FILE_MINIO_SECRET_KEY"),  # MinIO登录密码
#     }
# }

# API Ticket
API_TICKET_SALT = os.environ.get("API_TICKET_SALT")
API_TICKET_TOKEN = os.environ.get("API_TICKET_TOKEN")
