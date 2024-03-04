# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - scan filters
Scan Overview Filter
"""

from django_filters import rest_framework as filters

from apps.codeproj.models import Scan
from apps.codelint import models as lint_models
from apps.codemetric import models as metric_models


class ProjectOverviewLintScanFilter(filters.FilterSet):
    scan_time = filters.DateTimeFromToRangeFilter(field_name="scan__scan_time",
                                                  label="根据时间范围筛选", help_text="根据时间范围筛选")

    class Meta:
        model = lint_models.LintScan
        fields = ["scan_time"]


class ProjectOverviewCycScanFilter(filters.FilterSet):
    scan_time = filters.DateTimeFromToRangeFilter(field_name="scan__scan_time",
                                                  label="根据时间范围筛选", help_text="根据时间范围筛选")

    class Meta:
        model = metric_models.CyclomaticComplexityScan
        fields = ["scan_time"]


class ProjectOverviewDupScanFilter(filters.FilterSet):
    scan_time = filters.DateTimeFromToRangeFilter(field_name="scan__scan_time",
                                                  label="根据时间范围筛选", help_text="根据时间范围筛选")

    class Meta:
        model = metric_models.DuplicateScan
        fields = ["scan_time"]


class ProjectOverviewClocScanFilter(filters.FilterSet):
    scan_time = filters.DateTimeFromToRangeFilter(field_name="scan__scan_time",
                                                  label="根据时间范围筛选", help_text="根据时间范围筛选")

    class Meta:
        model = metric_models.ClocScan
        fields = ["scan_time"]


class ReposScanFilter(filters.FilterSet):
    class Meta:
        model = Scan
        fields = ["project_id", "state"]
