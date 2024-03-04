# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
localscan 向server查询操作类
"""

import time
import json

from node.app import settings
from node.localtask.localreport import LocalReport
from node.localtask.urlmgr import UrlMgr, UrlMap
from node.localtask.status import StatusType
from util.errcode import E_NODE_TASK_EXPIRED
from util.logutil import LogPrinter


class ServerQuery(object):
    """
    向server查询操作类
    """
    @staticmethod
    def fix_scan_result(scan_result, lintscan_result):
        """
        根据问题单实时状态，用 lintscan_result 修正 scan_result 中 lintscan 部分的数据
        scan_result是原始扫描数据,lintscan_result是从问题列表页面实时获取的数据（部分问题已经经过用户手动处理）
        注意1: 按规则类型分类的统计数据暂不更新，出于server查询效率考虑，实时数据暂未获取该部分数据，目前也暂未用到这部分数据作为红线判断
        注意2: 如果总问题量超过1000条，出于server查询效率考虑，不会更新实时数据，此时实时数据未更新
        :param scan_result:
        :param lintscan_result:
        :return:
        """
        # 先判空，没有开启代码检查的情况字段值会是None
        if "lintscan" in scan_result and scan_result["lintscan"]:
            # 将按类别分类的数据保存下来
            category_detail = {
                "current_scan": scan_result["lintscan"]["current_scan"]["active_category_detail"],
                "total": scan_result["lintscan"]["total"]["category_detail"]
            }
            # 修正scan_result
            scan_result["lintscan"]["issue_open_num"] = lintscan_result["current_scan"]["issue_open_num"]
            scan_result["lintscan"]["issue_fix_num"] = lintscan_result["current_scan"]["issue_fix_num"]
            scan_result["lintscan"]["current_scan"] = lintscan_result["current_scan"]
            scan_result["lintscan"]["total"] = lintscan_result["total"]
            # 将 category_detail 恢复回去
            scan_result["lintscan"]["current_scan"]["active_category_detail"] = category_detail["current_scan"]
            scan_result["lintscan"]["total"]["category_detail"] = category_detail["total"]
            return scan_result
        else:
            return scan_result

    @staticmethod
    def query_result_by_revision(dog_server, server_url, repo_id, proj_id, revision,
                                 org_sid=None, team_name=None, fix_result=True):
        """
        通过执行代码版本号查询扫描结果
        :param dog_server:
        :param server_url:
        :param repo_id:
        :param proj_id:
        :param revision:
        :return:
        """
        # 转换成前端页面url,供展示用
        front_end_url = UrlMap.get_frontend_url(server_url)
        scan_result = dog_server.get_scan_result_by_revision(proj_id, revision, repo_id, org_sid, team_name)
        # 先判空，没有开启代码检查的情况字段值会是None
        if "lintscan" in scan_result and scan_result["lintscan"]:
            # 获取问题单实时状态数据
            lintscan_result = dog_server.get_lintscan_result(project_id=proj_id, scan_revision=revision,
                                                             repo_id=repo_id, org_sid=org_sid, team_name=team_name)
            # 根据问题单实时状态，修正扫描结果数据
            if fix_result:
                scan_result = ServerQuery.fix_scan_result(scan_result, lintscan_result)
        return LocalReport.analyze_scan_result(front_end_url, scan_result, repo_id, proj_id,
                                               org_sid=org_sid, team_name=team_name)

    @staticmethod
    def query_result(dog_server, server_url, repo_id, proj_id, scan_id, timeout,
                     org_sid, team_name, job_web_url, fix_result):
        """
        向server端轮询扫描结果
        :param team_name:
        :param org_sid:
        :param dog_server:
        :param server_url:
        :param repo_id:
        :param proj_id:
        :param scan_id:
        :param timeout: 查询超时
        :param job_web_url: 任务详情页面url
        :return: status, url, , message
        {
            "status": "success|error",
            "error_code": 错误码,
            "url": "result url",
            "text": "simple msg",
            "description": "message",
            "stat_report": {"current_scan": xx, "total": xx} | {},
            "scan_report": {...}
        }
        """
        LogPrinter.info("query result from server ...")
        # 等待数据入库后再开始轮询结果
        time.sleep(settings.RESULT_INTO_DB_TIME)

        # 转换成前端页面url,供展示用
        front_end_url = UrlMap.get_frontend_url(server_url)

        scan_history_url = UrlMgr(front_end_url, repo_id, proj_id, org_sid=org_sid,
                                  team_name=team_name).get_scan_history_url()
        url = job_web_url if job_web_url else scan_history_url

        start_time = time.time()
        while True:
            # 判断是否超时
            cur_time = time.time()
            if cur_time - start_time > timeout:
                return {
                    "status": StatusType.ERROR,
                    "error_code": E_NODE_TASK_EXPIRED,
                    "url": url,
                    "text": "超时",
                    "description": "获取扫描结果超时,超时限制为%s秒,请查看任务详情:%s" % (timeout, url),
                    # "stat_report": {},
                    "scan_report": {}
                }

            # 向server查询扫描结果
            result = dog_server.get_scan_result(proj_id, scan_id, repo_id, org_sid, team_name)
            result_code = result["result_code"]

            # 有更新的任务执行完成了,本次扫描取消,取更新的结果（任务重定向结果码从303调整为2）
            if result_code == 303 or result_code == 2:
                result_msg = result["result_msg"]
                result_msg = json.loads(result_msg)
                # 更新scan_id为新任务,重新获取结果
                scan_id = result_msg["scan_id"]
                LogPrinter.info("another scan task (newer code revision) has been done, "
                                "get the latest result instead (scan_id: %s)" % scan_id)
                result = dog_server.get_scan_result(proj_id, scan_id, repo_id, org_sid, team_name)
                result_code = result["result_code"]

            # result_code==None,表示还未完成,继续等待和轮询结果(不能直接判非,因为返回0表示扫描成功)
            if result_code is None:
                time.sleep(settings.POLLING_INTERVAL)
                continue

            # 返回码是0-99,扫描成功
            elif result_code in list(range(100)):
                # 先判空，没有开启代码检查的情况字段值会是None
                if "lintscan" in result and result["lintscan"]:
                    # 获取问题单实时状态数据
                    lintscan_result = dog_server.get_lintscan_result(project_id=proj_id, scan_id=scan_id,
                                                                     repo_id=repo_id, org_sid=org_sid,
                                                                     team_name=team_name)
                    # 根据问题单实时状态，修正扫描结果数据
                    if fix_result:
                        result = ServerQuery.fix_scan_result(result, lintscan_result)

                return LocalReport.analyze_scan_result(front_end_url, result, repo_id, proj_id, scan_id,
                                                       org_sid, team_name, job_web_url)

            # 其他返回码,扫描异常
            else:
                return {
                    "status": StatusType.ERROR,
                    "error_code": result_code,
                    "url": url,
                    "text": result["result_code_msg"],
                    "description": result["result_msg"],
                    "scan_report": {}
                }
