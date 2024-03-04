# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

from __future__ import absolute_import
 
# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import celery_app
