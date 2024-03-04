# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
tca quick scan
"""


import os
import json
import logging

from node.app import settings
from node.localtask.status import StatusType
from util.logutil import LogPrinter
from util.pathfilter import FilterPathUtil
from util.pathlib import PathMgr
from node.quicktask.params import JobParams
from util.errcode import E_NODE_TASK_CONFIG
from util.exceptions import NodeError


logger = logging.getLogger(__name__)


class QuickScan(object):
    @staticmethod
    def is_quick_scan():
        """
        判断是否快速分析模式
        :return:
        """
        if os.getenv("TCA_QUICK_SCAN") == "True":
            return True
        else:
            return False

    @staticmethod
    def get_task_json_files(config_dir, languages):
        """
        从对应标签的配置目录中读取需要的任务参数json文件
        目录结构：
            |- label_name
               |- tool_name.json    适用于所有语言的任务
               |- language_name     语言类型名
                  |- tool_name.json 适用于指定语言的任务
        """
        task_json_paths = []
        for f_name in os.listdir(config_dir):
            f_path = os.path.join(config_dir, f_name)
            if os.path.isdir(f_path):  # 如果是个目录，则目录名为语言类型，如果在需要扫描的语言列表中，则添加到list
                if not languages or (languages and f_name in languages):
                    for json_name in os.listdir(f_path):
                        json_path = os.path.join(f_path, json_name)
                        task_json_paths.append(json_path)
            else:  # 如果是文件，表示适用于所有语言，直接添加到list
                task_json_paths.append(f_path)
        # logger.info(f">> task_json_paths: {task_json_paths}")
        return task_json_paths

    @staticmethod
    def get_scan_tasks(languages, labels, input_params):
        """获取工具任务参数"""
        tasks = []
        # 使用标签指定工具规则类型(标签优先使用命令行参数，其次从 input_params 中获取)
        if not labels:
            labels = input_params.get("labels", [])
        if labels:
            for label in labels:
                config_dir = os.path.join(settings.TOOL_BASE_DIR, f"quickscan/tasks/{label}")
                if not os.path.exists(config_dir):
                    raise NodeError(code=E_NODE_TASK_CONFIG,
                                    msg=f"config dir({config_dir}) not exist, please init tca.")
                new_task_json_files = QuickScan.get_task_json_files(config_dir, languages)

                new_tasks = []
                for file_path in new_task_json_files:
                    if not file_path.endswith(".json"):
                        continue
                    with open(file_path, "r") as rf:
                        task_config = json.load(rf)
                    new_tasks.append(task_config)
                # 不同的标签可能会包含同样的工具，这里通过merge合并相同工具
                tasks = QuickScan.merge_tasks(tasks, new_tasks)
        else:
            raise NodeError(code=E_NODE_TASK_CONFIG, msg=f"no label param, please specify lable by --label.")
        # LogPrinter.info(f"----->>> tasks: {[task['task_name'] for task in tasks]}")
        return tasks

    @staticmethod
    def get_proj_config(scm_url, languages, labels, input_params):
        # logger.info(f"===>>>> scm_url: {scm_url}")
        # logger.info(f"===>>>> languages: {languages}")
        JobParams.job_context["scm_url"] = scm_url

        tasks = QuickScan.get_scan_tasks(languages, labels, input_params)

        project_config = {
            "job_context": JobParams.job_context,
            "tasks": tasks
        }
        return project_config

    @staticmethod
    def merge_tasks(task_list, new_tasks):
        """将新task列表添加到原有task参数列表中，合并去重，一个工具只保留一个task"""
        task_dict = {}
        for task in task_list:
            task_name = task["task_name"]
            task_dict[task_name] = task

        for task in new_tasks:
            task_name = task["task_name"]
            if task_name in task_dict:
                new_rule_list = task["task_params"]["rule_list"]
                rule_list = task_dict[task_name]["task_params"]["rule_list"]
                task_dict[task_name]["task_params"]["rule_list"] = QuickScan.merge_rule_list(rule_list, new_rule_list)

                new_rules = task["task_params"]["rules"]
                rules = task_dict[task_name]["task_params"]["rules"]
                rules.extend(new_rules)
                task_dict[task_name]["task_params"]["rules"] = list(set(rules))
            else:
                task_dict[task_name] = task
        return list(task_dict.values())

    @staticmethod
    def merge_rule_list(rule_list, new_rule_list):
        """合并rule list, 如果规则相同，使用新规则参数替换原有规则参数"""
        rule_dict = {}
        for rule_info in rule_list:
            name = rule_info["name"]
            rule_dict[name] = rule_info
        for new_rule_info in new_rule_list:
            name = new_rule_info["name"]
            rule_dict[name] = new_rule_info
        return list(rule_dict.values())

    @staticmethod
    def get_scan_files_in_dir(source_dir, sub_dir, exclude_regex):
        dir_path = os.path.join(source_dir, sub_dir)
        if not dir_path.startswith(source_dir):
            LogPrinter.error(f"Wrong dir: {sub_dir}, skip!")
            return []
        file_paths = PathMgr().get_dir_files(dir_path)
        relpos = len(source_dir) + 1
        task_params = {
            "path_filters": {
                "inclusion": [],
                "exclusion": exclude_regex
            }
        }
        filtered_paths = FilterPathUtil(task_params).get_include_files(file_paths, relpos)
        rel_paths = [path[relpos:] for path in filtered_paths]
        # logger.info(f"{len(rel_paths)} files in {sub_dir} to scan: {rel_paths}")
        return rel_paths

    @staticmethod
    def get_path_filters(input_params=None):
        """获取过滤路径"""
        if not input_params:
            input_params = QuickScan.get_input_params()

        regex_include_paths = []
        regex_exclude_paths = []

        scan_paths = input_params.get("scan_path", [])
        for path_info in scan_paths:
            if path_info["type"] == "file":
                regex_include_paths.append(path_info["path"])
            elif path_info["type"] == "dir":
                path = path_info["path"]
                if path == "":  # 空字符串的目录，表示代码根目录
                    include_path = ".*"
                else:
                    include_path = path_info["path"].rstrip('/')
                    if not include_path:
                        LogPrinter.error(f"Skip wrong dir: {path_info['path']}")
                        continue
                    include_path = f"{include_path}/.*"
                regex_include_paths.append(include_path)
                exclude_regex = path_info.get("exclude_regex", [])
                if exclude_regex:
                    regex_exclude_paths.extend(path_info["exclude_regex"])

        return {
                   "inclusion": [],
                   "exclusion": [],
                   "re_inclusion": regex_include_paths,
                   "re_exclusion": regex_exclude_paths
               }

    @staticmethod
    def get_input_params(scan_files=None):
        """
        从json文件中获取输入参数
        """
        if scan_files:  # 如果命令行指定了扫描文件路径，直接使用
            scan_rel_paths = []
            for rel_path in scan_files:
                scan_rel_paths.append({
                    "path": rel_path,
                    "type": "file"
                })
            return {
                "scan_path": scan_rel_paths
            }

        params = {}
        input_env_key = "TCA_QUICK_SCAN_INPUT"
        input_file_env = os.getenv(input_env_key)
        if input_file_env:
            input_file_path = os.path.abspath(input_file_env)
            if os.path.exists(input_file_path):
                with open(input_file_path, "r") as rf:
                    params = json.load(rf)
        else:
            LogPrinter.warning(f"env {input_env_key} not exists, scan the source dir.")
            # 未指定扫描路径，扫描整个代码仓库目录
            params = {
                "scan_path": [
                    {
                        "path": "",  # 空字符串的目录，表示代码根目录
                        "type": "dir"
                    }
                ]
            }
        return params

    @staticmethod
    def get_scan_paths(params, source_dir):
        """获取需要扫描的文件列表（相对路径）"""
        path_info_dict = {}
        scan_rel_paths = []
        scan_paths = params.get("scan_path", [])
        for path_info in scan_paths:
            if path_info["type"] == "file":
                path = path_info.get("path")
                lines = path_info.get("lines", [])
                if path:
                    scan_rel_paths.append(path)
                    path_info_dict[path] = lines  # 指定文件时，可以指定改动的代码行，供过滤结果使用
            elif path_info["type"] == "dir":
                exclude_regex = path_info.get("exclude_regex", [])
                rel_paths = QuickScan.get_scan_files_in_dir(source_dir, path_info["path"], exclude_regex)
                for path in rel_paths:
                    if path not in scan_rel_paths:
                        scan_rel_paths.append(path)
                        path_info_dict[path] = []  # 指定目录时，不支持指定改动代码行，为空，表示扫描整个文件
        return scan_rel_paths, path_info_dict

    @staticmethod
    def get_result(proj_scan_succ, error_code, error_msg):
        if proj_scan_succ:
            status = StatusType.SUCCESS
            text = "分析成功"
        else:
            status = StatusType.ERROR
            text = "分析异常"
        scan_result = {
            "status": status,
            "error_code": error_code,
            "text": text,
            "description": error_msg,
        }
        return scan_result

    def generate_qucik_scan_report(self, scan_path_info, result, task_result_paths, task_rules):
        """
        从各个taskdir中读取本地分析结果issues（暂时只读取代码检查结果）

        代码度量结果（除了圈复杂度是在issue_dir目录，其他都在单独一个json里）：
        1. 本次分析的代码行数据：local_task_88/codeline_data.json
        2. 重复代码结果（cpd工具）：local_task_89/task_response.json
        3. 圈复杂度结果（lizard工具）：local_task_90/workdir/issue_dir/
        4. 代码统计结果（codecount工具）：local_task_91/task_response.json

        代码检查结果（都在issue_dir目录）：
        1. 代码检查-customfilescan工具结果：local_task_92/workdir/issue_dir
        2. 代码检查-regexscan工具结果：local_task_93/workdir/issue_dir
        :return:
        """
        rule_severity = ["fatal", "error", "warning", "info"]
        report_path = os.getenv("TCA_QUICK_SCAN_OUTPUT", "tca_quick_scan_report.json")
        report_path = os.path.abspath(report_path)

        total_path_issues = {}
        total_issues_cnt = 0
        security_count = {
            "fatal": 0,
            "error": 0,
            "warning": 0,
            "info": 0
        }
        for task_name, result_path in task_result_paths.items():
            if QuickScan.is_quick_scan():
                # 输出debug log,方便问题定位
                logger.debug("*" * 100)
                task_log = os.path.join(os.path.dirname(result_path), "task.log")
                with open(task_log, 'r') as rf:
                    logger.debug(rf.read())
                logger.debug("*" * 100)

            with open(result_path, "r") as rf:
                response_data = json.load(rf)
            file_issues = response_data["result"]

            if file_issues:
                # 收集当前task用到的规则信息
                rule_info_dict = {}
                rule_list = task_rules[task_name]
                for rule_params in rule_list:
                    rule_info_dict[rule_params["name"]] = rule_params

                for file_issue in file_issues:
                    path = file_issue.get("path")
                    path = path.replace(os.sep, '/')  # windows分隔符先转换成unix分隔符，再比较

                    issues = file_issue.get("issues", [])
                    for issue in issues:
                        # 检查行号和列号，统一为int类型
                        issue["line"] = int(issue["line"])
                        issue["column"] = int(issue.get("column", 1))

                        if path not in scan_path_info:  # 不在需要扫描的文件中，过滤掉
                            if issue["rule"] != "FilesNotFound":  # 该规则是检查文件不存在，是个例外
                                logger.info(f"skip filtered path: {path}")
                                continue

                        if path in scan_path_info:
                            lines = scan_path_info[path]
                            if lines:
                                lineno = issue["line"]
                                if lineno not in lines:  # 如果指定了代码行，过滤不在代码行列表中的问题
                                    # logger.info(f"skip filtered code, line number: {lineno} ({path})")
                                    continue

                        if issue.get("resolution") == 8:  # 通过注释忽略的问题，过滤掉
                            LogPrinter.info(f"comment igonre: {path}, {issue}")
                            continue

                        # 补充规则信息
                        rule_info = rule_info_dict.get(issue["rule"], {})
                        rule_severity_int = rule_info.get("severity")
                        if rule_severity_int in [1, 2, 3, 4]:
                            issue["severity"] = rule_severity[rule_severity_int - 1]
                        else:
                            LogPrinter.warning(
                                f"Wrong rule severity, change to Error: \n{json.dumps(issue, indent=2)}")
                            issue["severity"] = "Error"
                        security_count[issue["severity"]] += 1
                        # issue["tool_name"] = rule_info.get("tool_name")  # issue中已经有checker字段
                        issue["rule_title"] = rule_info.get("rule_title")

                        total_issues_cnt += 1
                        if path in total_path_issues:
                            total_path_issues[path].append(issue)
                        else:
                            total_path_issues[path] = [issue]

        result["issue_count"] = total_issues_cnt
        result["security_count"] = security_count
        result["issue_detail"] = total_path_issues

        if "code_line" in result:
            result.pop("code_line")
        with open(report_path, "wb") as status_obj:
            status_obj.write(str.encode(json.dumps(result, indent=2, ensure_ascii=False)))
        LogPrinter.info(f"tca qucik scan report path: {report_path}")
