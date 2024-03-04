# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
permissions - proxy permission
"""


import re
import logging

from rest_framework import permissions

from apps.codeproj.models import Project, Repository, ScanScheme, ProjectTeam, Organization


logger = logging.getLogger(__name__)


class ProxyServerPermission(permissions.BasePermission):
    """代理服务权限
    """

    def check_other_server_permission(self, original_uri, user):
        """检查其他服务的权限
        """
        reg = re.findall(r"/puppy_versions/", original_uri)
        if reg and user.is_superuser:
            logger.info("[Server: Files][User: %s] Get %s, checking user permission" % (user, original_uri))
            return True

    def check_repo_id(self, repo_id, username):
        """检查代码库编号
        """
        logger.info("Get scan repo[%d], checking user[%s] permission..." % (repo_id, username))
        try:
            return Repository.objects.get(id=repo_id)
        except Repository.DoesNotExist:
            logger.info("[Repo: %d] repo does not exist" % repo_id)
            return None

    def check_scheme_id(self, scheme_id, username):
        """检查扫描方案编号
        """
        logger.info("Get scan schme[%d], checking user[%s] permission..." % (scheme_id, username))
        try:
            scan_scheme = ScanScheme.objects.get(id=scheme_id)
            return scan_scheme.repo
        except ScanScheme.DoesNotExist:
            logger.info("[ScanScheme: %d] repo does not exist" % scheme_id)
            return None

    def check_project_id(self, project_id, username):
        """检查项目编号
        """
        logger.info("Get project[%d], checking user[%s] permission..." % (project_id, username))
        try:
            project = Project.objects.get(id=project_id)
            return project.repo
        except Project.DoesNotExist:
            logger.info("[Project: %d] project does not exist" % project_id)
            return None

    def has_permission(self, request, view):
        original_uri = request.META.get("HTTP_X_ORIGINAL_URI")
        username = request.user.username
        if original_uri:
            # 根据url中的值获取repo
            org_reg = re.findall(r"orgs/(\w+)/", original_uri)
            org_sid = org_reg[0] if org_reg else None

            pt_reg = re.findall(r"teams/([-a-zA-Z0-9_]+)/", original_uri)
            pt_name = pt_reg[0] if pt_reg else None

            if org_sid and pt_name:
                project_team = ProjectTeam.objects.filter(name=pt_name, organization__org_sid=org_sid).first()
                if not project_team:
                    logger.error("[Org: %s][Team:%s] 找不到该团队，权限校验不通过" % (org_sid, pt_name))
                    return False

            repo = None
            repo_reg = re.findall(r"repos/(\d+)", original_uri)
            repo_id = int(repo_reg[0]) if repo_reg else None

            scheme_reg = re.findall(r"schemes/(\d+)", original_uri)
            scheme_id = int(scheme_reg[0]) if scheme_reg else None

            project_reg = re.findall(r"projects/(\d+)", original_uri)
            project_id = int(project_reg[0]) if project_reg else None

            if repo_id:
                repo = self.check_repo_id(repo_id, username)
                if not repo:
                    return False
            elif scheme_id:
                repo = self.check_scheme_id(scheme_id, username)
                if not repo:
                    return False
            elif project_id:
                repo = self.check_project_id(project_id, username)
                if not repo:
                    return False
            if self.check_other_server_permission(original_uri, request.user):
                return True

            # 得到repo来鉴权
            if repo:
                if request.user.has_perm(repo.PermissionNameEnum.VIEW_REPO_PERM, repo):  # 代码库成员
                    logger.info("[User: %s][Repo: %d] 代码库查看权限校验通过" % (username, repo.id))
                    return True
                elif repo.organization and request.user.has_perm(
                        Organization.PermissionNameEnum.CHANGE_ORG_PERM, repo.organization):  # 团队管理员
                    logger.info("[User: %s][Repo: %d] 团队管理员权限权限校验通过，可以查阅当前代码库" % (username, repo.id))
                    return True
                elif repo.project_team and request.user.has_perm(
                        ProjectTeam.PermissionNameEnum.VIEW_TEAM_PERM, repo.project_team):  # 项目组成员
                    logger.info("[User: %s][Repo: %d] 项目组查看权限校验通过，可以查阅当前代码库" % (username, repo.id))
                    return True
                elif request.user.is_staff and request.user.is_superuser:
                    return True
                else:
                    logger.warning("[User: %s][Repo: %d] 没有权限访问当前代码库" % (
                        username, repo.id))
                    return False
            else:
                logger.warning("[User: %s] 匹配不到代码库, Url: %s" % (username, original_uri))
                return False
        else:
            logger.error("proxy server authentication 无法取到原地址，请检查nginx配置")
            return False
