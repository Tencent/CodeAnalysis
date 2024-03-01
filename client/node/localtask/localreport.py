# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
localscan 结果报告处理类
"""

import json

from node.localtask.urlmgr import UrlMgr
from node.localtask.status import StatusType
from util.logutil import LogPrinter
from util.errcode import OK


class LocalReport(object):
    """
    localscan 结果报告处理类
    """
    @staticmethod
    def output_report(result, report_file_path):
        """
        本地扫描的统计报告,输出到json文件中
        统计报告数据结构:
        {
            "status": "success|error",  # 执行成功|执行异常
            "error_code": 错误码,
            "url": 结果链接,
            "text": 简要描述,
            "description": 详细描述,
            "scan_report": {}
        }
        :param result: 扫描结果
        :param report_file_path: 输出结果文件路径
        :param dog_server: 与server通信的api实例
        :param proj_id: 项目id,供向server查询项目数据使用
        :param enable_report: 是否生成web报告
        :param local_task_dirs: 本地执行的任务目录列表
        :return:
        """
        # 输出到json文件
        with open(report_file_path, "wb") as status_obj:
            status_obj.write(str.encode(json.dumps(result, indent=2, ensure_ascii=False)))

        # 打印扫描结果
        description = result["description"]
        split_line = "*" * 100
        LogPrinter.info(f"\n{split_line}\n代码分析结果: \n{description}\n{split_line}")
        LogPrinter.info(f"json report: {report_file_path}")

    def __format_lint_report(self, lint_result):
        """
        格式化lint_result,补充完整所有字段,缺失的字段数据为0
        :param lint_result:
        :return:
        """
        # 初始化所有字段
        format_report = {
            "current_scan": {  # 本次扫描
                "issue_open_num": 0,    # 新增问题量
                "issue_fix_num": 0,     # 关闭问题量
                "active_severity_detail":{  #新增问题严重级别统计
                    "fatal": 0,   # 致命
                    "error": 0,   # 错误
                    "warning": 0, # 警告
                    "info": 0     # 提示
                },
                "active_category_detail":{  # 新增问题类别统计
                    "correctness": 0,    # 功能
                    "security": 0,       # 安全
                    "performance": 0,    # 性能
                    "usability": 0,      # 可用性
                    "accessibility": 0,  # 无障碍化
                    "i18n": 0,           # 国际化
                    "convention": 0,     # 代码风格
                    "other": 0           # 其他
                }
            },
            "total": {   # 存量问题
                "state_detail": {  # 总量统计
                    "active": 0,
                    "resolved": 0,
                    "closed": 0
                },
                "severity_detail":{  # 按严重级别统计
                    "fatal": {"active": 0, "resolved": 0, "closed": 0},   # 未处理，已处理，关闭
                    "error": {"active": 0, "resolved": 0, "closed": 0},
                    "warning": {"active": 0, "resolved": 0, "closed": 0},
                    "info": {"active": 0, "resolved": 0, "closed": 0}
                },
                "category_detail":{      # 按类别统计
                    "correctness": {"active": 0, "resolved": 0, "closed": 0},
                    "security": {"active": 0, "resolved": 0, "closed": 0},
                    "performance": {"active": 0, "resolved": 0, "closed": 0},
                    "usability": {"active": 0, "resolved": 0, "closed": 0},
                    "accessibility": {"active": 0, "resolved": 0, "closed": 0},
                    "i18n": {"active": 0, "resolved": 0, "closed": 0},
                    "convention": {"active": 0, "resolved": 0, "closed": 0},
                    "other": {"active": 0, "resolved": 0, "closed": 0}
                }
            }
        }

        # 遍历 lint_result 各字段并拷贝值到format_report
        if "current_scan" in lint_result:
            current_scan = lint_result["current_scan"]
            format_current_scan = format_report["current_scan"]
            if "issue_open_num" in current_scan:
                format_current_scan["issue_open_num"] = current_scan["issue_open_num"]
            if "issue_fix_num" in current_scan:
                format_current_scan["issue_fix_num"] = current_scan["issue_fix_num"]
            if "active_severity_detail" in current_scan:
                self.__copy_dict(current_scan["active_severity_detail"], format_current_scan["active_severity_detail"])
            if "active_category_detail" in current_scan:
                self.__copy_dict(current_scan["active_category_detail"], format_current_scan["active_category_detail"])
        if "total" in lint_result:
            total_scan = lint_result["total"]
            format_total_scan = format_report["total"]
            if "state_detail" in total_scan:
                self.__copy_dict(total_scan["state_detail"], format_total_scan["state_detail"])
            if "severity_detail" in total_scan:
                for key in total_scan["severity_detail"].keys():
                    self.__copy_dict(total_scan["severity_detail"][key], format_total_scan["severity_detail"][key])
            if "category_detail" in total_scan:
                for key in total_scan["category_detail"].keys():
                    self.__copy_dict(total_scan["category_detail"][key], format_total_scan["category_detail"][key])

        return format_report

    def __copy_dict(self, from_dict, to_dict):
        """
        拷贝dict中各个字段的值,只支持一层字典的拷贝
        :param from_dict:
        :param to_dict:
        :return:
        """
        for key in to_dict.keys():
            if key in from_dict and key in to_dict:
                to_dict[key] = from_dict[key]

    @staticmethod
    def analyze_scan_result(front_end_url, scan_result, repo_id, proj_id, scan_id=None,
                            org_sid=None, team_name=None, job_web_url=None):
        """
        解析扫描结果
        :param front_end_url: 前端展示域名
        :param scan_result:{
                    "lintscan": {},                 # 代码检查
                    "duplicatescan": {},            # 重复代码
                    "cyclomaticcomplexityscan": {}, # 圈复杂度
                    "clocscan": {}                  # 代码统计
                }
        :param repo_id:
        :param proj_id:
        :param scan_id: 如果没有传scan_id,表示此次扫描被跳过,是通过revision查询的扫描结果
        :param org_sid:
        :param team_name:
        :param job_web_url:
        :return:
        """
        # LogPrinter.info(f">> 原始 scan_result: {json.dumps(scan_result, indent=2)}")

        # 1. 获取 scan_id

        # 没有传scan_id,表示此次扫描被跳过,是通过revision查询的扫描结果，此时scan_id可以从结果字段中获取
        lint_scan_result = scan_result["lintscan"]
        if not scan_id and lint_scan_result:
            scan_id = lint_scan_result["scan"]["id"]
        cc_result = scan_result["cyclomaticcomplexityscan"]
        if not scan_id and cc_result:
            scan_id = cc_result.get("scan")
        duplicate_result = scan_result["duplicatescan"]
        if not scan_id and duplicate_result:
            scan_id = duplicate_result.get("scan")
        cloc_result = scan_result["clocscan"]
        if not scan_id and cloc_result:
            scan_id = cloc_result.get("scan")
        score_scan_result = scan_result.get("scorescan")
        if not scan_id and score_scan_result:
            scan_id = score_scan_result["scan"]["id"]

        # 2. 获取前端展示 urls

        url_mgr_client = UrlMgr(front_end_url, repo_id, proj_id, org_sid=org_sid, team_name=team_name)
        proj_overview_url = url_mgr_client.get_proj_overview_url()
        scan_history_url = url_mgr_client.get_scan_history_url()
        issue_open_url = url_mgr_client.get_scan_open_issues_url(scan_id)
        issue_fix_url = url_mgr_client.get_scan_fix_issues_url(scan_id)
        issues_url = url_mgr_client.get_issues_url()
        cc_worse_file_list_url = url_mgr_client.get_cc_worse_file_list_url()
        cc_result_url = url_mgr_client.get_cc_file_list_url()
        duplicate_result_url = url_mgr_client.get_duplicate_result_url()
        cloc_result_url = url_mgr_client.get_cloc_result_url()

        urls = {
            "proj_overview": proj_overview_url,  # 项目概览页面
            "scan_history": scan_history_url,  # 扫描历史页面
            "issues_new": issue_open_url,  # 本次扫描新增问题页面
            "issues_fixed": issue_fix_url,   # 本地扫描关闭问题页面
            "issues_total": issues_url,  # 所有问题列表页面
            "cc_worse_files": cc_worse_file_list_url,  # 圈复杂度恶化文件列表页面
            "cc_result": cc_result_url,  # 圈复杂度结果页面
            "duplicate_result": duplicate_result_url,  # 重复代码结果页面
            "cloc_result": cloc_result_url,  # 代码统计结果页面
        }

        # 3. 获取结果 messages

        message_list = []
        # 代码检查
        if lint_scan_result:
            # 格式化lintscan结果
            scan_result["lintscan"] = LocalReport().__format_lint_report(lint_scan_result)
            # LogPrinter.info(f">> lint_scan_result: {json.dumps(lint_scan_result, indent=2)}")

            issue_open_num = lint_scan_result["issue_open_num"]
            issue_fix_num = lint_scan_result["issue_fix_num"]

            lintscan_msg = "[代码检查结果] 本次扫描发现新问题量: %s, 关闭问题量: %s" % (issue_open_num, issue_fix_num)
            if issue_open_num:
                lintscan_msg += "\n查看新增问题列表: %s" % issue_open_url
            if issue_fix_num:
                lintscan_msg += "\n查看关闭问题列表: %s" % issue_fix_url
            lintscan_msg += "\n查看所有问题列表: %s" % issues_url
            message_list.append(lintscan_msg)

        # 圈复杂度
        if cc_result:
            cc_msg = "[圈复杂度结果] 圈复杂度恶化文件列表: %s" % cc_worse_file_list_url
            message_list.append(cc_msg)

        # 重复代码
        if duplicate_result:
            duplicate_msg = "[重复代码结果] 问题列表: %s" % duplicate_result_url
            message_list.append(duplicate_msg)

        # 代码统计
        if cloc_result:
            cloc_msg = "[代码统计结果] 统计数据: %s" % cloc_result_url
            message_list.append(cloc_msg)

        # 开源治理分数
        if score_scan_result:
            style_score = score_scan_result.get("style_score")
            if style_score:
                style_score = round(style_score, 1)  # 取小数点后1位
            security_score = score_scan_result.get("security_score")
            if security_score:
                security_score = round(security_score, 1)
            score_msg = f"[开源治理得分] 代码规范: {style_score}, 代码安全: {security_score}, 链接: {proj_overview_url}"
            message_list.append(score_msg)

        if job_web_url:
            message_list.append("任务执行详情: %s" % job_web_url)

        return {
            "status": StatusType.SUCCESS,
            "error_code": OK,
            "url": scan_history_url,
            "text": "扫描完成",
            "description": '\n'.join(message_list),
            "urls": urls,
            "scan_report": scan_result,
            "project_id": proj_id,  # 供CI流水线上报质量红线数据使用
            "scan_id": scan_id      # 供CI流水线上报质量红线数据使用
        }
