# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - apimixins
项目模块API基础类
"""

from django.shortcuts import get_object_or_404

from apps.codeproj import models


class ProjectBaseAPIView:
    """分析任务基础操作
    """

    def get_repo(self):
        repo_id = self.kwargs["repo_id"]
        return get_object_or_404(models.Repository, id=repo_id)

    def get_project(self):
        project_id = self.kwargs["project_id"]
        if self.kwargs.get("repo_id"):
            repo_id = self.kwargs["repo_id"]
            return get_object_or_404(models.Project, id=project_id, repo_id=repo_id)
        else:
            return get_object_or_404(models.Project, id=project_id)

    def get_scan_scheme(self):
        repo_id = self.kwargs["repo_id"]
        scheme_id = self.kwargs["scheme_id"]
        return get_object_or_404(models.ScanScheme.user_objects(self.request.user), id=scheme_id, repo_id=repo_id)


class ProjectTeamBaseAPIView(ProjectBaseAPIView):
    """项目基础操作
    """

    def get_project_team(self):
        org_sid = self.kwargs["org_sid"]
        team_name = self.kwargs["team_name"]
        return get_object_or_404(models.ProjectTeam, organization__org_sid=org_sid, name=team_name)

    def get_repo(self):
        org_sid = self.kwargs["org_sid"]
        team_name = self.kwargs["team_name"]
        repo_id = self.kwargs["repo_id"]
        return get_object_or_404(
            models.Repository, id=repo_id, project_team__name=team_name, organization__org_sid=org_sid)

    def get_scan_scheme(self):
        repo = self.get_repo()
        scheme_id = self.kwargs["scheme_id"]
        return get_object_or_404(models.ScanScheme, id=scheme_id, repo=repo)

    def get_project(self):
        repo = self.get_repo()
        project_id = self.kwargs["project_id"]
        return get_object_or_404(models.Project, id=project_id, repo=repo)
