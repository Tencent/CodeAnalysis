# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
apps.codemetric.core.codecountmgr
CodeCount core logic
"""

from django.db.models import Sum


class ClocDirFileManager(object):
    """目录文件代码统计管理
    """

    @classmethod
    def filter_cloc_dirs_by_project_id_and_path(cls, cloc_dir_model, project_id, path):
        """通过项目编号和指定路径筛选目录代码数据
        :param cloc_dir_model: Model
        :param project_id: int，项目编号
        :param path: str，路径
        :return: QuerySet
        """
        cloc_dirs = cloc_dir_model.objects.filter(
            project_id=int(project_id), is_latest=True, parent_path=path
        ).order_by("dir_path")
        return cloc_dirs

    @classmethod
    def filter_cloc_files_by_project_id_and_path(cls, cloc_file_model, project_id, path):
        """通过项目编号和指定路径筛选文件代码数据
        :param cloc_file_model: Model
        :param project_id: int，项目编号
        :param path: str，路径
        :return: QuerySet
        """
        cloc_files = cloc_file_model.objects.filter(
            project_id=int(project_id), is_latest=True, dir_path=path
        ).order_by("file_name")
        return cloc_files

    @classmethod
    def get_cloc_dir_sum_by_project_id_and_path(cls, clocl_dir_model, project_id, start_path):
        """通过项目编号和指定起始路径筛选目录代码累计数据
        :param clocl_dir_model: Model
        :param project_id: int，项目编号
        :param start_path: 路径
        :return: QuerySet
        """
        cloc_dirs = clocl_dir_model.objects.filter(
            project_id=int(project_id), is_latest=True, dir_path=start_path)
        cloc_dir_sum = cloc_dirs.aggregate(
            Sum("code_line_num"), Sum("comment_line_num"),
            Sum("blank_line_num"), Sum("total_line_num"),
            Sum("add_code_line_num"), Sum("add_comment_line_num"),
            Sum("add_blank_line_num"), Sum("add_total_line_num"),
            Sum("mod_code_line_num"), Sum("mod_comment_line_num"),
            Sum("mod_blank_line_num"), Sum("mod_total_line_num"),
            Sum("del_code_line_num"), Sum("del_comment_line_num"),
            Sum("del_blank_line_num"), Sum("del_total_line_num"))
        return cloc_dir_sum
