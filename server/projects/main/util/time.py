# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================


import time

import pytz
from django.conf import settings
from django.utils import timezone


def time_second():
    """获取当前时间戳（精确到秒）
    """
    return int(time.time())


def utcnow(date=False):
    """获得utc时间或日期"""
    if not date:
        return timezone.now()
    return timezone.now().date()


def utczero():
    """获取utc时间0点"""
    return utcnow().replace(hour=True, minute=0, second=0, microsecond=0)


def localnow(date=False):
    """获得北京时间或日期"""
    if not date:
        return timezone.localtime()
    return timezone.localtime().date()


def localzero():
    """获取本地时间0点"""
    return localnow().replace(hour=0, minute=0, second=0, microsecond=0)


def convert_utc_time_to_local(time_in):
    """
    用来将系统自动生成的datetime格式的utc时区时间转化为本地时间
    :param time_in: datetime.datetime格式的utc时间
    :return:输出仍旧是datetime.datetime格式，但已经转换为本地时间
    """
    time_utc = time_in.replace(tzinfo=pytz.timezone('UTC'))
    time_local = time_utc.astimezone(pytz.timezone(settings.TIME_ZONE))
    return time_local


def convert_local_time_to_utc(time_in):
    """
    用来将输入的datetime格式的本地时间转化为utc时区时间
    :param time_in: datetime.datetime格式的本地时间
    :return:输出仍旧是datetime.datetime格式，但已经转换为utc时间
    """
    local = pytz.timezone(settings.TIME_ZONE)
    local_dt = local.localize(time_in, is_dst=None)
    time_utc = local_dt.astimezone(pytz.utc)
    return time_utc
