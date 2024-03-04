# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
v3 api 接口url定义，v2系列接口均供前端页面调用
"""

# 第三方 import
from django.urls import path

# 项目内 import
from apps.authen.apis import v3

# 前缀/api/v3/authen/
urlpatterns = [
    path("userinfo/", v3.UserInfoApiView.as_view(),
         name="apiv3_userinfo"),
    path('userinfo/token/', v3.UserTokenView.as_view(),
         name="apiv3_userinfo_token"),
    path("scmallaccounts/", v3.ScmAllAcountListApiView.as_view(),
         name="apiv3_all_scm_accounts"),
    path("scmaccounts/", v3.ScmAccountListApiView.as_view(),
         name="apiv3_scm_account_list"),
    path("scmaccounts/<int:account_id>/", v3.ScmAccountDetailApiView.as_view(),
         name="apiv3_scm_account_detail"),
    path("scmsshinfos/", v3.ScmSSHInfoListApiView.as_view(),
         name="apiv3_scm_sshinfo_list"),
    path("scmsshinfos/<int:sshinfo_id>/", v3.ScmSSHInfoDetailApiView.as_view(),
         name="apiv3_scm_sshinfo_detail"),
    path("oauthsettings/", v3.OauthSettingsStatusAPIView.as_view(), name="apiv3_oauthsettings_status"),
    path("scmauthinfo/", v3.ScmAuthInfoCheckApiView.as_view(),
         name="apiv3_scmauthinfocheck"),
    path("scmauthinfos/", v3.ScmAuthInfoListApiView.as_view(), name="apiv3_scmauthinfos_list"),

    path("gitcallback/<str:scm_platform_name>/", v3.GitCallbackPlatformByScmProxy.as_view(),
         name="apiv3_gitcallback_platform"),
]
