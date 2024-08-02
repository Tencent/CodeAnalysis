# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
login - models
"""
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, UserManager

from login.lib.Cipher import base62_cipher
from login.lib.snowflake import IdWorker, GenerateId


def gen_id():
    """
    雪花算法生成id
    用base62压缩
    """
    worker = IdWorker(GenerateId.get_data_center_id(),
                      GenerateId.get_work_id(), 0)
    _id = worker.get_id()
    base62_id = base62_cipher.int_to_str62(_id)
    return base62_id


class UserInfo(AbstractBaseUser):
    """
    用户信息表
    """
    GENDER_CHOICES = (
        (2, "female"),
        (1, "male"),
        (0, "unknown")
    )

    objects = UserManager()

    uid = models.CharField(max_length=20, primary_key=True, default=gen_id, unique=True)
    nickname = models.CharField(max_length=1000)
    avatar_url = models.CharField(max_length=500)

    # 地区
    city = models.CharField(max_length=150, default="")
    province = models.CharField(max_length=150, default="")
    country = models.CharField(max_length=100, default="")

    # 联系方式
    phone = models.CharField(max_length=30, default="")
    mail = models.CharField(max_length=120, default="")

    # 1为男，2为女，0为未知
    gender_type = models.IntegerField(choices=GENDER_CHOICES, default=0)

    # 以下两个为通过token验证，必须存在
    # 默认是正常用户，否则注销
    is_active = models.BooleanField(default=True)
    # 用户名（和昵称不一样）
    username = models.CharField(max_length=100, default="")
    password = models.CharField(max_length=100, default="", blank=False)

    USERNAME_FIELD = "uid"
    REQUIRED_FIELDS = []

    # 时间
    create_time = models.DateTimeField("date published", default=timezone.now)
    update_time = models.DateTimeField("date updated", default=timezone.now)

    def __str__(self):
        return str(self.uid)


# 第三方授权信息表
class UserAuth(models.Model):
    """
    第三方授权信息表
    """
    user = models.ForeignKey("login.UserInfo", on_delete=models.CASCADE, blank=True, null=True)
    uid = models.CharField(max_length=20, primary_key=True, default=gen_id, unique=True)
    # 微信：wechat，qq：qq，企业微信：wework
    identity_type = models.CharField(max_length=20)
    # 手机号/邮箱/第三方的唯一标识(open_id)
    identifier = models.CharField(max_length=100)
    # 密码凭证 (自建账号的保存密码, 第三方的保存 token)
    credential = models.CharField(max_length=300)
    # 是否已经验证了，比如手机和邮箱，第三方默认验证,0为未验证，1为验证
    verified = models.IntegerField(default=0)
