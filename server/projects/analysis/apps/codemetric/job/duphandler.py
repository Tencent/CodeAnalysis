# -*- coding:utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codemetric - duplicate result handler

"""

import os
import json
import logging

from apps.codemetric import models
from apps.codemetric.job.utils import download_and_load_json_file

from util.genkey import gen_path_key
from util.encode import encode_with_ignore

logger = logging.getLogger(__name__)


class DupResultHandler(object):
    """重复文件结果处理
    """

    def __init__(self, scan, task_result):
        """初始化函数
        """
        self._scan = scan
        self._project = scan.project
        self._task_result = task_result
        self._log_prefix = "[Duplicate][Project: %d][Scan: %d]" % (self._scan.project_id, self._scan.id)

        self._result_detail = None
        self._task_params = None
        self._result_summary = None
        self._dup_scan = None
        self._new_issue_count = 0
        self._unique_duplicate_line_count = 0
        self._dup_block_num = 0
        self._duplicate_line_count = 0
        self._diff_duplicate_block_count = 0
        self._diff_duplicate_line_count = 0
        self._close_issue_count = 0
        self._reopen_issue_count = 0
        self._ignored_issue_count = 0

    def download_result_data(self):
        """下载Duplicate结果数据
        """
        self._task_params = download_and_load_json_file(self._task_result["params_url"])
        result_data = download_and_load_json_file(self._task_result["result_data_url"])
        self._result_detail = result_data["detail"]
        self._result_summary = result_data["summary"]

    def create_dup_scan(self):
        """创建重复扫描
        """
        dup_scan, _ = models.DuplicateScan.objects.get_or_create(
            scan=self._scan, defaults={"last_revision": self._task_params.get("scm_last_revision")})
        self._dup_scan = dup_scan

    def get_issue_path_list(self):
        """获取本次上报的问题路径列表
        """
        issue_path_list = []
        for item in self._result_detail:
            if not item.get("code_blocks"):
                continue
            issue_path = "%s%s" % (self._project.id, item["path"])
            issue_path_list.append(gen_path_key(issue_path))
        return issue_path_list

    def get_exist_issues(self, issue_path_list):
        """根据问题路径列表获取已存在的问题
        """
        return list(models.DuplicateIssue.objects.filter(
            project=self._project, issue_hash__in=issue_path_list
        ).values_list("issue_hash", flat=True))

    def update_old_issue_latest_flag(self):
        """更新历史问题的is_latest 标识位
        """
        dupfile_ids = list(models.DuplicateFile.objects.filter(
            project_id=self._project.id, is_latest=True
        ).values_list("id", flat=True))
        refresh_num = models.DuplicateFile.objects.filter(id__in=dupfile_ids).update(is_latest=False)  # 标记历史数据过期了
        logger.info("%s 刷新历史重复代码文件数据，预期刷新个数: %s, 实际刷新个数: %s" % (
            self._log_prefix, len(dupfile_ids), refresh_num))

    def create_issue(self, exist_issues):
        """问题入库
        """
        dup_issue_list = []
        dup_file_list = []
        dup_issue_comment_list = []
        for item in self._result_detail:
            if not item.get("code_blocks"):
                continue
            if item.get("last_modifier"):
                item["last_modifier"] = encode_with_ignore(item["last_modifier"][:127])
            issue_path = "%s%s" % (self._project.id, item["path"])
            issue_hash = gen_path_key(issue_path)
            if issue_hash not in exist_issues:
                # 新增issue
                self._new_issue_count += 1
                dup_issue_list.append(models.DuplicateIssue(issue_hash=issue_hash,
                                                            state=models.DuplicateIssue.StateEnum.ACTIVE,
                                                            owner=item["last_modifier"],
                                                            project_id=self._project.id,
                                                            dir_path=os.path.dirname(item["path"]),
                                                            file_name=os.path.basename(item["path"]),
                                                            file_path=item["path"]))
            # 新增file
            dup_file_list.append(models.DuplicateFile(scan_id=self._dup_scan.id,
                                                      project_id=self._project.id,
                                                      issue_hash=issue_hash,
                                                      dir_path=os.path.dirname(item["path"]),
                                                      file_name=os.path.basename(item["path"]),
                                                      file_path=item["path"],
                                                      duplicate_rate=float(item["duplicate_rate"]),
                                                      total_line_count=int(item["total_line_count"]),
                                                      total_duplicate_line_count=int(
                                                          item["total_duplicate_line_count"]),
                                                      block_num=int(item["block_num"]),
                                                      last_modifier=item["last_modifier"],
                                                      change_type=item.get("change_type"),
                                                      scm_revision=self._scan.current_revision))
            self._unique_duplicate_line_count += int(item["total_duplicate_line_count"])

        last_issue = models.DuplicateIssue.objects.all().order_by("-id").first()
        last_id = last_issue.id if last_issue else 0
        models.DuplicateIssue.objects.bulk_create(dup_issue_list, 1000, ignore_conflicts=True)
        models.DuplicateFile.objects.bulk_create(dup_file_list, 1000)
        new_issues = models.DuplicateIssue.objects.filter(project_id=self._project.id, id__gt=last_id)
        for issue in new_issues:
            dup_issue_comment_list.append(models.DuplicateIssueComment(
                project_id=issue.project_id,
                issue_id=issue.id,
                action="入库新建",
                message="在%s扫描[id:%d]中发现" % (self._scan.current_revision, self._scan.id),
                creator="codedog"))
        self.create_duplicate_issue_comment(dup_issue_comment_list)

    def close_issue(self, new_hash_list):
        """关闭issue
        """
        dup_issue_comment_list = []
        close_issue_queryset = models.DuplicateIssue.objects.filter(
            project_id=self._project.id, state=models.DuplicateIssue.StateEnum.ACTIVE
        ).exclude(issue_hash__in=new_hash_list)
        for issue in close_issue_queryset:
            dup_issue_comment_list.append(models.DuplicateIssueComment(
                project_id=issue.project_id,
                issue_id=issue.id,
                action="入库关单",
                message="在%s扫描[id:%d]中关闭" % (self._scan.current_revision, self._scan.id),
                creator="codedog"))
        self.create_duplicate_issue_comment(dup_issue_comment_list)
        close_issue_count = close_issue_queryset.update(state=models.DuplicateIssue.StateEnum.CLOSED)
        logger.info("%s close dup issues num: %d" % (self._log_prefix, close_issue_count))

    def create_relation_with_issue_and_file(self, new_hash_list):
        """将file和issue关联
        """
        dup_files = models.DuplicateFile.objects.filter(scan_id=self._dup_scan.id, is_latest=True)
        dup_issues = models.DuplicateIssue.objects.filter(project_id=self._project.id, issue_hash__in=new_hash_list)
        dup_issues_dict = {}
        dup_issue_comment_list = []
        for issue in dup_issues:
            dup_issues_dict.update({issue.issue_hash: issue})
        logger.info("%s update dup issues" % self._log_prefix)
        for dup_file in dup_files:
            issue = dup_issues_dict.get(dup_file.issue_hash)
            if not issue:
                logger.info("not found: %s" % dup_file.issue_hash)
            dup_file.issue_id = issue.id
            dup_file.save()
            if issue.state == models.DuplicateIssue.StateEnum.CLOSED:
                # reopen issues
                issue.state = models.DuplicateIssue.StateEnum.ACTIVE
                issue.owner = issue.owner or dup_file.last_modifier
                issue.save()
                dup_file.save()
                dup_issue_comment_list.append(
                    models.DuplicateIssueComment(project_id=issue.project_id,
                                                 issue_id=issue.id, action="入库重新打开",
                                                 message="在%s扫描[id:%d]中重新打开" % (
                                                     self._scan.current_revision, self._scan.id),
                                                 creator="codedog")
                )
                self._reopen_issue_count += 1
            if issue.state == models.DuplicateIssue.StateEnum.IGNORED:
                self._ignored_issue_count += 1
        self.create_duplicate_issue_comment(dup_issue_comment_list)

    def create_dup_block(self):
        """创建重复块
        """
        duplicate_files = models.DuplicateFile.objects.filter(scan_id=self._dup_scan.id, is_latest=True)
        dup_block_set = []
        logger.info("%s create dup block" % self._log_prefix)
        for item in self._result_detail:
            if not item.get("code_blocks"):
                continue
            # 处理字段编码异常，采用ignore方式进行处理
            if item.get("last_modifier"):
                item["last_modifier"] = encode_with_ignore(item["last_modifier"])[:127]
            if item.get("related_modifiers"):
                item["related_modifiers"] = encode_with_ignore(item["related_modifiers"])[:510]
            duplicate_file = duplicate_files.filter(file_path=item["path"]).first()
            for code_block in item["code_blocks"]:
                code_block["last_modifier"] = encode_with_ignore(code_block["last_modifier"])[:127]
                if code_block.get("related_modifiers"):
                    code_block["related_modifiers"] = encode_with_ignore(code_block["related_modifiers"])[:510]
                dup_block_set.append(models.DuplicateBlock(project_id=self._project.id,
                                                           scan_id=self._dup_scan.id,
                                                           duplicate_file_id=duplicate_file.id,
                                                           token_num=int(code_block["token_num"]),
                                                           duplicate_times=int(code_block["duplicate_times"]),
                                                           duplicate_rate=float(code_block["duplicate_rate"]),
                                                           start_line_num=int(code_block["start_line_num"]),
                                                           end_line_num=int(code_block["end_line_num"]),
                                                           duplicate_line_count=int(
                                                               code_block["duplicate_line_count"]),
                                                           block_hash=code_block.get("block_hash"),
                                                           last_modifier=code_block["last_modifier"],
                                                           change_type=code_block.get("change_type"),
                                                           related_modifiers=code_block.get("related_modifiers"),
                                                           ))
                self._duplicate_line_count += int(code_block["duplicate_line_count"])
                if code_block.get("change_type"):
                    self._diff_duplicate_block_count += 1
                    self._diff_duplicate_line_count += int(code_block["duplicate_line_count"])

        self._dup_block_num = len(dup_block_set)
        models.DuplicateBlock.objects.bulk_create(dup_block_set, 1000)

    def create_duplicate_issue_comment(self, dup_issue_comment_list):
        """保存重复代码问题评论
        """
        models.DuplicateIssueComment.objects.bulk_create(dup_issue_comment_list, 1000)

    def save_cpd_result_summary(self, dup_file_num):
        """summary的数据格式:
        {
            "duplication_rate": "67.15",
            "default": {
                "exhi_risk": {
                "range": [0.2,1],
                "file_count": 7,
                "diff": {"diff_file_count": 6}
                },
                "high_risk": {
                "range": [0.11,0.2],
                "file_count": 1,
                "diff": {"diff_file_count": 1}
                },
                "midd_risk": {
                "range": [0.05, 0.11],
                "file_count": 0,
                "diff": {"diff_file_count": 0}
                },
                "low_risk": {
                "range": [0, 0.05],
                "file_count": 1,
                "diff": {"diff_file_count": 1}
                }
            }
        }
        """
        self._dup_scan.duplicate_file_count = dup_file_num
        self._dup_scan.duplicate_block_count = self._dup_block_num
        self._dup_scan.duplicate_line_count = self._duplicate_line_count
        self._dup_scan.unique_duplicate_line_count = self._unique_duplicate_line_count
        self._dup_scan.diff_duplicate_block_count = self._diff_duplicate_block_count
        self._dup_scan.diff_duplicate_line_count = self._diff_duplicate_line_count
        self._dup_scan.close_issue_count = self._close_issue_count
        self._dup_scan.new_issue_count = self._new_issue_count
        self._dup_scan.reopen_issue_count = self._reopen_issue_count
        self._dup_scan.ignored_issue_count = self._ignored_issue_count
        self._dup_scan.duplicate_rate = self._result_summary["duplication_rate"]
        self._dup_scan.total_duplicate_line_count = self._result_summary["total_duplicate_line_count"]
        self._dup_scan.total_line_count = self._result_summary["total_line_count"]
        self._dup_scan.default_summary = json.dumps(self._result_summary["default"])
        self._dup_scan.custom_summary = json.dumps(self._result_summary.get('custom'))
        self._dup_scan.save()

    def handle(self):
        """cpd的result["result_data"]  - result_data格式：
        [{
            "file_path":"path/to/file.py",
            "block_num": 5,
            "total_duplicate_line_count": 22, //所有重复代码行的总行数（需去重）
            "total_line_count": 1331,
            "duplicate_rate": 80.3,
            "change_type": "add",
            "last_modifier": "xxx",
            "code_blocks":[
                {
                "start_line_num": 23,
                "end_line_num": 1310,
                "change_type": "add",
                "duplicate_times": 2,
                "duplicate_line_count": 1287,
                "duplicate_rate": 80.3,
                "token_num": 6876,
                "last_modifier": "xxx"
                },
                ...
            ]
        },...
        ]
        """
        logger.info("%s 处理重复代码结果数据入库" % self._log_prefix)
        self.download_result_data()
        issue_path_list = self.get_issue_path_list()
        self.create_dup_scan()
        exist_issues = self.get_exist_issues(issue_path_list)
        self.update_old_issue_latest_flag()
        self.create_issue(exist_issues)
        self.close_issue(issue_path_list)
        self.create_relation_with_issue_and_file(issue_path_list)
        self.create_dup_block()
        self.save_cpd_result_summary(len(issue_path_list))
