#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
Infer: a code static analyzer for c/c++/oc/java.
"""

import shlex
import os
import json

from util.subprocc import SubProcController
from util.logutil import LogPrinter
from util.tooldisplay import ToolDisplay


class Infer(object):
    def __init__(self, sensitive):
        self.sensitive = sensitive
        self.sensitive_word_maps = {"infer": "Tool", "Infer": "Tool"}

    def compile(self, params):
        """
        编译执行函数
        :param params:
        :return:
        """
        source_dir = params.source_dir
        work_dir = os.getcwd()
        pre_cmd = params.get("pre_cmd", None)
        build_cmd = shlex.split(params.get("build_cmd", None))
        incr_scan = params.get("incr_scan", True)
        envs = params.get("envs", {})

        # get compild cwd from env var
        build_cwd = os.environ.get("BUILD_CWD", None)
        compile_cwd = os.path.join(source_dir, build_cwd) if build_cwd else source_dir

        infer_result_dir = os.path.join(work_dir, "infer_result")
        error_output = os.path.join(infer_result_dir, "report.json")

        # pre-process step
        # 可能会需要要前置命令做为clean project, 可以做全量，需要clean一下项目
        # 或者infer compile -- cmake .
        # infer compile -- ./configure
        if pre_cmd:
            SubProcController(shlex.split(pre_cmd), cwd=compile_cwd, shell=False).wait()

        # capture
        scan_capture_cmd = ["infer", "capture", "--continue", "--jobs", "8"]
        # 增量--reactive
        if incr_scan:
            scan_capture_cmd.append("--reactive")
        # 针对iOS项目，如果默认与xcpretty结合使用，但是无法扫出问题，可以尝试无需使用xcpretty，这样会以infer自带的clang来编译项目
        if envs.get("INFER_NO_XCPRETTY", False):
            scan_capture_cmd.append("--no-xcpretty")
        # 编译捕获依赖，无须源码，jar包中class文件也能做到分析转换成中间文件。--dependencies
        if envs.get("INFER_DEPENDENCES", False):
            scan_capture_cmd.append("--dependencies")
        # 指定java的bootclasspath
        if envs.get("INFER_BOOTCLASSPATH", False):
            scan_capture_cmd.append("--bootclasspath")
            scan_capture_cmd.append(envs.get("INFER_BOOTCLASSPATH"))
        # 指定buck-out的根目录
        if envs.get("INFER_BUCK_OUT", False):
            scan_capture_cmd.append("--buck-out")
            scan_capture_cmd.append(envs.get("INFER_BUCK_OUT"))
        # 编译时候指定c++头文件model，可能会导致编译失败
        if envs.get("INFER_CXX_HEADER", False):
            scan_capture_cmd.append("--cxx-infer-headers")
            scan_capture_cmd.append(envs.get("INFER_CXX_HEADER"))

        # 设置特殊的option，比如--siof-safe-methods string, --no-default-linters,  "--compute-analytics"
        # "--headers" --header会扫描头文件使耗时家长
        if "INFER_CAPTURE_PARAMS" in envs:
            scan_capture_cmd += shlex.split(envs["INFER_CAPTURE_PARAMS"])

        scan_capture_cmd.extend(["-o", infer_result_dir, "--"])
        scan_capture_cmd.extend(build_cmd)

        # 若使用gradle构建，可能会报错，可以尝试-x lint解决
        if envs.get("INFER_NO_LINTER", False):
            scan_capture_cmd.extend(["-x", "lint"])
        # 指定iOS SDK版本
        if "INFER_IPHONEOS_TARGET_SDK_VERSION" in envs:
            scan_capture_cmd.extend(["--iphoneos-target-sdk-version", envs.get("INFER_IPHONEOS_TARGET_SDK_VERSION")])
        # 另外有LD、GCC_PRECOMPILE_PREFIX_HEADER=NO可能需要设在环境变量中

        SubProcController(scan_capture_cmd, cwd=compile_cwd).wait()
        self.print_log("cmd: %s" % " ".join(scan_capture_cmd))
        return True

    def analyze(self, params):
        """
        分析执行函数
        :param params:
        :return:
        """
        source_dir = params.source_dir
        work_dir = os.getcwd()
        lang = params.lang
        envs = params.get("envs", {})
        rules = params.get("rules", None)
        infer_result_dir = os.path.join(work_dir, "infer_result")
        error_output = os.path.join(infer_result_dir, "report.json")
        build_cwd = os.environ.get("BUILD_CWD", None)
        compile_cwd = os.path.join(source_dir, build_cwd) if build_cwd else source_dir

        scan_analyze_cmd = [
            "infer",
            "analyze",
            "--print-active-checkers",
            "--ml-buckets",
            "all",
            "--no-default-checkers",
        ]
        # 全量规则
        # 根据lang加载对应语言的checker
        if lang == "java":
            scan_analyze_cmd += [
                "--annotation-reachability",
                "--check-nullable",
                "--biabduction",
                "--bufferoverrun",
                "--eradicate",
                "--fragment-retains-view",
                "--immutable-cast",
                "--printf-args",
                "--suggest-nullable",
                "--quandary",
                "--racerd",
                "--litho",
                "--cost",
                "--starvation",
                "--dump-duplicate-symbols",
            ]
        else:
            # oc、C/C++
            scan_analyze_cmd += [
                "--check-nullable",
                "--biabduction",
                "--bufferoverrun",
                "--liveness",
                "--suggest-nullable",
                "--ownership",
                "--quandary",
                "--racerd",
                "--siof",
                "--uninit",
                "--cost",
                "--dump-duplicate-symbols",
                "--unsafe-malloc",
                "--cxx",
                "--linters",
            ]
        # 开启被禁用的规则, 以及指定中间文件夹
        scan_analyze_cmd += [
            "--enable-issue-type",
            "ANALYSIS_STOPS",
            "--enable-issue-type",
            "ARRAY_OUT_OF_BOUNDS_L1",
            "--enable-issue-type",
            "ARRAY_OUT_OF_BOUNDS_L2",
            "--enable-issue-type",
            "ARRAY_OUT_OF_BOUNDS_L3",
            "--enable-issue-type",
            "BUFFER_OVERRUN_L4",
            "--enable-issue-type",
            "BUFFER_OVERRUN_L5",
            "--enable-issue-type",
            "BUFFER_OVERRUN_U5",
            "--enable-issue-type",
            "CLASS_CAST_EXCEPTION",
            "--enable-issue-type",
            "CONDITION_ALWAYS_FALSE",
            "--enable-issue-type",
            "CONDITION_ALWAYS_TRUE",
            "--enable-issue-type",
            "DANGLING_POINTER_DEREFERENCE",
            "--enable-issue-type",
            "DIVIDE_BY_ZERO",
            "--enable-issue-type",
            "GLOBAL_VARIABLE_INITIALIZED_WITH_FUNCTION_OR_METHOD_CALL",
            "--enable-issue-type",
            "INFERBO_ALLOC_MAY_BE_BIG",
            "--enable-issue-type",
            "INFERBO_ALLOC_MAY_BE_NEGATIVE",
            "--enable-issue-type",
            "INFINITE_EXECUTION_TIME_CALL",
            "--enable-issue-type",
            "NULL_TEST_AFTER_DEREFERENCE",
            "--enable-issue-type",
            "RETURN_VALUE_IGNORED",
            "--enable-issue-type",
            "STACK_VARIABLE_ADDRESS_ESCAPE",
            "--enable-issue-type",
            "UNARY_MINUS_APPLIED_TO_UNSIGNED_EXPRESSION",
            "--keep-going",
            "-o",
            infer_result_dir,
        ]
        # 设置特殊的option, 比如--no-default-checkers, --biabduction-only(在末尾生效,指定指开启biabduction-checker)
        if "INFER_ANALYZE_PARAMS" in envs:
            scan_analyze_cmd += shlex.split(envs["INFER_ANALYZE_PARAMS"])
        # run_cmd(scan_analyze_cmd, cwd=compile_cwd)
        self.print_log("cmd: %s" % " ".join(scan_analyze_cmd))
        SubProcController(scan_analyze_cmd, cwd=compile_cwd).wait()

        # 结果处理
        issues = []
        try:
            with open(error_output, "r") as f:
                raw_warning_json = json.load(f)
        except MemoryError as err:
            # 如果json结果文件过大，出现内存溢出，则使用ijson来解析json文件
            LogPrinter.info("一次性加载json文件内存溢出, 使用ijson流式读取解析的方式.")
            raw_warning_json = "json_file_too_large"

        if raw_warning_json != "json_file_too_large":  # 一次性加载json文件没有内存溢出的情况
            for issue in raw_warning_json:
                rule = issue.get("bug_type", None)
                if rule not in rules:
                    continue
                msg = issue.get("qualifier", None)
                line = int(issue.get("line"))
                path = issue.get("file", None)
                trace = issue.get("bug_trace", None)
                if len(trace):
                    refs = []
                    for ref in trace:
                        ref_line = ref["line_number"]
                        ref_msg = ref["description"]
                        # tags = ref['node_tags'] 新版本infer-0.14.0以后去除了该标签
                        ref_path = ref["filename"]
                        if not ref_msg:
                            continue
                        refs.append({"line": ref_line, "msg": ref_msg, "path": ref_path})
                    issues.append({"path": path, "rule": rule, "msg": msg, "line": line, "refs": refs})
                else:
                    issues.append({"path": path, "rule": rule, "msg": msg, "line": line})
        else:  # json结果过大无法一次性加载的情况，且json被压缩在一行，无法使用逐行处理的方式，相对耗时
            self._large_json_handle(error_output, rules, issues)

        return issues

    def _large_json_handle(self, error_output, rules, issues):
        """
        流式处理过大Json文件
        [
          {
            "bug_class": "PROVER",
            "kind": "ERROR",
            "bug_type": "NULL_DEREFERENCE",
            "qualifier": "pointer `s` last assigned on line 12 could be null and is dereferenced at line 13, column 3.",
            "severity": "HIGH",
            "visibility": "user",
            "line": 13,
            "column": 3,
            "procedure": "test",
            "procedure_id": "test.098f6bcd4621d373cade4e832627b4f6",
            "procedure_start_line": 11,
            "file": "hello.c",
            "bug_trace": [
              {
                "level": 0,
                "filename": "hello.c",
                "line_number": 11,
                "column_number": 1,
                "description": "start of procedure test()"
              },
              ...
            ],
            "key": "hello.c|test|NULL_DEREFERENCE",
            "node_key": "df5c83dfdfb79926d42976bfa5b88b70",
            "hash": "4facc3dcd927de905b07688d040f0139",
            "bug_type_hum": "Null Dereference",
            "censored_reason": ""
          },
          ...
        ]
        :return:
        """
        import ijson

        f = open(error_output, "r")
        parser = ijson.parse(f)
        is_in_issue = False
        is_in_trace = False
        refs = []
        for prefix, event, value in parser:
            if is_in_issue:  # 在一个issue的范围内
                if prefix == "item.bug_type":
                    if value in rules:
                        rule = value
                    else:
                        is_in_issue = False
                        continue
                if prefix == "item.qualifier":
                    msg = value
                if prefix == "item.line":
                    line = value
                if prefix == "item.file":
                    path = value

                # bug_trace
                self._bug_trace_handle(is_in_trace, refs, prefix, event, value)

                if prefix == "item" and event == "end_map":
                    is_in_issue = False
                    issues.append({"path": path, "rule": rule, "msg": msg, "line": line, "refs": refs})
                    refs = []
            # 不在一个issue的范围内，需要寻找下一个issue的开始
            elif prefix == "item" and event == "start_map":
                is_in_issue = True
        f.close()

    def _bug_trace_handle(self, is_in_trace, refs, prefix, event, value):
        """
        处理bug trace
        :param is_in_trace:
        :param refs:
        :param prefix:
        :param event:
        :param value:
        :return:
        """
        if is_in_trace:
            if prefix == "item.bug_trace.item.line_number":
                ref_line = value
            if prefix == "item.bug_trace.item.description":
                ref_msg = value
                if not ref_msg:
                    is_in_trace = False
                    # continue
            if prefix == "item.bug_trace.item.filename":
                ref_path = value
            if prefix == "item.bug_trace.item" and event == "end_map":
                is_in_trace = False
                refs.append({"line": ref_line, "msg": ref_msg, "path": ref_path})
        elif prefix == "item.bug_trace.item" and event == "start_map":
            is_in_trace = True

    def print_log(self, message):
        """
        将日志中的敏感词替换掉，再打印日志
        :param message:
        :return:
        """
        ToolDisplay.print_log(self.sensitive, self.sensitive_word_maps, message)
