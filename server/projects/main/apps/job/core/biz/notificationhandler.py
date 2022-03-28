# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""消息提醒
"""

# 原生 import
import datetime
import json
import logging
import os

# 第三方 import
import jinja2

# 项目内 import
from apps.job.models import Job, CooperationJob
from util import errcode
from util.biz.msg.msghandler import MessageHandler

logger = logging.getLogger(__name__)

CODEDOG_MAIN_URL = "http://codedog.woa.com"
CODING_MAIN_URL = "http://tencent.coding.woa.com"

CODEDOG_URL_ISSUES_PARAMS = "resolution=&author&is_tapdbug&scan_open&scan_fix&ci_time_gte&ci_time_lte&file_path&checkrule_display_name&checkpackage&limit=12&offset=0"
CODING_URL_ISSUES_PARAMS = "tab=issues-list&offset=0&limit=10&ordering=severity"

CODEDOG_URLS = {
    "project_url": "%s/repos/{repo_id}/projects/{project_id}/" % CODEDOG_MAIN_URL,
    "code_check_url": "%s/repos/{repo_id}/projects/{project_id}/codelint/issues" % CODEDOG_MAIN_URL,
    "info_url": "%s/repos/{repo_id}/projects/{project_id}/codelint/issues?scan_open={scan_id}&state&severity=4&%s" % (
        CODEDOG_MAIN_URL, CODEDOG_URL_ISSUES_PARAMS),
    "warning_url": "%s/repos/{repo_id}/projects/{project_id}/codelint/issues?scan_open={scan_id}&state&severity=3&%s" % (
        CODEDOG_MAIN_URL, CODEDOG_URL_ISSUES_PARAMS),
    "error_url": "%s/repos/{repo_id}/projects/{project_id}/codelint/issues?scan_open={scan_id}&state&severity=2&%s" % (
        CODEDOG_MAIN_URL, CODEDOG_URL_ISSUES_PARAMS),
    "fatal_url": "%s/repos/{repo_id}/projects/{project_id}/codelint/issues?scan_open={scan_id}&state&severity=1&%s" % (
        CODEDOG_MAIN_URL, CODEDOG_URL_ISSUES_PARAMS),
    "info_active_url": "%s/repos/{repo_id}/projects/{project_id}/codelint/issues?severity=4&state=1&resolution" % CODEDOG_MAIN_URL,
    "warning_active_url": "%s/repos/{repo_id}/projects/{project_id}/codelint/issues?severity=3&state=1&resolution" % CODEDOG_MAIN_URL,
    "error_active_url": "%s/repos/{repo_id}/projects/{project_id}/codelint/issues?severity=2&state=1&resolution" % CODEDOG_MAIN_URL,
    "fatal_active_url": "%s/repos/{repo_id}/projects/{project_id}/codelint/issues?severity=1&state=1&resolution" % CODEDOG_MAIN_URL,
    "info_resolved_url": "%s/repos/{repo_id}/projects/{project_id}/codelint/issues?severity=4&state=2&resolution" % CODEDOG_MAIN_URL,
    "warning_resolved_url": "%s/repos/{repo_id}/projects/{project_id}/codelint/issues?severity=3&state=2&resolution" % CODEDOG_MAIN_URL,
    "error_resolved_url": "%s/repos/{repo_id}/projects/{project_id}/codelint/issues?severity=2&state=2&resolution" % CODEDOG_MAIN_URL,
    "fatal_resolved_url": "%s/repos/{repo_id}/projects/{project_id}/codelint/issues?severity=1&state=2&resolution" % CODEDOG_MAIN_URL,
    "info_closed_url": "%s/repos/{repo_id}/projects/{project_id}/codelint/issues?severity=4&state=3&resolution" % CODEDOG_MAIN_URL,
    "warning_closed_url": "%s/repos/{repo_id}/projects/{project_id}/codelint/issues?severity=3&state=3&resolution" % CODEDOG_MAIN_URL,
    "error_closed_url": "%s/repos/{repo_id}/projects/{project_id}/codelint/issues?severity=2&state=3&resolution" % CODEDOG_MAIN_URL,
    "fatal_closed_url": "%s/repos/{repo_id}/projects/{project_id}/codelint/issues?severity=1&state=3&resolution" % CODEDOG_MAIN_URL,
    "code_measure_url": "%s/repos/{repo_id}/projects/{project_id}/codemetric/ccfiles" % CODEDOG_MAIN_URL,

    "failure_url": "%s/repos/{repo_id}/projects/{project_id}/scan_history" % CODEDOG_MAIN_URL
}

CODING_URLS = {
    "project_url": "%s/p/{coding_project_name}/code-analysis/repos/{repo_id}/projects/{project_id}/overview?tab=overview" % CODING_MAIN_URL,
    "code_check_url": "%s/p/{coding_project_name}/code-analysis/repos/{repo_id}/projects/{project_id}/codelint-issues?%s" % (
        CODING_MAIN_URL, CODING_URL_ISSUES_PARAMS),
    "info_url": "%s/p/{coding_project_name}/code-analysis/repos/{repo_id}/projects/{project_id}/codelint-issues?severity=4&scan_open={scan_id}&state&%s" % (
        CODING_MAIN_URL, CODING_URL_ISSUES_PARAMS),
    "warning_url": "%s/p/{coding_project_name}/code-analysis/repos/{repo_id}/projects/{project_id}/codelint-issues?severity=3&scan_open={scan_id}&state&%s" % (
        CODING_MAIN_URL, CODING_URL_ISSUES_PARAMS),
    "error_url": "%s/p/{coding_project_name}/code-analysis/repos/{repo_id}/projects/{project_id}/codelint-issues?severity=2&scan_open={scan_id}&state&%s" % (
        CODING_MAIN_URL, CODING_URL_ISSUES_PARAMS),
    "fatal_url": "%s/p/{coding_project_name}/code-analysis/repos/{repo_id}/projects/{project_id}/codelint-issues?severity=1&scan_open={scan_id}&state&%s" % (
        CODING_MAIN_URL, CODING_URL_ISSUES_PARAMS),
    "info_active_url": "%s/p/{coding_project_name}/code-analysis/repos/{repo_id}/projects/{project_id}/codelint-issues?severity=4&state=1&%s" % (
        CODING_MAIN_URL, CODING_URL_ISSUES_PARAMS),
    "warning_active_url": "%s/p/{coding_project_name}/code-analysis/repos/{repo_id}/projects/{project_id}/codelint-issues?severity=3&state=1&%s" % (
        CODING_MAIN_URL, CODING_URL_ISSUES_PARAMS),
    "error_active_url": "%s/p/{coding_project_name}/code-analysis/repos/{repo_id}/projects/{project_id}/codelint-issues?severity=2&state=1&%s" % (
        CODING_MAIN_URL, CODING_URL_ISSUES_PARAMS),
    "fatal_active_url": "%s/p/{coding_project_name}/code-analysis/repos/{repo_id}/projects/{project_id}/codelint-issues?severity=1&state=1&%s" % (
        CODING_MAIN_URL, CODING_URL_ISSUES_PARAMS),
    "info_resolved_url": "%s/p/{coding_project_name}/code-analysis/repos/{repo_id}/projects/{project_id}/codelint-issues?severity=4&state=2&%s" % (
        CODING_MAIN_URL, CODING_URL_ISSUES_PARAMS),
    "warning_resolved_url": "%s/p/{coding_project_name}/code-analysis/repos/{repo_id}/projects/{project_id}/codelint-issues?severity=3&state=2&%s" % (
        CODING_MAIN_URL, CODING_URL_ISSUES_PARAMS),
    "error_resolved_url": "%s/p/{coding_project_name}/code-analysis/repos/{repo_id}/projects/{project_id}/codelint-issues?severity=2&state=2&%s" % (
        CODING_MAIN_URL, CODING_URL_ISSUES_PARAMS),
    "fatal_resolved_url": "%s/p/{coding_project_name}/code-analysis/repos/{repo_id}/projects/{project_id}/codelint-issues?severity=1&state=2&%s" % (
        CODING_MAIN_URL, CODING_URL_ISSUES_PARAMS),
    "info_closed_url": "%s/p/{coding_project_name}/code-analysis/repos/{repo_id}/projects/{project_id}/codelint-issues?severity=4&state=3&%s" % (
        CODING_MAIN_URL, CODING_URL_ISSUES_PARAMS),
    "warning_closed_url": "%s/p/{coding_project_name}/code-analysis/repos/{repo_id}/projects/{project_id}/codelint-issues?severity=3&state=3&%s" % (
        CODING_MAIN_URL, CODING_URL_ISSUES_PARAMS),
    "error_closed_url": "%s/p/{coding_project_name}/code-analysis/repos/{repo_id}/projects/{project_id}/codelint-issues?severity=2&state=3&%s" % (
        CODING_MAIN_URL, CODING_URL_ISSUES_PARAMS),
    "fatal_closed_url": "%s/p/{coding_project_name}/code-analysis/repos/{repo_id}/projects/{project_id}/codelint-issues?severity=1&state=3&%s" % (
        CODING_MAIN_URL, CODING_URL_ISSUES_PARAMS),
    "code_measure_url": "%s/p/{coding_project_name}/code-analysis/repos/{repo_id}/projects/{project_id}/metric/cc?tab=cc&offset=0&limit=10" % CODING_MAIN_URL,

    "failure_url": "%s/p/{coding_project_name}/code-analysis/repos/{repo_id}/projects/{project_id}/scan-history?tab=scan-history" % CODING_MAIN_URL
}


class JobNotifcationManager(object):
    """节点消息通知管理
    """

    @classmethod
    def format_created_from(cls, created_from):
        """格式化来源
        """
        if created_from == "qci":
            return "coding"
        else:
            return created_from

    @classmethod
    def daily_notify_failed_job(cls, job):
        """日常通知失败的任务数据
        发送给平台管理员
        """

    @classmethod
    def notify_job_result_with_msg(cls, job, job_result_data, scheme_report_cfg):
        """以消息通知形式发送任务结果
        """
        if 0 <= job.result_code < 100:
            if cls.result_data_is_empty(job_result_data):
                notict_title = "【TCA代码分析】任务执行结果通知"
                notice_message = "您好，%s通过「%s」启动的对代码库「%s」的扫描分析任务已完成，分析任务执行 %s \n" \
                                 "" \
                                 "产品名称: %s\n" \
                                 "扫描分支: %s\n" \
                                 "\n" \
                                 "结果详情: 当前代码无变动，无需进行增量扫描，请启动全量扫描" \
                                 "结果详情: %s" \
                                 % (job.creator, cls.format_created_from(job.created_from), job.project.repo.scm_url,
                                    "成功!",
                                    job.project.project_name,
                                    job.project.branch,
                                    cls.get_detail_url(job, job_result_data.get("coding_project_name", None))
                                    )
            else:
                notict_title = "【TCA代码分析】任务执行结果通知"
                notice_message = "您好，%s通过「%s」启动的对代码库「%s」的扫描分析任务已完成，分析任务执行 %s \n" \
                                 "" \
                                 "产品名称: %s\n" \
                                 "扫描分支: %s\n" \
                                 "任务版本号: %s\n" \
                                 "\n" \
                                 "结果详情: %s" \
                                 % (job.creator, cls.format_created_from(job.created_from), job.project.repo.scm_url,
                                    "成功!",
                                    job.project.project_name,
                                    job.project.branch,
                                    cls.get_revision(job_result_data),
                                    cls.get_detail_url(job, job_result_data.get("coding_project_name", None))
                                    )
        else:
            notict_title = "【TCA代码分析】任务执行结果通知"
            notice_message = "您好，%s通过「%s」启动的对代码库「%s」的扫描分析任务已完成，分析任务执行 %s \n" \
                             "" \
                             "产品名称: %s\n" \
                             "扫描分支: %s\n" \
                             "任务版本号: %s\n" \
                             "\n" \
                             "扫描失败详情: %s\n" \
                             "详情链接: %s" \
                             % (job.creator, cls.format_created_from(job.created_from), job.project.repo.scm_url, "失败!",
                                job.project.project_name,
                                job.project.branch,
                                cls.get_revision(job_result_data),
                                errcode.interpret_code(job.result_code),
                                cls.get_detail_url(job, job_result_data.get("coding_project_name", None))
                                )
        MessageHandler.send_msg(scheme_report_cfg.msg_recipients, notict_title, notice_message)

    @classmethod
    def notify_job_result_with_mail(cls, job, job_result_data, mail_recipients, mail_ccs):
        """以邮件通知形式发送任务结果

        Todo: 完善邮件发送格式
        """
        mail_title = "【TCA 代码分析】任务执行结果通知"
        mail_message = MailContentGenerator.generate_display_content(job, job_result_data)
        MessageHandler.send_mail(mail_recipients, mail_title, mail_message, cc=mail_ccs)

    @classmethod
    def notify_job_result_with_qywework_robot(cls, job, job_result_data, qy_webhook_url):
        """以微信机器人方式通知任务结果

        Todo: 完善企业微信机器人发送格式
        """
        if 0 <= job.result_code < 100:
            if cls.result_data_is_empty(job_result_data):
                content = "%s通过「%s」启动的对代码库「%s」的扫描分析任务已完成，任务执行 %s\n" \
                          "" \
                          "产品名称: %s\n" \
                          "扫描分支: %s\n" \
                          "\n" \
                          "结果详情: 当前代码无变动，无需进行增量扫描，请启动全量扫描\n" \
                          "详情链接: %s" \
                          % (job.creator, cls.format_created_from(job.created_from), job.project.repo.scm_url, "成功!",
                             job.project.project_name,
                             job.project.branch,
                             cls.get_detail_url(job, job_result_data.get("coding_project_name", None)))
            else:
                code_lint_info, code_duplicate_info, code_cyclomaticcomplexity = \
                    job_result_data.get("code_lint_info", {}), job_result_data.get("code_metric_dup_info",
                                                                                   {}), job_result_data.get(
                        "code_metric_cc_info", {})
                issues_info = MailContentGenerator.extract_issue_info(code_lint_info.get("total_severity_detail", ''))
                active_issues_info = MailContentGenerator.extract_issue_info(
                    code_lint_info.get("active_severity_detail", ''))
                content = "%s通过「%s」启动的对代码库「%s」的扫描分析任务已完成，任务执行 %s\n" \
                          "" \
                          "产品名称:%s\n" \
                          "扫描分支:%s\n" \
                          "扫描版本号:%s\n" \
                          "\n" \
                          "结果:\n" \
                          "新增问题：致命:%d, 错误:%d, 警告:%d, 提示:%d\n" \
                          "存量问题：致命:%d, 错误:%d, 警告:%d, 提示:%d\n" \
                          "\n" \
                          "{圈复杂度} 千行平均复杂度:%.2f, 超标函数数量:%d\n" \
                          "{重复率} 重复率:%.2f, 重复文件数量:%d, 重复代码块数量%d\n" \
                          "详情链接: %s" \
                          % (job.creator, cls.format_created_from(job.created_from), job.project.repo.scm_url, "成功!",
                             job.project.project_name,
                             job.project.branch,
                             cls.get_revision(job_result_data),
                             active_issues_info.get("fatal", 0),
                             active_issues_info.get("error", 0),
                             active_issues_info.get("warning", 0),
                             active_issues_info.get("info", 0),
                             issues_info.get("fatal", {}).get("active", 0) + issues_info.get("fatal", {}).get(
                                 "resolved", 0) + issues_info.get("fatal", {}).get("closed", 0),
                             issues_info.get("error", {}).get("active", 0) + issues_info.get("error", {}).get(
                                 "resolved", 0) + issues_info.get("error", {}).get("closed", 0),
                             issues_info.get("warning", {}).get("active", 0) + issues_info.get("warning", {}).get(
                                 "resolved", 0) + issues_info.get("warning", {}).get("closed", 0),
                             issues_info.get("info", {}).get("active", 0) + issues_info.get("info", {}).get("resolved",
                                                                                                            0) + issues_info.get(
                                 "info", {}).get("closed", 0),
                             code_cyclomaticcomplexity.get("cc_average_of_lines", 0),
                             code_cyclomaticcomplexity.get("cc_open_num", 0),
                             code_duplicate_info.get("duplicate_rate", 0),
                             code_duplicate_info.get("duplicate_file_count", 0),
                             code_duplicate_info.get("duplicate_block_count", 0),
                             cls.get_detail_url(job, job_result_data.get("coding_project_name", None)))
        else:
            content = "%s通过「%s」启动的对代码库「%s」的扫描分析任务已完成，任务执行 %s\n" \
                      "" \
                      "产品名称: %s\n" \
                      "扫描分支:%s\n" \
                      "扫描版本号:%s\n" \
                      "\n" \
                      "扫描失败详情: %s\n" \
                      "详情链接: %s" \
                      % (job.creator, cls.format_created_from(job.created_from), job.project.repo.scm_url, "失败！",
                         job.project.project_name,
                         job.project.branch,
                         cls.get_revision(job_result_data),
                         errcode.interpret_code(job.result_code),
                         cls.get_detail_url(job, job_result_data.get("coding_project_name", None)))

        data = {
            "msgtype": "text",
            "text": {
                "content": content,
                "mentioned_list": [job.creator]
            }
        }
        MessageHandler.send_wework_robot(qy_webhook_url, data)

    @classmethod
    def get_revision(cls, result_data):
        """从result_data中获取扫描版本信息"""
        current_revision = None
        info_list = []
        info_list.append(result_data.get("code_lint_info", {}))
        info_list.append(result_data.get("code_metric_dup_info", {}))
        info_list.append(result_data.get("code_metric_cloc_info", {}))
        info_list.append(result_data.get("code_metric_cc_info", {}))

        for info_dict in info_list:
            current_revision = info_dict.get("scan_revision", None)
            if current_revision:
                return current_revision
        return current_revision

    @classmethod
    def get_detail_url(cls, job, coding_project_name):
        """获取各平台对应的结果详情链接
        """
        if not coding_project_name:
            detail_url = CODEDOG_MAIN_URL + "/repos/%d/projects/%d/scan_history" % (job.project.repo.id, job.project.id)
        else:
            detail_url = CODING_MAIN_URL + "/p/%s/code-analysis/repos/%d/projects/%d/scan-history?tab=scan-history" % (
                coding_project_name, job.project.repo.id, job.project.id)
        return detail_url

    @classmethod
    def update_coding_project_name(cls, job_result_data, job_id):
        """向job_result_data更新coding_project_name信息
        """
        cooperation_job = CooperationJob.objects.filter(job__id=job_id).first()
        if cooperation_job and cooperation_job.ext_str_fields:
            ext_str_fields = json.loads(cooperation_job.ext_str_fields)
            coding_project_name = ext_str_fields.get("coding_project_name", None)
            job_result_data.update({"coding_project_name": coding_project_name})
        return job_result_data

    @classmethod
    def result_data_is_empty(cls, job_result_data):
        """判断result_data是否为空
           注：仅在代码无变动且启动增量分析时会导致结果为空
        """
        scan_config_list = ["code_lint_info", "code_metric_dup_info", "code_metric_cloc_info", "code_metric_cc_info"]
        for scan_config in scan_config_list:
            if scan_config not in job_result_data or not job_result_data.get(scan_config):
                pass
            else:
                return False
        return True


class MailContentGenerator(object):
    """用以生成结果消息邮件发送内容
    """

    @classmethod
    def update_issue_info(cls, template_info, result_data):
        """向模版信息更新问题信息
        """
        codelint_enabled = False
        issues = result_data.get("code_lint_info", None)
        if not issues:
            template_info.update({"codelint_enabled": codelint_enabled})
            return template_info

        codelint_enabled = True
        template_info.update({"codelint_enabled": codelint_enabled})
        issues_info = cls.extract_issue_info(issues.get("total_severity_detail", ''))
        active_issues_info = cls.extract_issue_info(issues.get("active_severity_detail", ''))

        issue_serverity_list = ["fatal", "error", "warning", "info"]
        issue_type_list = ["active", "closed", "resolved"]
        for serverity in issue_serverity_list:
            if serverity not in issues_info:
                for type in issue_type_list:
                    template_info.update({"%s_%s" % (serverity, type): 0})
            else:
                type_issuses = issues_info.get(serverity)
                for type in issue_type_list:
                    issus_num = type_issuses.get(type, 0)
                    template_info.update({"%s_%s" % (serverity, type): issus_num})

        for serverity in issue_serverity_list:
            template_info.update({serverity: active_issues_info.get(serverity, 0)})

        return template_info

    @classmethod
    def extract_issue_info(cls, issues):
        """提取问题信息，将字符串转化为字典"""
        if not issues:
            return {}
        return json.loads(issues)

    @classmethod
    def update_duplicate_info(cls, template_info, result_data):
        """向模版信息更新重复代码信息
        """
        duplicate_enabled = False
        duplicatescan_info = result_data.get("code_metric_dup_info", None)
        if not duplicatescan_info:
            template_info.update({"duplicate_enabled": duplicate_enabled})
            return template_info

        duplicate_enabled = True
        if isinstance(duplicatescan_info, str):
            duplicatescan_info = json.loads(duplicatescan_info)
        template_info.update({
            "duplicate_enabled": duplicate_enabled,
            "duplicate_file_count": duplicatescan_info.get("duplicate_file_count", 0),
            "duplicate_block_count": duplicatescan_info.get("duplicate_block_count", 0),
            "duplicate_rate": duplicatescan_info.get("duplicate_rate", 0)
        })
        return template_info

    @classmethod
    def update_cyclomaticcomplexity_info(cls, template_info, result_data):
        """向模版信息更新圈复杂度信息
        """
        cyclomaticcomplexity_enabled = False
        cyclomaticcomplexity_info = result_data.get("code_metric_cc_info", None)
        if not cyclomaticcomplexity_info:
            template_info.update({"cyclomaticcomplexity_enabled": cyclomaticcomplexity_enabled})
            return template_info

        cyclomaticcomplexity_enabled = True
        if isinstance(cyclomaticcomplexity_info, str):
            cyclomaticcomplexity_info = json.loads(cyclomaticcomplexity_info)
        template_info.update({
            "cc_average_of_lines": "%.2f" % cyclomaticcomplexity_info.get("cc_average_of_lines", 0),
            "cc_open_num": cyclomaticcomplexity_info.get("cc_open_num", 0),
            "cyclomaticcomplexity_enabled": cyclomaticcomplexity_enabled
        })
        return template_info

    @classmethod
    def update_score_info(cls, template_info, result_data):
        """向模版信息更新得分信息
        """
        score_enabled = False
        score_info = result_data.get("code_score_info", None)
        if not score_info:
            template_info.update({"score_enabled": score_enabled})
            return template_info

        score_enabled = True
        template_info.update({
            "style_score": score_info.get("style_score", 0),
            "security_score": score_info.get("security_score", 0),
            "metric_score": score_info.get("metric_score", 0),
            "score_enabled": score_enabled
        })
        return template_info

    @classmethod
    def update_cloc_info(cls, template_info, result_data):
        """向模版信息更新代码变更信息
        """
        cloc_enabled = False
        cloc_info = result_data.get("code_metric_cloc_info", None)
        if not cloc_info:
            template_info.update({"cloc_enabled": cloc_enabled})
            return template_info

        cloc_enabled = True
        template_info.update({
            "total_line_num": cloc_info.get("total_line_num", 0),
            "add_total_line_num": cloc_info.get("add_total_line_num", 0),
            "mod_total_line_num": cloc_info.get("mod_total_line_num", 0),
            "del_total_line_num": cloc_info.get("del_total_line_num", 0),
            "code_line_num": cloc_info.get("code_line_num", 0),
            "add_code_line_num": cloc_info.get("add_code_line_num", 0),
            "mod_code_line_num": cloc_info.get("mod_code_line_num", 0),
            "del_code_line_num": cloc_info.get("del_code_line_num", 0),
            "comment_line_num": cloc_info.get("comment_line_num", 0),
            "add_comment_line_num": cloc_info.get("add_comment_line_num", 0),
            "mod_comment_line_num": cloc_info.get("mod_comment_line_num", 0),
            "del_comment_line_num": cloc_info.get("del_comment_line_num", 0),
            "blank_line_num": cloc_info.get("blank_line_num", 0),
            "add_blank_line_num": cloc_info.get("add_blank_line_num", 0),
            "mod_blank_line_num": cloc_info.get("mod_blank_line_num", 0),
            "del_blank_line_num": cloc_info.get("del_blank_line_num", 0),
            "cloc_enabled": cloc_enabled
        })
        return template_info

    @classmethod
    def update_url_info(cls, template_info, job, coding_project_name, scan_id):
        """向模版信息更新各模块链接信息
        """
        repo_id, project_id = job.project.repo.id, job.project.id
        if 0 <= job.result_code < 100:
            if not coding_project_name:
                for codedog_url in CODEDOG_URLS:
                    template_info.update({
                        codedog_url: CODEDOG_URLS[codedog_url].format(repo_id=repo_id, project_id=project_id,
                                                                      scan_id=scan_id)
                    })
            else:
                for coding_url in CODING_URLS:
                    template_info.update({
                        coding_url: CODING_URLS[coding_url].format(repo_id=repo_id, project_id=project_id,
                                                                   coding_project_name=coding_project_name,
                                                                   scan_id=scan_id)
                    })
        else:
            if not coding_project_name:
                template_info.update({
                    "project_url": CODEDOG_URLS["project_url"].format(repo_id=repo_id, project_id=project_id),
                    "failure_url": CODEDOG_URLS["failure_url"].format(repo_id=repo_id, project_id=project_id)
                })
            else:
                template_info.update({
                    "project_url": CODING_URLS["project_url"].format(repo_id=repo_id, project_id=project_id,
                                                                     coding_project_name=coding_project_name),
                    "failure_url": CODING_URLS["failure_url"].format(repo_id=repo_id, project_id=project_id,
                                                                     coding_project_name=coding_project_name)
                })

        return template_info

    @classmethod
    def generate_template_info_if_empty(cls, job, coding_project_name):
        """当结果信息为空时的展示信息
        """
        template_info = {}
        template_info.update({
            "scan_succeed": True,
            "result_msg": "成功",
            "not_empty": False,
            "creator": job.creator,
            "created_from": JobNotifcationManager.format_created_from(job.created_from),
            "repo_url": job.project.repo.scm_url,
            "repo_name": job.project.project_name,
            "repo_scm_url": job.project.repo.scm_url,
            "proj_branch": job.project.branch,
            "scanscheme_name": job.project.scan_scheme.name,
        })
        template_info = cls.update_url_info(template_info, job, coding_project_name, job.scan_id)
        template_info.update({
            "detail_url": JobNotifcationManager.get_detail_url(job, coding_project_name)
        })

        return template_info

    @classmethod
    def generate_template_info_if_succeed(cls, job, result_data, coding_project_name):
        """扫描成功时展示的结果信息
        """
        template_info = {}
        template_info.update({
            "scan_succeed": True,
            "result_msg": "成功",
            "not_empty": True,
            "scan_time": JobNotifcationManager.get_revision(result_data),
            "creator": job.creator,
            "created_from": JobNotifcationManager.format_created_from(job.created_from),
            "repo_url": job.project.repo.scm_url,
            "repo_name": job.project.project_name,
            "repo_scm_url": job.project.repo.scm_url,
            "proj_branch": job.project.branch,
            "scanscheme_name": job.project.scan_scheme.name,
        })
        template_info = cls.update_cloc_info(template_info, result_data)
        template_info = cls.update_duplicate_info(template_info, result_data)
        template_info = cls.update_issue_info(template_info, result_data)
        template_info = cls.update_score_info(template_info, result_data)
        template_info = cls.update_cyclomaticcomplexity_info(template_info, result_data)
        template_info = cls.update_url_info(template_info, job, coding_project_name, job.scan_id)

        return template_info

    @classmethod
    def generate_template_info_if_fail(cls, job, result_data, coding_project_name):
        """扫描失败时展示的结果信息
        """
        template_info = {}
        template_info.update({
            "scan_succeed": False,
            "result_msg": "失败",
            "not_empty": True,
            "scan_time": JobNotifcationManager.get_revision(result_data),
            "creator": job.creator,
            "created_from": JobNotifcationManager.format_created_from(job.created_from),
            "repo_url": job.project.repo.scm_url,
            "repo_name": job.project.project_name,
            "repo_scm_url": job.project.repo.scm_url,
            "proj_branch": job.project.branch,
            "scanscheme_name": job.project.scan_scheme.name,

            "failure_detail": errcode.interpret_code(job.result_code)  # 失败错误详情
        })

        if 100 <= job.result_code < 200:
            template_info.update({
                "failure_reason": "未知服务异常"
            })
        elif 200 <= job.result_code < 300:
            template_info.update({
                "failure_reason": "未知节点异常"
            })
        elif 300 <= job.result_code < 400:
            template_info.update({
                "failure_reason": "未知使用异常"
            })
        else:
            template_info.update({
                "failure_reason": "未知异常",
                "failure_detail": "异常原因未知，请登陆详情页面查看！"
            })

        template_info = cls.update_url_info(template_info, job, coding_project_name, job.scan_id)
        return template_info

    @classmethod
    def generate_template_info(cls, job, result_data, coding_project_name):
        """生成最终结果信息
        """
        if 0 <= job.result_code < 100:
            if JobNotifcationManager.result_data_is_empty(result_data):
                template_info = cls.generate_template_info_if_empty(job, coding_project_name)
            else:
                template_info = cls.generate_template_info_if_succeed(job, result_data, coding_project_name)
        else:
            template_info = cls.generate_template_info_if_fail(job, result_data, coding_project_name)

        return template_info

    @classmethod
    def generate_display_content(cls, job, result_data):
        """生成邮件字符串流信息
        param: job-任务数据； result_data-结果数据
        return: display_content-邮件消息内容
        """
        coding_project_name = result_data.get("coding_project_name", None)
        template_info = cls.generate_template_info(job, result_data, coding_project_name)

        template_loader = jinja2.FileSystemLoader(
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "templates"))
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template('form.html')
        display_content = template.render(template_info)

        return display_content


class JobSummaryManager(object):
    """每周任务执行情况汇总
    """

    @classmethod
    def notify_job_summary_result(cls, recipients, cc=None):
        """通知任务汇总结果信息"""
        try:
            display_content = cls.generate_summary_info()
            MessageHandler.send_mail(
                recipients=recipients,
                subject="%s至%s任务执行汇总情况" % (datetime.date.today() - datetime.timedelta(days=7), datetime.date.today()),
                message=display_content,
                cc=cc
            )

        except Exception as err:
            logger.error("[JobSummaryNotify] 每周任务执行汇总情况发送异常")
            logger.error(err)

    @classmethod
    def generate_summary_info(cls):
        """生成向html文件发送的汇总字典信息"""
        res_dict = {}
        time_point = datetime.datetime.now() - datetime.timedelta(days=7)  # 设置时间节点为一周前

        total_num = Job.objects.filter(start_time__gte=time_point).count()
        res_dict = cls.update_res_dict(res_dict, time_point, total_num)

        return cls.render_result(res_dict)

    @classmethod
    def abstract_detail(cls, time_point, info_dict, res_dict, total_num, left, right):
        """细分数据维度，提取出各区间result_code各具体报错信息的数量
        """
        CODEDOG_JOB_URL = "http://codedog.woa.com/jobs/?limit=12&offset=0&result_code_gte={result_code}&result_code_lte={result_code}"

        queryset = Job.objects.filter(start_time__gte=time_point, result_code__gte=left, result_code__lt=right)
        category_total_num = queryset.count()
        for key in info_dict:
            if "desc_%d_to_%d" % (left, right) not in res_dict:
                res_dict.update({
                    "num_%d_to_%d" % (left, right): category_total_num,
                    "ratio_%d_to_%d" % (left, right): "%.2f%%" % (int(category_total_num) / int(total_num) * 100)
                })

            res_dict.update({
                "desc_%d" % key: "%s_%d" % (info_dict[key], key),
                "num_%d" % key: queryset.filter(result_code=key).count(),
                "ratio_%d" % key: "%.2f%%" % (int(queryset.filter(result_code=key).count()) / int(total_num) * 100),
                "url_%d" % key: CODEDOG_JOB_URL.format(result_code=key)
            })

        return res_dict, category_total_num

    @classmethod
    def update_res_dict(cls, res_dict, time_point, total_num):
        """更新结果字典信息
        """
        res_dict, total_0_to_100 = cls.abstract_detail(time_point, errcode.OK_DICT, res_dict, total_num, 0, 100)
        res_dict, total_100_to_200 = cls.abstract_detail(
            time_point, errcode.SERVER_ERROR_DICT, res_dict, total_num, 100, 200)
        res_dict, total_200_to_300 = cls.abstract_detail(
            time_point, errcode.NODE_ERROR_DICT, res_dict, total_num, 200, 300)
        res_dict, total_300_to_400 = cls.abstract_detail(
            time_point, errcode.CLIENT_ERROR_DICT, res_dict, total_num, 300, 400)

        res_dict.update({
            "num_of_success_job": total_0_to_100,
            "num_of_fail_job": total_100_to_200 + total_200_to_300 + total_300_to_400,
            "num_of_total_job": total_num,
            "percentage_of_success_job": "%.2f%%" % ((total_0_to_100 / total_num) * 100),
            "percentage_of_fail_job": "%.2f%%" % ((1 - (total_0_to_100 / total_num)) * 100),
            "percentage_of_total_job": "100%"
        })

        return res_dict

    @classmethod
    def render_result(cls, res_dict):
        """渲染结果数据
        """
        template_loader = jinja2.FileSystemLoader(
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "templates"))
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template('job_summary.html')
        display_content = template.render(res_dict)

        return display_content
