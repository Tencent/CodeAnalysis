# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - v3 filters
"""
# 原生
import logging

# 第三方
from django.db.models import Q
from django_filters import rest_framework as filters

# 项目内
from apps.codeproj import models
from util.scm import ScmClient

logger = logging.getLogger(__name__)


class RepositoryFilter(filters.FilterSet):
    """代码库筛选

    ```python
    scm_url_or_name: str, 代码库地址或代码库名称, 模糊匹配
    scm_url: str, 代码库地址
    scope: str, 过滤范围
    ```
    """

    class ScopeEnum:
        ALL = "all"
        MY = "my"
        SUBSCRIBED = "subscribed"

    SCOPE_CHOICES = (
        (ScopeEnum.ALL, "全部"),
        (ScopeEnum.MY, "我创建的"),
        (ScopeEnum.SUBSCRIBED, "我关注的"),
    )
    scm_url_or_name = filters.CharFilter(label="scm_url_or_name", help_text="代码库地址或者名称，支持模糊匹配",
                                         method="scm_url_or_name_filter")
    scm_url = filters.CharFilter(label="scm_url", help_text="代码库仓库，会将地址转化为仓库地址再匹配",
                                 method="scm_url_filter")
    scope = filters.ChoiceFilter(label="scope", help_text="过滤范围", method="scope_filter", choices=SCOPE_CHOICES)

    def scm_url_or_name_filter(self, queryset, name, value):
        """scm_url、名称筛选
        统一格式后再进行筛选
        """
        value = value.replace("https://", "").replace("http://", "").strip().rstrip("/")
        if value.endswith(".git"):
            value = value[:-4]
        return queryset.filter(Q(scm_url__icontains=value) | Q(name__icontains=value))

    def scm_url_filter(self, queryset, name, value):
        try:
            git_repo = ScmClient(models.Repository.ScmTypeEnum.GIT, value,
                                 models.ScmAuth.ScmAuthTypeEnum.PASSWORD).get_repository()
            svn_repo = ScmClient(models.Repository.ScmTypeEnum.SVN, value,
                                 models.ScmAuth.ScmAuthTypeEnum.PASSWORD).get_repository()
            return queryset.filter(Q(scm_url=git_repo) | Q(scm_url=svn_repo))
        except Exception as err:
            logger.error("filter scm_url failed, err: %s, value: %s" % (err, value))
            return queryset.filter(scm_url="")

    def scope_filter(self, queryset, name, value):
        user = self.request.user
        if value == self.ScopeEnum.MY:
            return queryset.filter(creator=user)
        elif value == self.ScopeEnum.SUBSCRIBED:
            return queryset.filter(subscribers__username=user)
        return queryset

    class Meta:
        model = models.Repository
        fields = ["scm_url_or_name", "scm_url", "scope"]
