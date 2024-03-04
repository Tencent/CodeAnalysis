# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
apps.codemetric.resources 资源声明
"""

from django.conf import settings
from import_export import fields
from import_export import resources

from apps.base.resources import CSVResourceGeneratorMiXin
from apps.codemetric import models


class CCIssueResource(CSVResourceGeneratorMiXin, resources.ModelResource):
    """圈复杂度导出信息
    """
    url = fields.Field()

    def dehydrate_status(self, ccissue):
        return dict(models.CyclomaticComplexity.STATUS_CHOICES_DICT).get(ccissue.status)

    def dehydrate_url(self, ccissue):
        return "%s/repos/%d/projects/%d/codemetric/ccissues/%d" % (
            settings.LOCAL_DOMAIN, ccissue.project.repo_id, ccissue.project_id, ccissue.id)

    def get_export_headers(self):
        return ['问题ID', '文件', '函数名称', '函数长名称', '圈复杂度', '函数参数个数',
                '状态', '最近修改人', '相关修改人', '负责人', '项目ID', '扫描ID', '链接']

    class Meta:
        model = models.CyclomaticComplexity
        fields = ('id', 'file_path', 'func_name', 'long_name', 'ccn', 'func_param_num',
                  'status', 'last_modifier', 'related_modifiers', 'author',
                  'project', 'scan_open', 'url')
        export_order = ('id', 'file_path', 'func_name', 'long_name', 'ccn', 'func_param_num',
                        'status', 'last_modifier', 'related_modifiers', 'author',
                        'project', 'scan_open', 'url')


class DupFileResource(CSVResourceGeneratorMiXin, resources.ModelResource):
    """重复代码
    """
    url = fields.Field()
    owner = fields.Field()
    state = fields.Field()

    def dehydrate_state(self, dup_file):
        return dict(models.DuplicateIssue.STATE_CHOICES_DICT).get(dup_file.issue.state)

    def dehydrate_owner(self, dup_file):
        return dict(models.DuplicateIssue.STATE_CHOICES_DICT).get(dup_file.issue.owner)

    def dehydrate_url(self, dup_file):
        return "%s/repos/%d/projects/%d/codemetric/dupfiles/%d" % (
            settings.LOCAL_DOMAIN, dup_file.project.repo_id, dup_file.project_id, dup_file.id)

    def get_export_headers(self):
        return ['问题ID', '文件路径', '文件名', '重复率', '总行数', '总重复行数',
                '重复代码块数（去重）', '重复代码块数', '最近修改人', '更改类型',
                '负责人', '版本号', '状态', '项目ID', '扫描ID', '链接']

    class Meta:
        model = models.DuplicateFile
        fields = ('id', 'file_path', 'file_name', 'duplicate_rate', 'total_line_count', 'total_duplicate_line_count',
                  'block_num', 'last_modifier', 'change_type', 'owner', 'scm_revision', 'state',
                  'project', 'scan', 'url')
        export_order = ('id', 'file_path', 'file_name', 'duplicate_rate', 'total_line_count',
                        'total_duplicate_line_count', 'block_num', 'last_modifier',
                        'change_type', 'owner', 'scm_revision', 'state', 'project', 'scan', 'url')
