#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""工程初始化文件
"""
# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.

from .celery import celery_app
