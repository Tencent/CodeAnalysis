# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
TaskProcessMgr
"""
import sys
import logging

from util.exceptions import NodeError
from util import errcode
from node.localtask.serverquery import ServerQuery
from node.app import settings
from node.localtask.localreport import LocalReport

logger = logging.getLogger(__name__)


class ScmRevisionCheck(object):
    def __init__(self, dog_server, source_dir, total_scan, scm_info,
                 scm_client, report_file, server_url, scan_history_url,
                 job_web_url, repo_id, proj_id, org_sid, team_name):
        self._total_scan = total_scan
        self._source_dir = source_dir
        self._scm_info = scm_info
        self._scm_client = scm_client
        self._report_file = report_file
        self._dog_server = dog_server
        self._server_url = server_url
        self._repo_id = repo_id
        self._proj_id = proj_id
        self._org_sid = org_sid
        self._team_name = team_name
        self._scan_history_url = scan_history_url
        self._job_web_url = job_web_url

    def _local_rev_is_newer(self, compare_revision):
        """
        判断本地代码版本是否更新(大于对比版本)
        :param compare_revision:
        :return: True | False | "Error"(判断异常)
        """
        # 判空
        if not compare_revision:
            logger.error("compare_revision is empty(%s)" % compare_revision)
            return "Error"
        # 如果版本号相同,本地revision肯定不比last_revision更新,直接返回False
        if str(compare_revision) == str(self._scm_info.scm_revision):
            return False

        # 没有指定本地代码目录时, self._scm_client还未被初始化,为None
        # 此时扫描的scm_revision为远端代码库的最新版本,由于此时已经排除相等的情况,那么revision肯定是比对比版本更新的
        if not self._scm_client:
            return True
        else:
            try:
                is_newer = self._scm_client.revision_lt(compare_revision, self._scm_info.scm_revision)
                return is_newer
            except Exception as err:
                # 以下情况会异常:
                # 1. 本地代码版本 < scm_last_revision,git本地没有scm_last_revision的信息,无法比较
                # 2. scm_last_revision的git记录被删除,导致找不到该版本,无法比较
                logger.error("scm_client.revision_lt() warning: %s", err)
                return "Error"

    def is_revision_unchanged(self):
        """
        判断扫描后本地代码revision是否与扫描前一致
        :return: True(版本相同)|False(版本不同), error_msg
        """
        # 不使用本地代码(新拉取的代码),不需要判断
        if not self._source_dir:
            return True, ""
        # 获取扫描完成后的本地代码版本号
        try:
            after_scan_revision = self._scm_client.info().commit_revision
        except Exception as err:
            raise NodeError(code=errcode.E_NODE_TASK_SCM_FAILED, msg=str(err))
        if after_scan_revision == self._scm_info.scm_revision:
            return True, ""
        else:
            error_msg = "扫描结束时本地代码版本号(%s)与扫描前(%s)不同,扫描失败!请勿在扫描过程中修改代码目录!" % (
            after_scan_revision, self._scm_info.scm_revision)
            return False, error_msg

    def check_scm_revision(self, job_context, task_list):
        """
        检查扫描版本号，如果版本号：
            1. 不比上次扫描版本号新,取消扫描
            2. 小于起始版本号,取消扫描
        :param job_context: 项目参数
        :param task_list: task列表
        :return: True|False,是否符合扫描条件
        """
        # logger.info("===>>> job_context: %s" % json.dumps(job_context, indent=2))
        if not self._total_scan:
            # 收集所有 scan_app 的上次扫描版本号(新增scan app的情况下,每个 scan app 的 last_revision 不同)
            last_scan_revisions = []
            for task in task_list:
                if "scm_last_revision" in task["task_params"]:
                    scm_last_revision = task["task_params"]["scm_last_revision"]
                    if scm_last_revision:
                        last_scan_revisions.append(scm_last_revision)

            # 1. 增量扫描时,如果本地版本<=上次扫描版本,不允许启动
            for last_scan_rev in last_scan_revisions:
                local_is_newer = self._local_rev_is_newer(last_scan_rev)
                # 判断版本失败,直接改为全量扫描,允许本次执行
                if local_is_newer == "Error":
                    logger.info("Fail to compare with last revision(%s),switch to total scan." % last_scan_rev)
                    self._total_scan = True
                    continue
                if not local_is_newer:
                    if str(last_scan_rev) == str(self._scm_info.scm_revision):
                        message = f'代码版本({self._scm_info.scm_revision})与上次扫描任务相同,直接获取上次扫描结果.'
                    else:
                        message = f'代码版本({self._scm_info.scm_revision})早于上次扫描版本({last_scan_rev}),直接获取上次扫描结果.'

                    scan_result = ServerQuery().query_result_by_revision(self._dog_server, self._server_url,
                                                                         self._repo_id, self._proj_id,
                                                                         last_scan_rev, self._org_sid,
                                                                         self._team_name, True)

                    # 改写text,description字段值,标记本次扫描由于版本问题被跳过
                    scan_result["text"] = "跳过,直接取结果"
                    scan_result["description"] = "%s\n%s" % (message, scan_result["description"])
                    LocalReport.output_report(scan_result, self._report_file)
                    sys.exit(0)  # 直接退出

            # 2. 增量扫描时,如果本地版本 <= 正在扫描的版本,不启动本地扫描,直接轮询等待正在扫描的任务完成,取最新扫描结果
            latest_scan_data = self._dog_server.get_latest_scm_scan(self._proj_id, self._repo_id, self._org_sid,
                                                                    self._team_name)
            if latest_scan_data:
                running_rev = latest_scan_data["current_revision"]
                status = latest_scan_data["result_code"]
                if (status is None) and running_rev:  # status=None表示正在执行; running_rev=None时不做判断
                    local_rev_is_newer = self._local_rev_is_newer(running_rev)
                    if local_rev_is_newer == "Error":
                        # 判断版本失败,直接改为全量扫描,允许本次执行
                        logger.info(
                            "Fail to compare with running task revision(%s),switch to total scan." % running_rev)
                        self._total_scan = True
                    else:
                        if not local_rev_is_newer:  # 本地版本 <= 正在扫描的最新版本,不启动本地扫描,直接轮询最新扫描结果
                            if str(running_rev) == str(self._scm_info.scm_revision):
                                message = f"已经有相同代码版本({self._scm_info.scm_revision})的扫描任务在执行中"
                            else:
                                message = f"当前代码版本:({self._scm_info.scm_revision}),已经有更新的代码版本({running_rev})任务在执行中"
                            logger.info("%s,跳过本次扫描,请等待获取扫描结果..." % message)
                            logger.info("可以打开链接，查看任务进度: %s" % self._scan_history_url)

                            # 从server端查询本次扫描结果
                            query_timeout = settings.LOCAL_TASK_EXPIRED
                            scan_id = latest_scan_data["id"]
                            scan_result = ServerQuery.query_result(self._dog_server, self._server_url,
                                                                   self._repo_id, self._proj_id,
                                                                   scan_id, query_timeout, self._org_sid,
                                                                   self._team_name, self._job_web_url, True)
                            # 改写description字段值,标记本次扫描由于版本问题被跳过
                            message = "%s,跳过本次扫描,直接获取结果." % message
                            scan_result["description"] = "%s\n%s" % (message, scan_result["description"])
                            # 输出本地报告
                            LocalReport.output_report(scan_result, self._report_file)
                            sys.exit(0)

        # 3.如果本地代码版本<起始版本号,取消扫描
        # 项目起始版本号
        scm_initial_last_revision = job_context.get('scm_initial_last_revision')
        if self._scm_client and scm_initial_last_revision:
            try:
                local_revision_is_newer = self._scm_client.revision_lt(scm_initial_last_revision,
                                                                       self._scm_info.scm_revision)
            except Exception as err:
                # 如果本地代码版本号比 scm_initial_last_revision 老,git本地没有 scm_initial_last_revision 的信息,无法比较,会抛异常
                logger.warning("scm_client.revision_lt() warning: %s", err)
                local_revision_is_newer = False
            if not local_revision_is_newer:
                message = f"base_revision({scm_initial_last_revision} must be " \
                          f"older than latest revision({self._scm_info.scm_revision})"
                raise NodeError(code=errcode.E_NODE_TASK_CONFIG, msg=message)
