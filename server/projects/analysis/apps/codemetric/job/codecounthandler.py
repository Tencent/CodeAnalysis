# -*- coding:utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codemetric - codecount result handler

"""
import os
import logging
from collections import namedtuple

from apps.codemetric import models
from .utils import download_and_load_json_file

logger = logging.getLogger(__name__)


class CodeCountResultHandler(object):
    """CodeCount结果处理
    """

    def __init__(self, scan, task_result):
        """初始化函数
        """
        self._scan = scan
        self._project = scan.project
        self._task_result = task_result
        self._log_prefix = "[CodeCount][Project: %d][Scan: %d]" % (self._scan.project_id, self._scan.id)
        self._task_params = None
        self._result_data = None
        self._codecount_tuple = None
        self._cloc_scan = None

    def _get_codecount_fields(self, codecount_tuple):
        """获取代码统计fields
        """
        return {
            "code_line_num": codecount_tuple.code_line_num,
            "comment_line_num": codecount_tuple.comment_line_num,
            "blank_line_num": codecount_tuple.blank_line_num,
            "total_line_num": codecount_tuple.total_line_num,

            "add_code_line_num": codecount_tuple.add_code_line_num,
            "add_comment_line_num": codecount_tuple.add_comment_line_num,
            "add_blank_line_num": codecount_tuple.add_blank_line_num,
            "add_total_line_num": codecount_tuple.add_total_line_num,

            "mod_code_line_num": codecount_tuple.mod_code_line_num,
            "mod_comment_line_num": codecount_tuple.mod_comment_line_num,
            "mod_blank_line_num": codecount_tuple.mod_blank_line_num,
            "mod_total_line_num": codecount_tuple.mod_total_line_num,

            "del_code_line_num": codecount_tuple.del_code_line_num,
            "del_comment_line_num": codecount_tuple.del_comment_line_num,
            "del_blank_line_num": codecount_tuple.del_blank_line_num,
            "del_total_line_num": codecount_tuple.del_total_line_num,
        }

    def download_result_data(self):
        """下载codecount结果数据
        """
        self._task_params = download_and_load_json_file(self._task_result["params_url"])
        self._result_data = download_and_load_json_file(self._task_result["result_data_url"])

    def init_handler(self):
        """初始化处理器
        """
        self._codecount_tuple = namedtuple("CodeCountTuple", self._result_data["cloc_tuple_definition"])

    def create_codecount_scan(self):
        """创建codecount scan
        """
        cloc_scan, _ = models.ClocScan.objects.get_or_create(scan=self._scan, defaults={
            "last_revision": self._task_params.get("scm_last_revision")})
        self._cloc_scan = cloc_scan

    def reset_codecount_file_latest_flag(self):
        """reset codecount file
        """
        models.ClocFile.objects.filter(project_id=self._project.id, is_latest=True).update(is_latest=False)

    def add_codecount_file(self):
        """计算codecount文件
        """
        codecount_file_list = []
        total_code_line_num = 0
        total_comment_line_num = 0
        total_blank_line_num = 0
        total_total_line_num = 0
        total_add_code_line_num = 0
        total_add_comment_line_num = 0
        total_add_blank_line_num = 0
        total_add_total_line_num = 0
        total_mod_code_line_num = 0
        total_mod_comment_line_num = 0
        total_mod_blank_line_num = 0
        total_mod_total_line_num = 0
        total_del_code_line_num = 0
        total_del_comment_line_num = 0
        total_del_blank_line_num = 0
        total_del_total_line_num = 0
        for file_path, item in self._result_data["files"].items():
            codecount_tuple = self._codecount_tuple(*item["cloc_tuple"])
            codecount_file_list.append(models.ClocFile(
                project_id=self._project.id,
                scan_id=self._cloc_scan.id,
                dir_path=os.path.dirname(file_path),
                file_name=os.path.basename(file_path),
                language=item["language"],
                change_type=item.get("change_type", None),

                **self._get_codecount_fields(codecount_tuple)
            ))
            total_code_line_num += codecount_tuple.code_line_num
            total_comment_line_num += codecount_tuple.comment_line_num
            total_blank_line_num += codecount_tuple.blank_line_num
            total_total_line_num += codecount_tuple.total_line_num

            total_add_code_line_num += codecount_tuple.add_code_line_num
            total_add_comment_line_num += codecount_tuple.add_comment_line_num
            total_add_blank_line_num += codecount_tuple.add_blank_line_num
            total_add_total_line_num += codecount_tuple.add_total_line_num

            total_mod_code_line_num += codecount_tuple.mod_code_line_num
            total_mod_comment_line_num += codecount_tuple.mod_comment_line_num
            total_mod_blank_line_num += codecount_tuple.mod_blank_line_num
            total_mod_total_line_num += codecount_tuple.mod_total_line_num

            total_del_code_line_num += codecount_tuple.del_code_line_num
            total_del_comment_line_num += codecount_tuple.del_comment_line_num
            total_del_blank_line_num += codecount_tuple.del_blank_line_num
            total_del_total_line_num += codecount_tuple.del_total_line_num

        self.reset_codecount_file_latest_flag()
        models.ClocFile.objects.bulk_create(codecount_file_list, 1000)

        self._cloc_scan.code_line_num = total_code_line_num
        self._cloc_scan.comment_line_num = total_comment_line_num
        self._cloc_scan.blank_line_num = total_blank_line_num
        self._cloc_scan.total_line_num = total_total_line_num

        self._cloc_scan.add_code_line_num = total_add_code_line_num
        self._cloc_scan.add_comment_line_num = total_add_comment_line_num
        self._cloc_scan.add_blank_line_num = total_add_blank_line_num
        self._cloc_scan.add_total_line_num = total_add_total_line_num

        self._cloc_scan.mod_code_line_num = total_mod_code_line_num
        self._cloc_scan.mod_comment_line_num = total_mod_comment_line_num
        self._cloc_scan.mod_blank_line_num = total_mod_blank_line_num
        self._cloc_scan.mod_total_line_num = total_mod_total_line_num

        self._cloc_scan.del_code_line_num = total_del_code_line_num
        self._cloc_scan.del_comment_line_num = total_del_comment_line_num
        self._cloc_scan.del_blank_line_num = total_del_blank_line_num
        self._cloc_scan.del_total_line_num = total_del_total_line_num
        self._cloc_scan.save()

    def reset_codecount_dir_latest_flag(self):
        """reset codecount dir
        """
        models.ClocDir.objects.filter(project_id=self._project.id, is_latest=True).update(is_latest=False)

    def add_codecount_dir(self):
        """计算cloc目录
        """
        codecount_dir_list = []
        for dir_path, item in self._result_data["dirs"].items():
            codecount_tuple = self._codecount_tuple(*item["cloc_tuple"])
            codecount_dir_list.append(models.ClocDir(
                project_id=self._project.id,
                scan_id=self._cloc_scan.id,
                dir_path=dir_path,
                parent_path=os.path.dirname(dir_path),
                file_num=int(item["file_num"]),

                **self._get_codecount_fields(codecount_tuple)
            ))
        self.reset_codecount_dir_latest_flag()
        models.ClocDir.objects.bulk_create(codecount_dir_list, 1000)

    def reset_codecount_lang_latest_flag(self):
        """reset codecount lang
        """
        models.ClocLanguage.objects.filter(project_id=self._project.id, is_latest=True).update(is_latest=False)

    def add_codecount_language(self):
        """计算codecount语言
        """
        codecount_language_list = []
        for name, item in self._result_data["langs"].items():
            codecount_tuple = self._codecount_tuple(*item["cloc_tuple"])
            codecount_language_list.append(models.ClocLanguage(
                project_id=self._project.id,
                scan_id=self._cloc_scan.id,
                name=name,
                file_num=int(item["file_num"]),

                **self._get_codecount_fields(codecount_tuple)
            ))
        self.reset_codecount_lang_latest_flag()
        models.ClocLanguage.objects.bulk_create(codecount_language_list, 1000, ignore_conflicts=True)

    def handle(self):
        """处理函数
        """
        self.download_result_data()
        self.init_handler()
        self.create_codecount_scan()
        self.add_codecount_file()
        self.add_codecount_dir()
        self.add_codecount_language()
