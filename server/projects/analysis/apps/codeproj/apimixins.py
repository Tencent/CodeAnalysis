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

import logging

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound

from apps.codeproj import models

logger = logging.getLogger(__name__)


class ProjectBaseAPIView:

    def get_repo_id(self):
        return self.kwargs["repo_id"]

    def get_project(self):
        project_id = self.kwargs["project_id"]
        logger.info("[Project: %s] find project" % project_id)
        return get_object_or_404(models.Project, id=project_id)


class ProjectTeamBaseAPIView(ProjectBaseAPIView):

    def get_repo_id(self):
        org_sid = self.kwargs["org_sid"]
        team_name = self.kwargs["team_name"]
        repo_id = self.kwargs["repo_id"]
        projects = models.Project.objects.filter(repo_id=repo_id, org_sid=org_sid, team_name=team_name)
        logger.info("[Org: %s][Team: %s][Repo: %s] find repo" % (
            org_sid, team_name, repo_id))
        if projects.count():
            return repo_id
        else:
            raise NotFound()

    def get_project(self):
        org_sid = self.kwargs["org_sid"]
        team_name = self.kwargs["team_name"]
        repo_id = self.kwargs["repo_id"]
        project_id = self.kwargs["project_id"]
        logger.info("[Org: %s][Team: %s][Repo: %s][Project: %s] find project" % (
            org_sid, team_name, repo_id, project_id))
        return get_object_or_404(models.Project, id=project_id, repo_id=repo_id, org_sid=org_sid, team_name=team_name)

    def get_project_with_kwargs(self, **kwargs):
        org_sid = kwargs["org_sid"]
        team_name = kwargs["team_name"]
        repo_id = kwargs["repo_id"]
        project_id = kwargs["project_id"]
        logger.info("[Org: %s][Team: %s][Repo: %s][Project: %s] find project" % (
            org_sid, team_name, repo_id, project_id))
        return get_object_or_404(models.Project, id=project_id, repo_id=repo_id, org_sid=org_sid, team_name=team_name)
