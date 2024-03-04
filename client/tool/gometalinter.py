#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
gometalinter: Concurrently run Go lint tools and normalise their output.
"""

import os
import shlex

from task.codelintmodel import CodeLintModel
from task.scmmgr import SCMMgr
from util.logutil import LogPrinter
from util.pathfilter import FilterPathUtil
from util.pathlib import PathMgr
from util.subprocc import SubProcController
from tool.util.toolenvset import ToolEnvSet
from task.basic.common import subprocc_log
from node.app import settings
from util.exceptions import AnalyzeTaskError

logger = LogPrinter

SPLIT = "[CODEDOG]"
GOLINT = {
    "golint/time",
    "golint/range",
    "golint/comment",
    "golint/unexported_type_in_api",
    "golint/package",
    "golint/op",
    "golint/naming",
    "golint/indent",
    "golint/imports",
    "golint/context",
    "golint/errors" "golint/arg_order",
    "goimports/import",  # 这里因为代码规范包含goimports但其实只是格式化工具并不会报错
}


def build_error_check(result):

    if "gotype" == result and "could not import" in result:
        return True

    if "error:" in result and "No such file or directory" in result:
        return True

    if "unknown field" in result and "struct literal" in result:
        return True

    if "not declared by package" in result:
        return True

    if "package" in result and "expected" in result:
        return True

    if result.count("[CODEDOG]") < 3:
        return True
    return False


class Gometalinter(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.sensitive_word_maps = {
            "gometalinter": "Tool",
            "GometaLinter": "Tool",
            "golint": "Tool",
            "gosec": "Tool",
            "goimport": "Tool",
        }
        # 这里之前过滤在扫描时做了，这里没必要再次过滤。
        self._filters = []

    def analyze(self, params):
        """
        分析执行函数
        :param params: 分析所需要的资源 1.项目地址 2.工作地址 3.分析参数
        :return:
        """
        source_dir = params.source_dir
        self.pos = len(source_dir) + 1
        work_dir = os.getcwd()
        rules = set(params["rules"])
        logger.info(rules)
        incr_scan = params["incr_scan"]
        build_cmd = params.get("build_cmd", None)
        path_exclude = params.path_filters.get("wildcard_exclusion", [])
        # filter_mgr = FilterPathUtil(params)

        error_output = os.path.join(work_dir, "result.json")

        ToolEnvSet.set_go_env(params)
        # 设置GOROOT，否则gometalinter可能会报错
        if not os.environ.get("GOROOT"):
            os.environ["GOROOT"] = os.path.join(settings.TOOL_BASE_DIR, os.path.basename(os.environ.get("GO_HOME")))
            logger.info("GOROOT: %s" % os.environ.get("GOROOT", ""))
        go_path = os.environ.get("GOPATH")
        if not go_path:
            os.environ["GOPATH"] = os.pathsep.join([source_dir, os.path.join(settings.TOOL_BASE_DIR, "go-1.12.6/go")])
            logger.info("GOPATH: %s" % os.environ.get("GOPATH", ""))

        if build_cmd:
            logger.info("build_cmd: %s" % build_cmd)
            go_buid_cmd = shlex.split(build_cmd)
            rtcode = SubProcController(
                go_buid_cmd, cwd=source_dir, stdout_line_callback=subprocc_log, stderr_line_callback=subprocc_log
            ).wait()
            if rtcode != 0:
                logger.error("go项目编译失败，建议客户保证项目编译通过，否则可能导致部分依赖编译的规则出现漏报！")
        logger.info(rules - GOLINT)
        only_standard = False
        issues = []
        rule_set = set(rules)
        if rules & GOLINT:
            # 如果有golint规则则单独执行
            if not rules - GOLINT:
                only_standard = True
            # 扫描增全量
            issues.extend(self._run_golint(params))
        if not only_standard:
            # gometalinter执行扫描
            # 需要设置deadline，默认是30s，超出之后会杀掉对应linter进程
            # 切割 [CODEDOG] 获取规则信息解析issue
            scan_cmd = [
                "gometalinter",
                "--debug",
                "--vendor",
                "--line-length=120",
                "--sort=path",
                "--enable-gc",
                "--deadline=%ss" % str(os.environ.get("GOMETALINTER_DEADLINE", "300")),
                "--format={{.Path.Abs}}'[CODEDOG]'{{.Line}}'[CODEDOG]'{{.Linter}}'[CODEDOG]'{{.Message}}",
                "-j 2",
            ]
            # 修改为所有规则扫描，再基于结果过滤
            scan_cmd.extend(
                [
                    "--enable-all",
                    "--disable=gocyclo",
                    "--disable=dupl",
                    "--disable=testify",
                    "--disable=test",
                    "--disable=lll",
                    "--disable=gotype",
                    "--disable=gotypex",
                    "--disable=megacheck",
                    "--disable=unconvert",
                    "--disable=vet",
                    "--disable=golint",
                ]
            )

            if path_exclude:
                # 直接是目录名，只支持dir/.*模式，不支持直接过滤文件的形式
                exclusion = list()
                for path in path_exclude:
                    if path.endswith("/*") and path.count("*") == 1:
                        exclusion.append("--skip=" + path[:-2])
                scan_cmd.extend(exclusion)
            # 默认过滤库文件
            # 除非设置GOMETALIINTER_VENDOR=flase
            # GOMETALINTER_FILTER用来增加需要过滤的目录，也可以通过设置扫描路径过滤的方式
            if "GOMETALIINTER_VENDOR" not in os.environ:
                # 这里逻辑有错误, 会默认过滤所有文件夹, 因为EPC考核内卷, 不想大部分增加错误故先保留该逻辑, 之后温水煮青蛙
                if os.environ.get("GOMETALINTER_VERSION", "new") == "EPC":
                    # ''空字符串split ',' 返回 ['']; endswith('')永远为True
                    self._filters.extend(os.environ.get("GOMETALINTER_FILTER", "").split(","))
                # 这是正常的过滤逻辑
                elif "GOMETALINTER_FILTER" in os.environ:
                    self._filters.extend(os.environ.get("GOMETALINTER_FILTER").split(","))
                scan_cmd.extend(
                    ["--skip=%s" % d[self.pos :] for d in self._get_package_path(source_dir, tuple(self._filters))]
                )

            # 工具额外配置
            if os.environ.get("GOMETALINTER_OPTION_PARAMS", None):
                scan_cmd.extend(shlex.split(os.environ.get("GOMETALINTER_OPTION_PARAMS")))
            # 增量时候扫描文件，部分小工具只能扫描目录，会扫描失败，所以该会全量
            scan_cmd.append("./...")
            self.print_log("scan_cmd: %s" % " ".join(scan_cmd))
            SubProcController(
                scan_cmd,
                cwd=source_dir,
                stdout_filepath=error_output,
                stderr_line_callback=self._error_callback,
                shell=True,
            ).wait()
            issues.extend(self._get_issues(error_output, rule_set, incr_scan, False))
            logger.info(issues)

        return issues

    def _run_golint(self, params):
        """golint部分单独执行加快风格分析效率
        """
        scan_cmd = ["golint_standard"]
        source_dir = params.source_dir
        rules = set(params["rules"])
        work_dir = os.getcwd()
        scan_cmd = ["golint_standard"]
        if not rules - GOLINT:
            only_standard = True
        # 扫描增全量
        toscans = []
        want_suffix = [".go"]
        incr_scan = params["incr_scan"]
        if incr_scan:
            diffs = SCMMgr(params).get_scm_diff()
            toscans = [
                os.path.join(source_dir, diff.path).replace(os.sep, "/")
                for diff in diffs
                if diff.path.endswith(tuple(want_suffix)) and diff.state != "del"
            ]
            toscans = FilterPathUtil(params).get_include_files(toscans, self.pos)
        else:
            toscans = [
                path.replace(os.sep, "/") for path in PathMgr().get_dir_files(source_dir, tuple(want_suffix))
            ]
            # filter include and exclude path
            toscans = FilterPathUtil(params).get_include_files(toscans, self.pos)
        if not toscans:
            logger.debug("To-be-scanned files is empty ")
            return []
        issues = []
        error_output = os.path.join(work_dir, "result.json")
        for toscan in toscans:
            scan_cmd.append(toscan)
            logger.info("scan %s" % scan_cmd)
            SubProcController(
                scan_cmd,
                cwd=source_dir,
                stdout_filepath=error_output,
                stderr_line_callback=self._error_callback,
                shell=True,
            ).wait()
            issues.extend(self._get_issues(error_output, rules, incr_scan, True))
            scan_cmd.pop()
        return issues

    def _get_issues(self, error_output, rule_set, is_inc, is_standard):
        """ """
        issues = []
        if os.path.exists(error_output):
            with open(error_output, "r") as rf:
                lines = rf.readlines()
                for line in lines:
                    if build_error_check(line):
                        continue
                    result = line.split(SPLIT)
                    # logger.info(result)
                    # 非增量gometalinter是返回绝对路径，但是golint是返回相对路径；执行路径为代码库路径情况
                    if os.path.isabs(result[0]):
                        path = result[0][self.pos :]
                    else:
                        path = result[0]  # 路径为第一个
                    line_num = result[1]
                    msg = result[3]
                    if is_standard:
                        rule = msg.split("-")[0]
                    elif msg.find("golint") >= 0 or result[2] == "golint":  # 是否为golint规则
                        rule = msg.split("-")[0]
                    else:
                        rule = result[2]
                    if rule in rule_set:
                        # logger.info("rule %s" % rule)
                        # logger.info(result)
                        issues.append(
                            {
                                "line": int(line_num),
                                "column": 0,
                                "rule": rule,
                                "path": path,
                                "msg": msg,
                            }
                        )
        return issues

    def _get_package_path(self, root_dir, filters):
        """

        :param root_dir:
        :return:
        """
        dirs = list()
        filelist = os.listdir(root_dir)
        for file in filelist:
            path = os.path.join(root_dir, file).replace("\\", "/")
            if not os.path.isdir(path):
                continue
            # logger.info('filter is : %s', filters)
            if path.endswith(filters):
                dirs.append(path)
                # logger.info('filter done: %s', path)
            else:
                dirs.extend(self._get_package_path(path, filters))
        return dirs

    def _error_callback(self, line):
        """
        异常捕获
        :param line:
        :return:
        """
        self.print_log(line)

        if line.find("gometalinter: error: user: Current not implemented on linux/amd64") != -1:
            raise AnalyzeTaskError("检查GOPATH是否为空，若为空，则麻烦设置GOPATH指向项目依赖路径，然后重试。")

    def check_tool_usable(self, tool_params):
        """
        这里判断机器是否支持运行gometalinter
        1. 支持的话，便在客户机器上扫描
        2. 不支持的话，就发布任务到公线机器扫描
        :return:
        """
        if SubProcController(["gometalinter", "--version"]).wait() != 0:
            return []
        return ["analyze"]


tool = Gometalinter

if __name__ == "__main__":
    pass
