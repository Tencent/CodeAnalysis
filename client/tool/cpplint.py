# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
cpplint 扫描任务
"""


import os
import re
import time
import threading
from functools import reduce

from task.scmmgr import SCMMgr
from util.logutil import LogPrinter
from util.pathlib import PathMgr
from node.common.processmgr import ProcMgr
from task.codelintmodel import CodeLintModel
from util.pathfilter import FilterPathUtil
from util.configlib import ConfigReader
from util.subprocc import SubProcController
from util.scanlang.callback_queue import CallbackQueue


logger = LogPrinter


class ResultMgr(object):
    """
    结果处理类
    """

    def parse_result(self, regex_client, cmd_output):
        """解析cpplint执行输出信息"""
        errors = []
        for line in cmd_output:
            reg_result = regex_client.findall(line)
            if reg_result:
                item = {}
                file_path, line_num, item['error_msg'], item['error_type'], item['error_level'] = reg_result[0]
                # 因为多线程执行的原因,读取到的stdout输出,路径前可能包含很多空字符,需要过滤掉
                if "\u0000" in file_path:
                    logger.warning("fix file_path(%s)." % file_path)
                    file_path = file_path.replace("\u0000", "")
                item["file_path"] = file_path
                line_num = int(line_num)
                item["line_num"] = line_num if line_num > 0 else 1
                errors.append(item)
        return errors

    def __format_message(self, source_dir, msg):
        """
        格式化issue的msg信息，如果msg中带有代码目录绝对路径，删除，只保留相对路径部分
        :param msg:
        :return:
        """
        if "/" in source_dir:
            src_dir_prefix = source_dir + "/"
        else:
            src_dir_prefix = source_dir + "\\"
        if src_dir_prefix in msg:
            msg = msg.replace(src_dir_prefix, "")
        return msg

    def format_result(self, source_dir, scan_result, rules):
        """格式化工具执行结果"""
        issues = []
        relpos = len(source_dir) + 1
        # scan_result 字典数组去重
        f = lambda x, y: x if y in x else x + [y]
        scan_result = reduce(
            f,
            [
                [],
            ]
            + scan_result,
        )
        # 格式化结果
        for error in scan_result:
            rule_name = error["error_type"]
            # 结果可能包含不需要扫描的规则，过滤掉
            if rules and rule_name not in rules:
                logger.debug("ignore rule:%s" % rule_name)
                continue
            issue = {}
            issue["path"] = error["file_path"][relpos:]
            issue["line"] = error["line_num"]
            issue["column"] = "1"
            issue["msg"] = self.__format_message(source_dir, error["error_msg"])
            issue["rule"] = rule_name
            issues.append(issue)
        return issues


class CpplintRunner(object):
    def __init__(self):
        self.cmd_output = []

    def __collect_result_callback__(self, line):
        """单行输出回调,收集结果"""
        self.cmd_output.append(line)

    def run_cpplint_on_files(self, toscans, cmd_args, regex_client, source_dir, rules):
        """逐个扫描多个文件"""
        issues = []
        for file_path in toscans:
            file_issues = self.run_cpplint_on_file(file_path, cmd_args, regex_client, source_dir, rules)
            if file_issues:
                issues.extend(file_issues)
        return issues

    def run_cpplint_on_file(self, file_path, cmd_args, regex_client, source_dir, rules):
        """扫描单个文件"""
        # 先置空，以免上一个影响
        self.cmd_output = []
        cmd = cmd_args + ["\"%s\"" % file_path]
        logger.info("scan file: %s" % file_path)
        # cpplint的error信息通过stderr通道输出,结果统计信息通过stdout通道输出,可以只解析stderr结果
        subProC = SubProcController(cmd, stderr_line_callback=self.__collect_result_callback__)
        try:
            subProC.wait(timeout=300)  # 设置cpplint分析单个文件超时为5分钟，避免cpplint卡死的情况
        except Exception as err:
            if "SubProcControllerTimeout" in str(err):
                logger.error(
                    "timeout when run on file(%s): %s. Kill this process(%s)..." % (file_path, str(err), subProC.pid)
                )
                ProcMgr().kill_proc_famliy(subProC.pid)
            else:
                logger.error("error on file(%s): %s" % (file_path, err))
                raise

        # 解析cpplint原始结果
        scan_result = ResultMgr().parse_result(regex_client, self.cmd_output)

        # 转换成codedog最终结果格式
        file_issues = ResultMgr().format_result(source_dir, scan_result, rules)
        return file_issues


class ThreadRunner(object):
    """多线程执行类"""

    def __init__(self, cmd_args, regex_client, source_dir, rules):
        self.cmd_args = cmd_args
        self.regex_client = regex_client
        self.source_dir = source_dir
        self.rules = rules
        self.issues = []
        self.mutex = threading.Lock()  # 线程锁,访问全局变量时需要上锁

    def __scan_file_callback__(self, file_path):
        file_result = CpplintRunner().run_cpplint_on_file(
            file_path, self.cmd_args, self.regex_client, self.source_dir, self.rules
        )
        self.mutex.acquire()  # 上锁
        self.issues.extend(file_result)
        self.mutex.release()  # 解锁

    def run(self, file_paths):
        callback_queue = CallbackQueue(min_threads=20, max_threads=1000)
        for path in file_paths:
            callback_queue.append(self.__scan_file_callback__, path)
        callback_queue.wait_for_all_callbacks_to_be_execute_and_destroy()
        return self.issues


class Cpplint(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.sensitive_word_maps = {"Cpplint": "Tool", "cpplint": "Tool"}
        pass

    want_suffix = (
        ".c",
        ".cc",
        ".h",
        ".hpp",
        ".c++",
        ".h++",
        ".cpp",
        ".hxx",
        ".cxx",
    )

    def __prepare_cpplint_args(self, source_dir, rules, linelength, project_name):
        """
        准备cpplint命令行执行参数
        :param source_dir:
        :param rules:
        :return:
        """
        # 可以设置使用用户自己维护的cpplint，但需要注意的是 用户的cpplint独有的规则，可能会被过滤掉
        cpplint_path = os.environ.get("CPPLINT_PATH", None)
        if cpplint_path:
            cpplint_path = os.path.join(source_dir, cpplint_path)
        else:
            # 默认使用puppy集成的版本
            cpplint_path = os.path.join(os.environ.get("CPPLINT_HOME"), "cpplint.py")

        cmd_args = [
            "python",
            "\"%s\"" % cpplint_path,
            "--repository=\"%s\"" % source_dir,
            "--linelength=%s" % linelength,
            "--headers=h,hpp,cuh,hxx,h++",
        ]

        file_extensions = os.environ.get("EXTENSIONS")
        if file_extensions:
            cmd_args.append("--extensions=" + file_extensions)
            logger.info("扫描文件为 %s" % file_extensions)
        if project_name:
            if project_name.find(".git") != -1:
                project_name = project_name.replace(".git", "")
            cmd_args.append("--root=%s" % project_name)
        if rules:
            filter_arg = "--filter=-,+" + ",+".join(rules)
            cmd_args.append(filter_arg)
        return cmd_args

    def __get_linelength_param(self, params):
        """
        获取最大行长度参数
        :param params:
        :return:
        """
        # 1. 从环境变量里获取
        linelength = os.environ.get("CPPLINT_LINELENGTH", None)
        if linelength:
            return linelength

        # 2. 从规则参数中获取
        rule_list = params["rule_list"]
        rule_params = None
        # 找到linelength规则
        for rule_info in rule_list:
            if rule_info["name"] == "whitespace/line_length":
                rule_params = rule_info["params"]
                break
        # 解析linelength规则参数
        if rule_params:
            rule_params = "[linelength]\r\n" + rule_params
            rule_params_dict = ConfigReader(cfg_string=rule_params).read("linelength")
            if "max" in rule_params_dict:
                return rule_params_dict["max"]

        # 3. 默认使用腾讯C++代码规范的行长度标准值
        return "100"

    def analyze(self, params):
        """执行cpplint扫描任务
        :param params: 需包含下面键值：
           'rules'： lint扫描的规则列表
           'incr_scan' : 是否增量扫描
        :return: return a :py:class:`IssueResponse`
        """
        source_dir = params.source_dir
        rules = params["rules"]
        incr_scan = params["incr_scan"]

        path_mgr = PathMgr()

        if incr_scan:
            diffs = SCMMgr(params).get_scm_diff()
            toscans = [
                os.path.join(source_dir, diff.path)
                for diff in diffs
                if diff.path.endswith(self.want_suffix) and diff.state != "del"
            ]
        else:
            toscans = path_mgr.get_dir_files(source_dir, self.want_suffix)

        # filter include and exclude path
        relpos = len(source_dir) + 1
        toscans = FilterPathUtil(params).get_include_files(toscans, relpos)

        if not toscans:
            logger.info("To-be-scanned files is empty ")
            return []
        else:
            logger.info("toscans: %s" % len(toscans))

        # 执行cpplint工具
        start_time = time.time()
        reg_client = re.compile(r"^(.+?):(\d+):\s+(.+?)\s+\[([\S]+)\]\s+\[(\d+)\]$")
        max_linelength = self.__get_linelength_param(params)
        # 获取项目名称
        project_name = None
        scm_type = params.get("scm_type")
        if "git" == scm_type:  # git仓库
            project_name = params.get("scm_url")
            if project_name.find("#") != -1:
                project_name = project_name.split("#")[0]
            project_name = project_name.split("/")[-1]
            project_name = project_name.replace(".git", "")
        elif "svn" == scm_type:  # svn项目
            project_name = params.get("scm_url").split("/")[-1].split("_proj")[0]
        cmd_args = self.__prepare_cpplint_args(source_dir, rules, max_linelength, project_name)

        self.print_log("run cmd on every file: %s" % " ".join(cmd_args))

        # 多线程执行cpplint
        issues = ThreadRunner(cmd_args, reg_client, source_dir, rules).run(toscans)

        # 单线程执行cpplint
        # issues = CpplintRunner().run_cpplint_on_files(toscans, cmd_args, reg_client, source_dir, rules)

        logger.info(" use time: %s" % (time.time() - start_time))
        logger.info("issues len: %s" % len(issues))
        if not issues:
            logger.info("result is empty ")

        return issues

    def check_tool_usable(self, tool_params):
        """
        这里判断Linux机器是否有python环境，没有的话便把任务发布给其他公线机器执行
        :return:
        """
        if SubProcController(["python", "--version"]).wait() != 0:
            return []
        return ["analyze"]


tool = Cpplint

if __name__ == "__main__":
    pass
