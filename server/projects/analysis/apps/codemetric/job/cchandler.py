# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codemetric - cc result handler
"""

import json
import logging
import os
import time

from apps.codemetric import models
from apps.codemetric.job.utils import download_and_load_json_file, download_and_unzip_file, grouper, \
    yield_issue_from_files
from util.encode import encode_with_ignore

logger = logging.getLogger(__name__)


class CCResultHandler(object):
    """圈复杂度结果处理器
    """

    def __init__(self, scan, task_result):
        """初始化函数
        """
        self._scan = scan
        self._project = scan.project
        self._task_result = task_result
        self._log_prefix = "[CC][Project: %d][Scan: %d]" % (self._scan.project_id, self._scan.id)

        self._cc_scan = None
        self._task_params = None
        self._result_data = None
        self._result_data_path = None
        self._incr_scan_flag = None

    def _handle_data_encode(self, data):
        """处理指定字段的编码格式
        """
        target_fields = ["modifier", "last_modifier", "related_modifiers", "most_weight_modifier",
                         "most_weight_modifier_email", "weight_modifiers"]
        for field in target_fields:
            if data.get(field):
                data[field] = encode_with_ignore(data[field])
        return data

    def download_result_data(self):
        """下载结果数据
        """
        logger.debug("%s dowload task params file: %s" % (self._log_prefix, self._task_result["params_url"]))
        self._task_params = download_and_load_json_file(self._task_result["params_url"])

        logger.debug("%s dowload result_data file: %s" % (self._log_prefix, self._task_result["result_data_url"]))
        dir_path, _ = download_and_unzip_file(self._task_result["result_data_url"])
        self._result_data_path = os.path.join(dir_path, "issue_dir")
        if not os.path.exists(self._result_data_path):
            self._result_data_path = os.path.join(dir_path, "tmp_dir")
        with open(os.path.join(self._result_data_path, "report.json")) as f:
            self._result_data = json.loads(f.read())
            logger.info("%s result data overview：" % self._log_prefix)
            logger.info(json.dumps(self._result_data))

    def init_handler(self):
        """初始化处理器
        """
        self._incr_scan_flag = self.get_incr_scan_flag()

    def get_incr_scan_flag(self):
        """判断当前扫描是否为增量扫描
        """
        if self._result_data.get("incr_scan") is not None:
            logger.info("通过结果数据获取incr_scan标识")
            return self._result_data.get("incr_scan") is True
        else:
            logger.info("通过任务参数获取incr_scan标识")
            return self._task_params.get("incr_scan") is True

    def create_cc_scan(self):
        """创建cc扫描
        """
        cc_scan, _ = models.CyclomaticComplexityScan.objects.get_or_create(scan=self._scan, defaults={
            "last_revision": self._task_params.get("scm_last_revision")})
        self._cc_scan = cc_scan
        logger.info("%s relate cc scan: %s" % (self._log_prefix, self._cc_scan.id))

    def reset_ccfile_and_cc(self):
        """重置cc问题
        """
        reset_file_num = models.CyclomaticComplexityFile.objects.filter(project=self._project,
                                                                        scan_close__isnull=True).update(
            change_type=models.CyclomaticComplexityFile.ChangeTypeEnum.DEFAULT,
            diff_over_func_cc=0, diff_over_cc_sum=0, diff_over_cc_avg=0, diff_over_cc_func_count=0, worse=False
        )
        logger.info("%s reset unclosed cc file latest flag: %s" % (self._log_prefix, reset_file_num))
        reset_cc_ids = list(models.CyclomaticComplexity.everything.filter(
            project=self._project, is_latest=True).values_list("id", flat=True))
        reset_cc_num = 0
        for reset_cc_ids_chunk in grouper(reset_cc_ids, 1000):
            reset_cc_num += models.CyclomaticComplexity.everything.filter(id__in=reset_cc_ids_chunk).update(
                change_type=models.CyclomaticComplexity.ChangeTypeEnum.DEFAULT)
        logger.info("%s reset unclosed cc latest flag: %s" % (self._log_prefix, reset_cc_num))

    def read_cc_issue_data(self, callback=None, batch_size=100, **kwargs):
        """从多个结果文件逐行读取issue，然后批量入库
        执行逻辑:
            1. 逐行读取issue
            2. 判断当前行是否为文件，如果为文件：
                2.1 读取问题数量
                2.2 存储上一个文件问题数据到文件问题列表
                2.3 判断当前文件列表数量是否超过阈值，超过则入库，并重置文件问题列表为空
                2.4 添加当前问题文件
            3. 当前行为具体问题时，添加到当前问题文件中
        """
        logger.info("%s start reading cc issue data and save" % self._log_prefix)

        file_hash_list = []
        path_issue_list = []
        path_issue = {}
        path_issue_count = 0
        file_count = 0
        incr_scan = self._incr_scan_flag

        for issue in yield_issue_from_files(
                self._result_data_path, self._result_data["issue_detail_paths"]):
            if issue.get("file_hash"):
                file_hash_list.append(issue["file_hash"])
                if path_issue:
                    path_issue_list.append(path_issue)
                    if len(path_issue_list) >= batch_size:
                        logger.debug("%s file issue reach size: %s" % (self._log_prefix, batch_size))
                        if callback:
                            callback(path_issue_list, incr_scan=incr_scan, **kwargs)
                        path_issue_list = []

                file_count += 1
                path_issue_count = issue.get("issues_cnt") or 0
                logger.debug("%s read %s file issues[num: %s]: %s" % (
                    self._log_prefix, file_count, path_issue_count, issue["path"]))
                path_issue = {"path": issue, "issues": []}
            elif path_issue_count > 0:
                path_issue["issues"].append(issue)
                path_issue_count -= 1
            else:
                logger.error("%s current issue can not related file: %s" % (self._log_prefix, issue))

        if path_issue:
            path_issue_list.append(path_issue)
        if path_issue_list:
            if callback:
                callback(path_issue_list, incr_scan=incr_scan, **kwargs)
        return file_hash_list

    def save_cc_issue_data(self, path_issues, incr_scan=False, **kwargs):
        """存储Lizard数据
        """
        logger.info("%s start saving cc issue data" % self._log_prefix)
        file_hash_list = []
        new_cc_files = {}
        no_issue_file = {}
        new_ccs = []
        new_cc_details = []
        path_issue_num = len(path_issues)
        # 存储数据
        for idx, item in enumerate(path_issues):
            path_info = item["path"]
            raw_issues = item.get("issues", [])
            file_path = path_info["path"][:512]
            file_hash = path_info["file_hash"]
            file_hash_list.append(file_hash)
            change_type = models.CyclomaticComplexityFile.CHANGEDTYPE_MAP.get(path_info.get("change_type")) or \
                          models.CyclomaticComplexityFile.ChangeTypeEnum.DEFAULT
            scan_close, state = (self._cc_scan, models.CyclomaticComplexityFile.StateEnum.CLOSED) if not raw_issues \
                else (None, models.CyclomaticComplexityFile.StateEnum.ACTIVE)
            logger.info("%s[CCFile: %d/%d] start to save cc file detail: %s" % (
                self._log_prefix, idx + 1, path_issue_num, file_path))
            # 处理指定字段的编码问题
            path_info = self._handle_data_encode(path_info)
            file_owners = path_info.get("owners")
            if isinstance(file_owners, list):
                file_owners = ";".join(file_owners)
            if file_owners:
                file_owners = file_owners[:250]
            if path_info.get("ci_time"):
                file_ci_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(path_info["ci_time"]))
            else:
                file_ci_time = None

            new_cc_file = models.CyclomaticComplexityFile(
                project=self._project,
                file_hash=file_hash,
                file_path=file_path,
                over_func_cc=path_info.get("over_func_cc", 0),
                over_cc_sum=path_info.get("over_cc_sum", 0),
                over_cc_avg=path_info.get("over_cc_avg", 0),
                over_cc_func_count=path_info.get("over_cc_func_count", 0),
                language=path_info.get("language"),
                diff_over_func_cc=path_info.get("diff_over_func_cc", 0),
                diff_over_cc_sum=path_info.get("diff_over_cc_sum", 0),
                diff_over_cc_avg=path_info.get("diff_over_cc_avg", 0),
                diff_over_cc_func_count=path_info.get("diff_over_cc_func_count", 0),
                worse=path_info.get("worse", False),
                g_file_hash=path_info["g_file_hash"],
                state=state,
                change_type=change_type,
                scan_close=scan_close,
                scan_open=self._cc_scan,
                file_owners=file_owners,
                revision=path_info.get("revision"),
                ci_time=file_ci_time,
                last_modifier=path_info.get("last_modifier", "")[:16],
                related_modifiers=path_info.get("related_modifiers", "")[:256],
                most_weight_modifier=path_info.get("most_weight_modifier", ""),
                most_weight_modifier_email=path_info.get("most_weight_modifier_email", ""),
                weight_modifiers=path_info.get("weight_modifiers", ""),
            )
            # 增加文件数据
            if raw_issues:
                new_cc_files[file_hash] = new_cc_file
            else:
                no_issue_file[file_hash] = new_cc_file
            for raw_issue in raw_issues:
                change_type = models.CyclomaticComplexity.CHANGEDTYPE_MAP.get(raw_issue.get("change_type")) or \
                              models.CyclomaticComplexity.ChangeTypeEnum.DEFAULT
                # 处理指定字段编码异常，采用ignore方式进行处理
                raw_issue = self._handle_data_encode(raw_issue)
                if raw_issue.get("ci_time"):
                    cc_ci_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(raw_issue.get("ci_time")))
                else:
                    cc_ci_time = None

                cc = models.CyclomaticComplexity(
                    project=self._project,
                    ccn=raw_issue["ccn"],
                    file_path=file_path,
                    file_hash=file_hash,
                    func_name=raw_issue["func_name"][:512],
                    func_param_num=raw_issue["func_param_num"],
                    long_name=raw_issue["long_name"][:1024],
                    change_type=change_type,
                    last_modifier=raw_issue["modifier"][:16],
                    related_modifiers=raw_issue["related_modifiers"][:256],
                    language=path_info.get("language"),
                    revision=raw_issue.get("revision"),
                    ci_time=cc_ci_time,
                    diff_ccn=raw_issue.get("diff_ccn"),
                    scan_open=self._cc_scan,
                    is_latest=True,
                    most_weight_modifier=raw_issue.get("most_weight_modifier", ""),
                    most_weight_modifier_email=raw_issue.get("most_weight_modifier_email", ""),
                    weight_modifiers=raw_issue.get("weight_modifiers", ""),
                    token=raw_issue["token"],
                    line_num=raw_issue["line_num"],
                    code_line_num=raw_issue["code_line_num"],
                    scan_revision=self._cc_scan.scan.current_revision,
                    start_line_no=raw_issue["start_line_no"],
                    end_line_no=raw_issue["end_line_no"]
                )
                new_ccs.append(cc)

        no_issue_cc_file_ids = list(models.CyclomaticComplexityFile.objects.filter(
            project=self._project, file_hash__in=list(no_issue_file.keys())).values_list("id", flat=True))
        logger.info("%s 批量关闭已存在的issue文件结果: %s" % (self._log_prefix, len(no_issue_cc_file_ids)))
        models.CyclomaticComplexityFile.objects.filter(id__in=no_issue_cc_file_ids).update(
            scan_close=self._cc_scan, state=models.CyclomaticComplexityFile.StateEnum.CLOSED,
            over_cc_sum=0, over_cc_avg=0, over_cc_func_count=0, over_func_cc=0
        )
        origin_cc_files = list(models.CyclomaticComplexityFile.objects.filter(
            project=self._project, file_hash__in=list(new_cc_files.keys())))
        logger.info("%s 批量更新已存在的issue文件结果: %s" % (self._log_prefix, len(origin_cc_files)))
        for cc_file in origin_cc_files:
            new_cc_file = new_cc_files[cc_file.file_hash]
            cc_file.over_func_cc = new_cc_file.over_func_cc
            cc_file.over_cc_sum = new_cc_file.over_cc_sum
            cc_file.over_cc_avg = new_cc_file.over_cc_avg
            cc_file.over_cc_func_count = new_cc_file.over_cc_func_count
            cc_file.diff_over_func_cc = new_cc_file.diff_over_func_cc
            cc_file.diff_over_cc_sum = new_cc_file.diff_over_cc_sum
            cc_file.diff_over_cc_avg = new_cc_file.diff_over_cc_avg
            cc_file.diff_over_cc_func_count = new_cc_file.diff_over_cc_func_count
            cc_file.worse = new_cc_file.worse
            cc_file.change_type = new_cc_file.change_type
            cc_file.state = new_cc_file.state
            cc_file.language = cc_file.language
            cc_file.scan_close = new_cc_file.scan_close
            cc_file.file_owners = new_cc_file.file_owners
            cc_file.last_modifier = new_cc_file.last_modifier
            cc_file.related_modifiers = new_cc_file.related_modifiers
            cc_file.most_weight_modifier = new_cc_file.most_weight_modifier
            cc_file.most_weight_modifier_email = new_cc_file.most_weight_modifier_email
            cc_file.weight_modifiers = new_cc_file.weight_modifiers

        # 批量更新已创建的
        models.CyclomaticComplexityFile.objects.bulk_update(
            origin_cc_files,
            ["change_type", "state", "over_func_cc", "over_cc_sum", "over_cc_avg", "over_cc_func_count", "language",
             "diff_over_func_cc", "diff_over_cc_sum", "diff_over_cc_avg", "diff_over_cc_func_count", "worse",
             "scan_close", "file_owners", "last_modifier", "related_modifiers", "most_weight_modifier",
             "most_weight_modifier_email", "weight_modifiers"]
        )
        new_cc_files = list(new_cc_files.values())
        # 批量创建
        logger.info("%s 批量创建issue文件数据: %s(去重后: %s)" % (
            self._log_prefix, len(new_cc_files), len(new_cc_files) - len(origin_cc_files)))
        models.CyclomaticComplexityFile.objects.bulk_create(new_cc_files, batch_size=1000, ignore_conflicts=True)
        logger.info("%s 批量创建issue问题数据: %s" % (self._log_prefix, len(new_ccs)))
        models.CyclomaticComplexity.objects.bulk_create(new_ccs, batch_size=1000, ignore_conflicts=True)
        logger.info("%s 批量创建issue详情数据: %s" % (self._log_prefix, len(new_cc_details)))

        # 增量扫描：批量刷新存量问题
        #   - Add和Mod文件包含的问题全部设置为latest=True
        #   - 变更文件且无问题的文件包含的问题全部设置为 latest=False
        #   - 无变更文件不刷新
        if incr_scan is True:
            logger.info("%s 刷新最新的圈复杂度latest标识位" % self._log_prefix)
            # 获取目标文件中非本次扫描且latest=True的问题编号
            cc_ids = list(models.CyclomaticComplexity.everything.filter(
                project=self._project,
                is_latest=True,
                file_hash__in=file_hash_list
            ).exclude(
                scan_open=self._cc_scan
            ).values_list("id", flat=True))
            models.CyclomaticComplexity.everything.filter(id__in=cc_ids).update(is_latest=False)

    def update_old_cc_latest(self, active_cc_file_hash_list):
        """刷新旧圈复杂度文件
        """
        logger.info("%s 刷新最新的issue id" % self._log_prefix)
        if self._incr_scan_flag is True:
            logger.info("%s 增量扫描，不刷新数据" % self._log_prefix)
            return

        # 处理旧扫描中问题的is_latest值
        cc_ids = list(models.CyclomaticComplexity.everything.filter(project=self._project, is_latest=True).exclude(
            scan_open=self._cc_scan).values_list("id", flat=True))
        update_cc_num = 0
        # 分批刷新
        for update_cc_ids_chunk in grouper(cc_ids, 1000):
            update_cc_num += models.CyclomaticComplexity.everything.filter(
                id__in=update_cc_ids_chunk).update(is_latest=False)
        logger.info("%s 全量扫描，非本次扫描发现的问题全部设置 latest=False，数量为%s" % (
            self._log_prefix, update_cc_num))

        # 筛选非本次扫描上报的文件编号，进行关闭
        cc_file_ids = list(models.CyclomaticComplexityFile.objects.filter(
            project=self._project.id,
            state=models.CyclomaticComplexityFile.StateEnum.ACTIVE
        ).exclude(
            file_hash__in=active_cc_file_hash_list
        ).values_list("id", flat=True))
        closed_cnt = models.CyclomaticComplexityFile.objects.filter(
            id__in=cc_file_ids
        ).update(
            state=models.CyclomaticComplexityFile.StateEnum.CLOSED,
            over_cc_sum=0, over_cc_avg=0, over_cc_func_count=0, over_func_cc=0
        )
        logger.info("%s 全量扫描，将不在本次上报列表的文件关闭，关闭数量为%s" % (self._log_prefix, closed_cnt))

        scan_closed_cnt = models.CyclomaticComplexityFile.objects.filter(
            id__in=cc_file_ids,
            state=models.CyclomaticComplexityFile.StateEnum.CLOSED,
            scan_close__isnull=True
        ).update(
            scan_close=self._cc_scan
        )
        logger.info("%s 全量扫描，刷新状态为已关闭但scan_close为Null的问题，关闭数量为%s" % (
            self._log_prefix, scan_closed_cnt))

    def save_cc_scan_worse_file_num(self):
        """保存当前扫描恶化文件数
        """
        self._cc_scan.worse_cc_file_num = models.CyclomaticComplexityFile.objects.filter(
            project=self._project, worse=True).count()
        self._cc_scan.save()

    def read_cc_person_data(self):
        """从多个结果文件读取person数据，然后批量入库
        """
        person_paths = self._result_data.get("person_paths", [])
        if not person_paths:
            return
        logger.info("%s 待入库的人员圈复杂度统计文件数: %s" % (self._log_prefix, len(person_paths)))
        person_data_list = []
        for person_data in yield_issue_from_files(self._result_data_path, person_paths):
            person_data_list.append(person_data)
        self.save_cc_person_data(person_data_list)

    def save_cc_person_data(self, person_datas):
        """保存圈复杂度人员数据
        """
        cc_persons = []
        for person_data in person_datas:
            author = encode_with_ignore(person_data["author"])
            author_email = encode_with_ignore(person_data["author_email"])

            cc_persons.append(models.PersonCyclomaticComplexity(
                project=self._project, scan=self._cc_scan, author=author, author_email=author_email,
                over_cc_func_count=person_data.get("over_cc_func_count"),
                over_cc_sum=person_data.get("over_cc_sum")
            ))
        models.PersonCyclomaticComplexity.objects.bulk_create(cc_persons, batch_size=1000, ignore_conflicts=True)

    def save_cc_result_summary(self):
        """summary的数据格式
        """
        logger.info("%s start saving cc result summary" % self._log_prefix)
        summary = self._result_data["summary"]
        # 如果存在custom，则优先取custom
        if summary.get("custom"):
            self._cc_scan.diff_cc_num = summary["custom"].get("diff_over_cc_func_count", 0)
            self._cc_scan.cc_average_of_lines = summary["custom"].get("cc_average_of_lines", 0)

        else:
            self._cc_scan.diff_cc_num = summary["default"].get("diff_over_cc_func_count", 0)
            self._cc_scan.cc_average_of_lines = summary["default"].get("cc_average_of_lines", 0)
        # 计算总和
        self._cc_scan.default_summary = json.dumps(summary["default"])
        self._cc_scan.custom_summary = json.dumps(summary.get("custom"))
        self._cc_scan.min_ccn = self._task_params.get("min_ccn", 20)
        self._cc_scan.cc_open_num = self._result_data["issue_count"]
        self._cc_scan.save()

    def handle(self):
        """处理函数
        """
        self.download_result_data()
        self.init_handler()
        self.create_cc_scan()
        self.reset_ccfile_and_cc()
        active_cc_file_hash_list = self.read_cc_issue_data(callback=self.save_cc_issue_data)
        self.save_cc_scan_worse_file_num()
        self.read_cc_person_data()
        self.save_cc_result_summary()
        self.update_old_cc_latest(active_cc_file_hash_list)
        logger.info("%s 完成圈复杂度数据存储" % self._log_prefix)
