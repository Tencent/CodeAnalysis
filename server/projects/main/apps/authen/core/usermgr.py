# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
authen - user manager core
"""
import pytz
import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import User

from apps.authen import models

logger = logging.getLogger(__name__)


class UserManager(object):
    """基础用户管理
    """

    @classmethod
    def get_username(cls, user):
        """获取用户名
        """
        if user.codedoguser:
            return user.codedoguser.nickname
        else:
            cd_user = CodeDogUserManager.get_codedog_user(user)
            return cd_user.nickname

    @classmethod
    def get_user(cls, username):
        """获取用户
        """
        return User.objects.get(username=username)


class CodeDogUserManager(object):
    """CodeDog用户管理
    """
    @classmethod
    def get_codedog_user(cls, user, nickname=None):
        """获取关联的CodeDog用户
        """
        if not nickname:
            nickname = user.username
        codedog_user, created = models.CodeDogUser.objects.get_or_create(
            user=user, defaults={"nickname": nickname})
        if settings.CODEDOG_USER_CHECK is False:
            codedog_user.level = codedog_user.LevelEnum.SUPER_VIP
            codedog_user.status = codedog_user.StatusEnum.ACTIVE
            codedog_user.save()
        return codedog_user

    @classmethod
    def get_current_org_id(cls, codedog_user):
        """获取当前组织id
        """
        if codedog_user.org:
            return codedog_user.org_id
        else:
            return None

    @classmethod
    def validate_codedog_user_checked(cls, user):
        """判断codedog用户是否审批通过
        """
        codedog_user = cls.get_codedog_user(user)
        if codedog_user.status > codedog_user.StatusEnum.CHECKED:
            return False
        else:
            return True

    @classmethod
    def check_codedog_user(cls, apply_id, checker, check_result, expired_day_count, check_remark=None):
        """审批CodeDog用户申请
        如果用户已取消，则不能审批
        """
        codedog_user_perm_apply = models.CodeDogUserPermissionApply.objects.get(id=apply_id)
        if codedog_user_perm_apply.status == models.CodeDogUserPermissionApply.ApplyStatusEnum.CHECKED:
            logger.info("[User: %s][Applicant: %d] apply has been checked",
                        codedog_user_perm_apply.applicant, codedog_user_perm_apply.id)
        if codedog_user_perm_apply.status == models.CodeDogUserPermissionApply.ApplyStatusEnum.CANCELED:
            logger.info("[User: %s][Applicant: %d] apply has been canceld",
                        codedog_user_perm_apply.applicant, codedog_user_perm_apply.id)

        with transaction.atomic():
            # 审批通过时，调整用户状态
            if check_result == models.CodeDogUserPermissionApply.CheckResultEnum.PASS:
                codedog_user = codedog_user_perm_apply.applicant
                codedog_user.status = codedog_user.StatusEnum.ACTIVE
                # 审批当日开始，增加续期时间
                if expired_day_count:
                    codedog_user.expired_time = datetime.now(tz=pytz.UTC) + timedelta(days=expired_day_count)
                    check_remark = "%s，用户账号过期天数：%d 天" % (check_remark, expired_day_count)
                else:
                    codedog_user.expired_time = datetime(2099, 12, 31, tzinfo=pytz.UTC)
                    check_remark = "%s，永久账号" % check_remark
                codedog_user.save()
            models.CodeDogUserPermissionApply.objects.select_for_update().filter(id=apply_id).update(
                checker=checker, check_result=check_result,
                check_remark=check_remark, check_time=timezone.now(),
                status=codedog_user_perm_apply.ApplyStatusEnum.CHECKED)
        codedog_user_perm_apply.refresh_from_db()
        return codedog_user_perm_apply
