# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - base core
"""
import time
import uuid
import json
import logging
import traceback
from zipfile import BadZipFile
from collections import defaultdict
from importlib import import_module
from json.decoder import JSONDecodeError

from django.utils.timezone import now

from apps.codeproj import models

from util import errcode
from util.exceptions import CDErrorBase
from util.fileserver import file_server

logger = logging.getLogger(__name__)


class ProjectController(object):
    """项目控制器
    """

    @classmethod
    def create_project(cls, **kwargs):
        """创建项目
        """
        # 创建项目
        project = models.Project.objects.create(
            id=kwargs["id"],
            repo_id=kwargs.get("repo_id"),
            scan_scheme_id=kwargs.get("scan_scheme_id"),
            scm_type=kwargs.get("scm_type"),
            scm_url=kwargs.get("scm_url"),
            user=kwargs.get("creator"),
            org_sid=kwargs.get("org_sid"),
            team_name=kwargs.get("team_name"),
        )
        logger.info("create new project, project: %s, repo: %s, scan_scheme: %s" % (
            project.id, project.repo_id, project.scan_scheme_id))
        return project


class ScanResultController(object):
    """扫描结果控制器
    """

    def __init__(self, project_id, scan_id):
        """初始化函数
        :param project_id: int, 项目编号
        :param scan_id: int, 扫描编号
        """
        self._project_id = project_id
        self._scan_id = scan_id
        self._project = None
        self._scan = None
        self._log_prefix = None

    def _put_module_result(self, module_name, module_tasks):
        """return traceback string if has error
        """
        module = import_module("apps.%s.job" % module_name)
        method = getattr(module, "on_job_end", None)
        if method:
            try:
                method(self._scan, module_tasks)
                return None, errcode.OK
            except CDErrorBase as err:
                logger.exception("apps.%s.on_job_end has error: %s" % (module_name, err))
                return traceback.format_exc(), err.code
            except BadZipFile as err:
                logger.exception("apps.%s.on_job_end has error: %s" % (module_name, err))
                return traceback.format_exc(), errcode.E_SERVER_FILE_SERVICE_ERROR
            except JSONDecodeError as err:
                logger.exception("apps.%s.on_job_end has error: %s" % (module_name, err))
                return traceback.format_exc(), errcode.E_SERVER_FILE_SERVICE_ERROR
            except Exception as err:
                logger.exception("apps.%s.on_job_end has error: %s" % (module_name, err))
                return traceback.format_exc(), errcode.E_SERVER

    def init_controller(self):
        """初始化
        """
        self._project = models.Project.objects.get(id=self._project_id)
        self._scan = models.Scan.objects.get(id=self._scan_id, project_id=self._project_id)
        self._log_prefix = "[Project: %s][Job: %d][Scan: %d][Type :%d]" % (
            self._project_id, self._scan.job_gid, self._scan_id, self._scan.type)

    def wait_other_scan_closing(self):
        """等待其他scan入库
        """
        wait_count = 0
        wait_time = 30
        wait_limit = 10
        while models.Scan.objects.filter(project=self._project, state=models.Scan.StateEnum.CLOSING).exclude(
                id=self._scan_id).count():
            # 是否有其他任务正在入库
            wait_count += 1
            if wait_count > wait_limit:
                logger.info(self._log_prefix + "有其他scan/job正在入库，但已等待超过%d次，强行入库..." % wait_limit)
                break
            wait_time = min(300, wait_time + 60)
            logger.info(self._log_prefix + "有其他scan/job正在入库，第(%d/%d)次等待 %d 秒后继续入库..." % (
                wait_count, wait_limit, wait_time))
            time.sleep(wait_time)

    def check_current_scan_closing(self):
        """检查当前扫描是否在入库中
        """
        nrows = models.Scan.objects.filter(
            id=self._scan_id, state__in=[models.Scan.StateEnum.WAITING, models.Scan.StateEnum.RUNNING]) \
            .update(state=models.Scan.StateEnum.CLOSING)
        return True if not nrows else False

    def close_current_scan(self, job):
        """关闭当前扫描
        """
        models.Scan.objects.filter(id=self._scan_id, state=models.Scan.StateEnum.CLOSING).update(
            state=models.Scan.StateEnum.CLOSED, result_code=job["result_code"],
            result_msg=job.get("result_msg"), end_time=now())

    def close_old_scan(self):
        """关闭之前未完成的扫描
        """
        result_msg = json.dumps({"job_id": self._scan.job_gid or 0, "scan_id": self._scan_id,
                                 "msg": "已有新版任务完成扫描，合流任务请重启工具直接取结果即可。"})
        for old_scan in models.Scan.objects.filter(
                project=self._project, state=models.Scan.StateEnum.RUNNING, id__lt=self._scan_id):
            logger.info(self._log_prefix + "正在关闭更早的扫描scan[%d] ..." % old_scan.id)
            if old_scan.result_code is None:
                nrows = models.Scan.objects.filter(id=old_scan.id, state=models.Scan.StateEnum.RUNNING).update(
                    result_code=errcode.CLIENT_REDIRECT,
                    result_msg=result_msg,
                    end_time=now(),
                    state=models.Scan.StateEnum.CLOSED)
            else:
                # 兼容历史数据，未添加state参数但已入库数据。
                nrows = models.Scan.objects.filter(id=old_scan.id, state=models.Scan.StateEnum.RUNNING).update(
                    state=models.Scan.StateEnum.CLOSED)
            if nrows:
                logger.info(self._log_prefix + "已关闭更早的扫描scan[%d] ..." % old_scan.id)
            else:
                logger.info(self._log_prefix + "关闭更早的扫描失败。scan[%d]" % old_scan.id)

    def upload_scan_result(self, errors):
        """上传scan结果到文件服务器
        """
        error_uuid = str(uuid.uuid1().hex)
        try:
            scan_result_path = "scandata/projects/%d/scans/%d/%s/error_msg.json" % (
                self._project_id, self._scan_id, error_uuid)
            scan_result_path = file_server.put_file(str(errors), scan_result_path,
                                                    file_server.TypeEnum.TEMPORARY)
            return scan_result_path, None
        except Exception as err:
            logger.error("上传文件服务器异常: %s" % err)
        return None, "数据入库失败，且上报错误信息到文件服务器失败。"

    def save_scan_result(self, data):
        """保存扫描结果
        """
        scan_result_path = None
        logger.info(self._log_prefix + "开始数据入库...(参数如下)")
        logger.info(data)
        job = data["job"]
        tasks = data["tasks"]
        # 判断是否有其他任务正在入库
        # 2. 等待正在入库的历史任务结束
        self.wait_other_scan_closing()
        # 检查是否正在入库或已经入库完成？
        scan_closing = self.check_current_scan_closing()
        if scan_closing:
            # 是，正在入库或者已经入库完成
            logger.info(self._log_prefix + "入库结束。当前任务%s " % self._scan.get_state_display())
            # 判断scan是否closing且job为closed
            if self._scan.state == models.Scan.StateEnum.CLOSING and job.get("result_code"):
                logger.info(self._log_prefix + "根据Job的结果码[%s]关闭scan" % job["result_code"])
                self.close_current_scan(job)

        else:  # 否，锁定资源，可以入库
            # 当前任务结果是重定向
            if errcode.is_client_redirect(job["result_code"]):
                logger.info(self._log_prefix + "Job result_code 成功，开始关闭更早的未入库的扫描（如有）...")
                self.close_current_scan(job)

            elif errcode.is_success(job["result_code"]):  # 是否扫描成功
                # 是，任务成功结束
                # 1. 取消未开始入库的历史任务
                logger.info(self._log_prefix + "Job result_code 成功，开始关闭更早的未入库的扫描（如有）...")
                self.close_old_scan()
                logger.info(self._log_prefix + "已关闭更早的未入库的扫描...")

                # 2. 开始当前任务数据入库
                logger.info(self._log_prefix + "准备task数据...")
                module_results = defaultdict(list)
                for task in tasks:
                    module_name = task["module"]
                    module_results[module_name].append(task)
                logger.info(self._log_prefix + "调用各个模块job.on_job_end开始入库...")

                result_code = None
                errors = []
                ok_modules = set()
                for module_name, module_tasks in module_results.items():
                    logger.info(self._log_prefix + "模块[%s]开始入库 ..." % module_name)
                    tb, code = self._put_module_result(module_name, module_tasks)
                    if tb:
                        errors.append({"module": module_name, "traceback": tb, "result_code": code})
                        result_code = code
                    else:
                        ok_modules.add(module_name)
                if errors:
                    self._scan.result_code = result_code
                    self._scan.result_msg = "数据入库失败。"
                    scan_result_path, result_msg = self.upload_scan_result(errors)
                    if not scan_result_path:
                        self._scan.result_msg = result_msg
                    logger.error(self._log_prefix + self._scan.result_msg + str(errors))
                else:
                    self._scan.result_code = errcode.OK
                    self._scan.result_msg = None
                self._scan.end_time = now()
                self._scan.state = models.Scan.StateEnum.CLOSED
                self._scan.save()
            else:
                # 否，任务失败，只更新当前扫描结果
                logger.info(self._log_prefix +
                            "Job result_code[%d] 失败，仅记录当前扫描失败，无数据入库。" % job["result_code"])
                models.Scan.objects.filter(id=self._scan_id).update(
                    result_code=job["result_code"], result_msg=job["result_msg"], end_time=now(),
                    state=models.Scan.StateEnum.CLOSED)

        return scan_result_path
