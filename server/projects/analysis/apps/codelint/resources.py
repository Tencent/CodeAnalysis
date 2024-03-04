# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
apps.codelint.resources 资源声明
"""

from django.conf import settings
from import_export import fields
from import_export import resources

from apps.base.resources import CSVResourceGeneratorMiXin
from apps.codelint import models


class IssueResource(CSVResourceGeneratorMiXin, resources.ModelResource):
    url = fields.Field()

    def dehydrate_state(self, issue):
        return dict(models.Issue.STATE_CHOICES).get(issue.state)

    def dehydrate_resolution(self, issue):
        return dict(models.Issue.RESOLUTION_CHOICES).get(issue.resolution)

    def dehydrate_severity(self, issue):
        return dict(models.Issue.SEVERITY_CHOICES).get(issue.severity)

    def dehydrate_tapd_bug_id(self, issue):
        return '已提单' if issue.tapd_bug_id else '未提单'

    def dehydrate_url(self, issue):
        return "%s/repos/%d/projects/%d/codelint/issues/%d" % (settings.LOCAL_DOMAIN, issue.project.repo_id,
                                                               issue.project_id, issue.id)

    def get_export_headers(self):
        return ['问题ID', '文件', '规则名', '规则realname', '出错信息', '状态', '处理方法',
                '负责人', '严重级别', '版本号', '项目ID', '发现版本时间', '扫描ID', '是否提单', '链接']

    class Meta:
        model = models.Issue
        fields = ('id', 'file_path', 'checkrule_display_name', 'checkrule_real_name', 'msg', 'state',
                  'resolution', 'author', 'severity', 'revision', 'project', 'ci_time', 'scan_open', 'tapd_bug_id',
                  'url')
        export_order = ('id', 'file_path', 'checkrule_display_name', 'checkrule_real_name', 'msg', 'state',
                        'resolution', 'author', 'severity', 'revision', 'project', 'ci_time', 'scan_open',
                        'tapd_bug_id', 'url')
