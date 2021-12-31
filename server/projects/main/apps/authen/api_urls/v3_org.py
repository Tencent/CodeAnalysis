# -*- coding: utf-8 -*-
"""
authen - v3 apis for org
"""

# 第三方 import
from django.urls import path

# 项目内 import
from apps.authen.apis import v3

# 前缀/api/v3/
urlpatterns = [
    path("orgs/", v3.OrganizationListApiView.as_view(), name="apiv3_org_list"),
    path("orgs/invited/<str:code>/", v3.OrganizationMemberConfInvitedApiView.as_view(),
         name="apiv3_org_invited_code"),
    path("orgs/<str:org_sid>/", v3.OrganizationDetailApiView.as_view(),
         name="apiv3_org_detail"),
    path("orgs/<str:org_sid>/memberconf/", v3.OrganizationMemberInviteApiView.as_view(),
         name="apiv3_org_member_conf"),
    path("orgs/<str:org_sid>/memberconf/<int:role>/<str:username>/",
         v3.OrganizationMemberDeleteApiView.as_view(),
         name="apiv3_org_member_role_user"),
]
