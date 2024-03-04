# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""codedog.celery 说明
"""
# 2016-01-27    qfchen    created
# 2020-01-08    jerolin   update - 补充定时任务


import logging
import os

from celery import Celery
from celery.signals import after_setup_logger
from django.conf import settings

# set the default Django settings module for the "celery" program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "codedog_file_server.settings")

celery_app = Celery("codedog_file_server")

# Using a string here means the worker will not have to
# pickle the object when using Windows.
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()

# 定时任务配置
celery_app.conf.timezone = settings.TIME_ZONE
celery_app.conf.worker_max_tasks_per_child = 100

# celery 日志配置
logger = logging.getLogger(__name__)


@after_setup_logger.connect
def setup_loggers(*args, **kwargs):
    _logger = logging.getLogger()
    formatter = logging.Formatter(
        '-%(asctime)s-%(levelname)s-%(name)s: %(message)s')

    # StreamHandler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    _logger.addHandler(console_handler)

    # FileHandler
    fh = logging.FileHandler(os.path.join(
        settings.PROJECT_PATH, 'log', 'celery.log'))
    fh.setFormatter(formatter)
    _logger.addHandler(fh)
