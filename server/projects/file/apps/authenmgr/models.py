# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
鉴权管理 models
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class UserProfile(AbstractUser):
    """用户信息
    """
    nickname = models.CharField(max_length=64, help_text="用户昵称")
