# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
base - apimixins
"""

import logging

from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import NotFound

from apps.authen.models import Organization
from apps.codeproj.models import Project, ProjectTeam, Repository, ScanScheme
from apps.scan_conf.models import CheckPackage, CheckRule, CheckTool, ToolLib, ToolLibScheme

logger = logging.getLogger(__name__)


class GetOrCreateMixin(object):
    """
    重载 get_object方法为get_or_create。适用于默认生成实例的场景。
    """

    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        try:
            obj, created = queryset.get_or_create(**filter_kwargs)
        except IntegrityError as e:
            logger.exception(e)
            raise NotFound('无法获取对象，且尝试新建对象失败')

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


class CustomSerilizerMixin(object):
    """
    重载 get_serializer_class方法为get_or_create。适用于默认生成实例的场景。
    """

    def get_serializer_class(self):
        if self.request and self.request.method == 'PUT':
            if hasattr(self, 'put_serializer_class'):
                return self.put_serializer_class
        if self.request and self.request.method == 'POST':
            if hasattr(self, 'post_serializer_class'):
                return self.post_serializer_class
        return generics.GenericAPIView.get_serializer_class(self)


def attachment_response(export_data, filename='download.xls', content_type='application/vnd.ms-excel'):
    # Django 1.7 uses the content_type kwarg instead of mimetype
    try:
        response = HttpResponse(export_data, content_type=content_type)
    except TypeError:
        response = HttpResponse(export_data, mimetype=content_type)
    response['Content-Disposition'] = 'attachment; filename={}'.format(filename)
    return response


class BaseGetModelMixinAPIView(object):
    """获取对象
    """

    def get_repo_with_kwargs(self, **kwargs):
        """获取代码库
        :param kwargs:
            repo_id: int, url代码库ID参数
        :return: repo
        """
        repo_id = kwargs["repo_id"]
        logger.info("[Repo: %s] find repo" % (repo_id))
        return get_object_or_404(Repository, id=repo_id)

    def get_repo(self):
        """获取代码库，利用self.kwargs传递链接参数
        :return: repo
        """
        return self.get_repo_with_kwargs(**self.kwargs)

    def get_project_with_kwargs(self, **kwargs):
        """获取分支项目
        :param kwargs:
            repo_id: int, url代码库ID参数
            project_id: int, url分支项目ID参数
        :return: project
        """
        repo_id = kwargs["repo_id"]
        project_id = kwargs["project_id"]
        logger.info("[Repo: %s][Project: %s] find project" % (repo_id, project_id))
        return get_object_or_404(Project, id=project_id, repo_id=repo_id)

    def get_project(self):
        """获取分支项目，利用self.kwargs传递链接参数
        :return: project
        """
        return self.get_project_with_kwargs(**self.kwargs)

    def get_scheme_with_kwargs(self, **kwargs):
        """获取扫描方案
        :param kwargs:
            repo_id: int, url代码库ID参数
            scheme_id: int, url扫描方案ID参数
        :return: scheme
        """
        repo_id = kwargs["repo_id"]
        scheme_id = kwargs["scheme_id"]
        logger.info("[Repo: %s][ScanScheme: %s] find scheme" % (repo_id, scheme_id))
        return get_object_or_404(ScanScheme, id=scheme_id, repo_id=repo_id)

    def get_scheme(self):
        """获取扫描方案，利用self.kwargs传递链接参数
        :return: scheme
        """
        return self.get_scheme_with_kwargs(**self.kwargs)

    def get_checkprofile_with_kwargs(self, **kwargs):
        """获取扫描方案规则配置
        :param kwargs:
            repo_id: int, url代码库ID参数
            scheme_id: int, url扫描方案ID参数
        :return: checkprofile
        """
        scheme = self.get_scheme_with_kwargs(**kwargs)
        logger.info("[ScanScheme: %s] find checkprofile" % scheme.id)
        checkprofile = scheme.get_checkprofile()
        if not checkprofile:
            raise NotFound()
        return checkprofile

    def get_checkprofile(self):
        """获取扫描方案规则配置，利用self.kwargs传递链接参数
        :return: checkprofile
        """
        return self.get_checkprofile_with_kwargs(**self.kwargs)

    def get_checkpackage_with_kwargs(self, **kwargs):
        """获取扫描方案具体官方规则包、规则配置
        :param kwargs:
            repo_id: int, url代码库ID参数
            scheme_id: int, url扫描方案ID参数
            checkpackage_id: int, url扫描方案官方规则包ID参数
        :return: (checkpackage, checkprofile)
        """
        checkprofile = self.get_checkprofile_with_kwargs(**kwargs)
        checkpackage_id = kwargs["checkpackage_id"]
        # 暂时兼容处理
        if checkpackage_id == checkprofile.custom_checkpackage_id:
            checkpackage = checkprofile.custom_checkpackage
        else:
            checkpackage = CheckPackage.objects.filter(id=checkpackage_id,
                                                       package_type=CheckPackage.PackageTypeEnum.OFFICIAL).first()
            # checkpackage = checkprofile.checkpackages.filter(id=checkpackage_id).first()
        if not checkpackage:
            raise NotFound("规则配置不存在该规则包")
        return (checkpackage, checkprofile)

    def get_checkprofile_checkpackage(self):
        """获取扫描方案具体官方规则包、规则配置，利用self.kwargs传递链接参数
        :return: (checkpackage, checkprofile)
        """
        return self.get_checkpackage_with_kwargs(**self.kwargs)

    def get_checktool_with_kwargs(self, **kwargs):
        """获取工具
        :param kwargs:
            checktool_id: int, 工具ID
        :return: checktool
        """
        checktool_id = kwargs["checktool_id"]
        logger.info("[CheckTool: %s] find checktool" % (checktool_id))
        return get_object_or_404(CheckTool, id=checktool_id)

    def get_checktool(self):
        """获取工具，利用self.kwargs传递链接参数
        :return: checktool
        """
        return self.get_checktool_with_kwargs(**self.kwargs)

    def get_checktool_rule_with_kwargs(self, **kwargs):
        """获取工具规则
        :param kwargs:
            checktool_id: int, 工具ID
            checkrule_id: int, 规则ID
        :return: checktool
        """
        checktool_id = kwargs["checktool_id"]
        checkrule_id = kwargs["checkrule_id"]
        logger.info("[CheckTool: %s][CheckRule: %s] find checktool" % (checktool_id, checkrule_id))
        return get_object_or_404(CheckRule, checktool_id=checktool_id, id=checkrule_id)

    def get_checktool_rule(self):
        """获取工具规则，利用self.kwargs传递链接参数
        """
        return self.get_checktool_rule_with_kwargs(**self.kwargs)

    def get_toollib_with_kwargs(self, **kwargs):
        """获取工具依赖
        :param kwargs:
            toollib_id: int, 工具依赖ID
        :return: toollib
        """
        toollib_id = kwargs["toollib_id"]
        logger.info("[ToolLib: %s] find toollib" % (toollib_id))
        return get_object_or_404(ToolLib, id=toollib_id)

    def get_toollib(self):
        """获取工具依赖，利用self.kwargs传递链接参数
        :return: toollib
        """
        return self.get_toollib_with_kwargs(**self.kwargs)

    def get_libscheme_with_kwargs(self, **kwargs):
        """获取工具依赖方案
        :param kwargs:
            checktool_id: int, 工具ID
            libscheme_id: int, 工具依赖方案ID
        :return: toollibscheme
        """
        checktool_id = kwargs["checktool_id"]
        libscheme_id = kwargs["libscheme_id"]
        logger.info("[CheckTool: %s][ToolLibScheme: %s] find ToolLibScheme" % (checktool_id, libscheme_id))
        return get_object_or_404(ToolLibScheme, id=libscheme_id, checktool_id=checktool_id)

    def get_libscheme(self):
        """获取工具依赖方案，利用self.kwargs传递链接参数
        :return: toollibscheme
        """
        return self.get_libscheme_with_kwargs(**self.kwargs)


class V3GetModelMixinAPIView(BaseGetModelMixinAPIView):

    def get_org_with_kwargs(self, **kwargs):
        """获取团队
        :param kwargs:
            org_sid: str, url团队org_sid参数
        :return: org
        """
        org_sid = kwargs["org_sid"]
        logger.info("[Org: %s] find org" % org_sid)
        return get_object_or_404(Organization, org_sid=org_sid)

    def get_org(self):
        """获取团队，利用self.kwargs传递链接参数
        :return: org
        """
        return self.get_org_with_kwargs(**self.kwargs)

    def get_project_team_with_kwargs(self, **kwargs):
        """获取项目
        :param kwargs:
            org_sid: str, url团队org_sid参数
            team_name: str, url项目team_name参数
        :return: project_team
        """
        org_sid = kwargs["org_sid"]
        team_name = kwargs["team_name"]
        logger.info("[Org: %s][Team: %s] find project-team" % (org_sid, team_name))
        return get_object_or_404(ProjectTeam, name=team_name, organization__org_sid=org_sid)

    def get_project_team(self):
        """获取项目，利用self.kwargs传递链接参数
        :return: project_team
        """
        return self.get_project_team_with_kwargs(**self.kwargs)

    def get_repo_with_kwargs(self, **kwargs):
        """获取代码库
        :param kwargs:
            org_sid: str, url团队org_sid参数
            team_name: str, url项目team_name参数
            repo_id: int, url代码库ID参数
        :return: repo
        """
        org_sid = kwargs["org_sid"]
        team_name = kwargs["team_name"]
        repo_id = kwargs["repo_id"]
        logger.info("[Org: %s][Team: %s][Repo: %s] find repo" % (org_sid, team_name, repo_id))
        return get_object_or_404(Repository, id=repo_id, project_team__name=team_name,
                                 project_team__organization__org_sid=org_sid)

    def get_project_with_kwargs(self, **kwargs):
        """获取分支项目
        :param kwargs:
            org_sid: str, url团队org_sid参数
            team_name: str, url项目team_name参数
            repo_id: int, url代码库ID参数
            project_id: int, url分支项目ID参数
        :return: project
        """
        org_sid = kwargs["org_sid"]
        team_name = kwargs["team_name"]
        repo_id = kwargs["repo_id"]
        project_id = kwargs["project_id"]
        logger.info("[Org: %s][Team: %s][Repo: %s][Project: %s] find project" % (
            org_sid, team_name, repo_id, project_id))
        return get_object_or_404(Project, id=project_id, repo_id=repo_id,
                                 repo__project_team__organization__org_sid=org_sid,
                                 repo__project_team__name=team_name)

    def get_scheme_with_kwargs(self, **kwargs):
        """获取分析方案，做了兼容处理，根据url不同区分获取代码库分析方案还是分析方案模板
        :param kwargs:
            org_sid: str, url团队org_sid参数
            team_name: str, url项目team_name参数，如果是分析方案模板url则无team_name
            repo_id: int, url代码库ID参数，如果是分析方案模板url则无repo_id
            scheme_id: int, url分析方案ID参数
        :return: scheme
        """
        org_sid = kwargs["org_sid"]
        team_name = kwargs.get("team_name", None)
        repo_id = kwargs.get("repo_id", None)
        scheme_id = kwargs["scheme_id"]
        if team_name and repo_id:
            # 获取代码库分析方案
            logger.info("[Org: %s][Team: %s][Repo: %s][ScanScheme: %s] find scheme" % (
                org_sid, team_name, repo_id, scheme_id))
            return get_object_or_404(ScanScheme, id=scheme_id, repo_id=repo_id,
                                     repo__project_team__organization__org_sid=org_sid,
                                     repo__project_team__name=team_name)
        else:
            # 获取分析方案模板
            logger.info("[Org: %s][ScanScheme: %s] find global scheme" % (org_sid, scheme_id))
            scheme = ScanScheme.objects.filter(id=scheme_id, repo__isnull=True,
                                               scheme_key=ScanScheme.SchemeKey.PUBLIC).first()
            if not scheme:
                scheme = get_object_or_404(ScanScheme, id=scheme_id, repo__isnull=True, scheme_key='org_%s' % org_sid)
            return scheme
