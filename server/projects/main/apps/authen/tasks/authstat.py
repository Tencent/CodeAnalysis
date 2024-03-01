# -*- coding: utf-8 -*-
#  Copyright (c) 2021-2024 THL A29 Limited
#  #
#  This source code file is made available under MIT License
#  See LICENSE for details
#  ==============================================================================

"""
authem - base tasks
"""
import logging

from codedog.celery import celery_app
from apps.authen.core import OauthManager

logger = logging.getLogger(__name__)


@celery_app.task
def refresh_oauth_token():
    """定时通过刷新oauthToken，避免过期
    """
    OauthManager.refresh_token()
