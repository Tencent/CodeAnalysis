# -*- coding: utf-8 -*-
#  Copyright (c) 2021-2024 THL A29 Limited
#  #
#  This source code file is made available under MIT License
#  See LICENSE for details
#  ==============================================================================

"""oauth配置管理类
"""
import logging
import time

from django.conf import settings

from apps.authen.models import ScmAuthInfo, ScmOauthSetting
from apps.codeproj.models import Repository
from util.cdcrypto import decrypt, encrypt
from util.scm import SCM_PLATFORM_NAME_AS_KEY, SCM_PLATFORM_NUM_AS_KEY, NEED_REFRESH_SCM_PLATFORMS, ScmClient

logger = logging.getLogger(__name__)


class OauthManager(object):
    """oauth相关管理类
    """

    @classmethod
    def get_oauth_setting(cls, scm_platform):
        """获取指定scm平台的配置
        :param scm_platform: <str/int> scm平台类型
        :return ScmOauthSetting: scm配置数据
        """
        if isinstance(scm_platform, str):
            scm_platform = SCM_PLATFORM_NAME_AS_KEY.get(scm_platform, None)
        if not scm_platform:
            logger.warning("[OauthMgr] 传入的scm平台类型不存在: %s" % scm_platform)
            return None
        return ScmOauthSetting.objects.filter(scm_platform=scm_platform)

    @classmethod
    def get_user_oauth_info(cls, user):
        """获取用户各scm平台授权信息
        :param user: <User> 用户
        :return: 用户scm授权信息
        """
        result = dict((scm_platform, False) for scm_platform, _ in SCM_PLATFORM_NAME_AS_KEY.items())
        auth_infos = ScmAuthInfo.objects.filter(user=user)
        for auth_info in auth_infos:
            if auth_info.gitoa_access_token:
                result[SCM_PLATFORM_NUM_AS_KEY[auth_info.scm_platform]] = True
        result.pop("other")
        return result

    @classmethod
    def refresh_token(cls):
        """刷新即将达到过期时间的token
        """
        current_timestamp = int(time.time())
        logger.info("[OauthMgr] Refresh token at %s" % current_timestamp)
        # 刷新即将在一小时内过期的Token
        expiring_auth_infos = ScmAuthInfo.objects.filter(gitoa_access_token__isnull=False,
                                                         gitoa_refresh_token__isnull=False,
                                                         expires_at__lte=current_timestamp + 60 * 60,
                                                         scm_platform__in=NEED_REFRESH_SCM_PLATFORMS)
        for auth_info in expiring_auth_infos:
            scm_platform = SCM_PLATFORM_NUM_AS_KEY[auth_info.scm_platform]
            data = {"refresh_token": decrypt(auth_info.gitoa_refresh_token, settings.PASSWORD_KEY)}
            if scm_platform == "gitlab":
                # gitlab 需要额外的参数
                oauth_setting = OauthManager.get_oauth_setting(scm_platform)
                if not oauth_setting:
                    logger.info("[OauthMgr] scm platform gitlab has not oauth settings")
                    continue
                oauth_setting = oauth_setting.first()
                data.update({"redirect_uri": oauth_setting.redirect_uri,
                             "client_id": oauth_setting.decrypted_client_id,
                             "client_secret": oauth_setting.decrypted_client_secret})
            try:
                git_client = ScmClient(Repository.ScmTypeEnum.GIT, scm_url="", auth_type="oauth",
                                       scm_platform=scm_platform)
                result = git_client.get_token_through_refresh_token(auth_info=data)
            except Exception as msg:
                logger.exception("refresh token failed, err: %s" % msg)
                continue
            # 更新authinfo数据
            auth_info.gitoa_access_token = encrypt(result["access_token"], settings.PASSWORD_KEY)
            auth_info.gitoa_refresh_token = encrypt(result["refresh_token"], settings.PASSWORD_KEY)
            auth_info.expires_at = result["expires_in"] + result["created_at"]
            auth_info.save()
