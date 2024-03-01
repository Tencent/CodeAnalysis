# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
AndroidLint工具封装类
"""

import os
import re
import time

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from task.codelintmodel import CodeLintModel
from util.pathlib import PathMgr
from util.subprocc import SubProcController
from tool.util.compile import BasicCompile
from util.exceptions import CompileTaskError, AnalyzeTaskError
from util.logutil import LogPrinter


# Advanced options of the androidlint tool.
# Users can change the tool execution mode by setting environment variables
# Environment variable name:
LINT_BUILD_TYPE_ENV = "ANDROID_LINT_BUILD_TYPE"
LINT_TASK_NAME_ENV = "ANDROID_LINT_TASK_NAME"
PROJECT_DIR_ENV = "ANDROID_LINT_PROJECT_DIR"
CLASSPATH_ENV = "ANDROID_LINT_CLASSPATH"
SDK_TOOL_ENV = "ANDROID_SDK_TOOL"
LINT_CMD = "GRADLEW_LINT_CMD"


class AndroidLint(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.sensitive_word_maps = {"AndroidLint": "Tool", "androidlint": "Tool"}

    def compile(self, params):
        """
        编译执行函数
        :param params:
        :return:
        """
        build_cmd = params.get("build_cmd")
        if not build_cmd:
            raise CompileTaskError("编译语言项目执行静态分析需要输入编译命令，请填入编译命令后重试！")
        BasicCompile(
            params,
            sensitive=self.sensitive,
            sensitive_word_maps=self.sensitive_word_maps,
            build_cmd=BasicCompile.generate_shell_file(build_cmd),
        ).compile()
        return True

    def analyze(self, params):
        """
        分析执行函数
        :param params:
        :return:
        """
        source_dir = params["source_dir"]
        build_cwd = os.environ.get("BUILD_CWD", None)
        # 构建当前目录
        build_cwd = os.path.join(source_dir, build_cwd) if build_cwd else source_dir

        enabled_rules = params["rules"]
        error_output = os.path.join(os.path.curdir, "androidlint_result.xml")
        # 添加构建方式环境变量
        # 默认是使用gradle方式。也可能是其他的，比如ant
        build_type = os.environ.get(LINT_BUILD_TYPE_ENV, "gradle").lower()

        # 如果该项目为gradle项目即通过gradle执行lint
        if build_type == "gradle":
            return self.gradle_mode_analyze(params)
        else:
            # 查看用户是否有传入工具配置参数，若有则按参数传入进行工具适配
            lint_proj_dir = os.environ.get(PROJECT_DIR_ENV)
            if lint_proj_dir:
                self.print_log("get lint project dir: %s" % lint_proj_dir)
                source_dir = os.path.join(source_dir, lint_proj_dir)

            # gradle项目不可以直接执行lint.jar，因此此处先删除项目中的build.gradle文件，可以保证工具正常执行
            for root, _, files in os.walk(source_dir):
                for filename in files:
                    if filename == "build.gradle":
                        try:
                            PathMgr().rmpath(os.path.join(root, "build.gradle"))
                        except Exception as e:
                            LogPrinter.exception(
                                "rmpath gradle config error : %s, exception: %s"
                                % (os.path.join(root, "build.gradle"), str(e))
                            )

            # analyze step
            scan_cmd = [
                "java",
                "-jar",
                os.path.join(os.environ[SDK_TOOL_ENV], "lib", "lint.jar"),
                "--quiet",
                "--nolines",
            ]

            # 获取用户传入的参数
            lint_classpath = os.environ.get(CLASSPATH_ENV)
            if lint_classpath:
                classpath_list = re.compile("[:,;]").split(lint_classpath)
                real_classpath_list = []
                for classpath_path in classpath_list:
                    real_classpath_list.append(os.path.join(source_dir, classpath_path))
                scan_cmd.append("--classpath")
                sep = ":"
                scan_cmd.append(sep.join(real_classpath_list))

            if enabled_rules:
                scan_cmd.append("--check")
                scan_cmd.append(",".join(enabled_rules))
            scan_cmd.extend(["--xml", error_output, source_dir])
            scan_cmd = PathMgr().format_cmd_arg_list(scan_cmd)
            SubProcController(
                scan_cmd,
                stdout_line_callback=self.print_log,
                stderr_line_callback=self.print_log,
            ).wait()

            # format step
            return self.__get_issues_from_file(error_output, source_dir)

    def gradle_mode_analyze(self, params):
        """
        使用gradle模式，处理gralde项目
        """
        source_dir = params["source_dir"]
        build_cwd = os.environ.get("BUILD_CWD", None)
        # 构建当前目录
        build_cwd = os.path.join(source_dir, build_cwd) if build_cwd else source_dir
        enabled_rules = params["rules"]

        if os.environ.get(LINT_TASK_NAME_ENV, False):
            lint_cmd = ["gradle", os.environ[LINT_TASK_NAME_ENV]]
        elif os.environ.get(LINT_CMD, None):
            lint_cmd = os.environ[LINT_CMD]
        else:
            lint_cmd = ["gradle", "lint"]

        lint_cmd = PathMgr().format_cmd_arg_list(lint_cmd)
        self.print_log("subprocc : %s" % lint_cmd)
        sub_proc = SubProcController(
            lint_cmd, cwd=build_cwd, stdout_line_callback=self.print_log, stderr_line_callback=self.print_log
        )
        sub_proc.wait()
        err_log = self.__get_stderr_log(sub_proc)
        if err_log.find("FAILURE: Build failed with an exception") != -1:
            raise AnalyzeTaskError("lint执行失败，请查看日志排查原因")
        self.print_log("%s done." % lint_cmd)
        # 执行完扫描后，无法在项目中找到lint文件，但文件却存在，因此sleep3秒
        time.sleep(3)
        error_output = []
        issues = []
        LogPrinter.info("lint report find : %s" % source_dir)
        for dirpath, _, filenames in os.walk(source_dir):
            for f in filenames:
                if not isinstance(f, str):
                    LogPrinter.info("source have not str name file: %s" % str(f))
                    f = str(f)
                if f.find("lint") >= 0 and f.endswith(".xml"):
                    error_output.append(os.path.join(dirpath, f))
        LogPrinter.info(u"total get %s result file ." % str(len(error_output)))
        for unit in error_output:
            LogPrinter.info(u"read issue from %s" % unit)
            issues.extend(self.__get_issues_from_file(unit, source_dir))
        LogPrinter.info(u"total get %s issue ." % str(len(issues)))
        result = []
        for issue in issues:
            if issue["rule"] in enabled_rules:
                result.append(issue)
        self.print_log(u"Lint found issue: %s" % str(result))
        return result

    def __get_stderr_log(self, sub_proc):
        """
        获取执行stderr的log
        :param sub_proc:
        :return: stderr中的log
        """
        if not os.path.exists(sub_proc.stderr_filepath):
            return ""
        spc_err = open(sub_proc.stderr_filepath, "r", encoding="utf-8")
        log = spc_err.read()
        spc_err.close()
        return log

    def __get_issues_from_file(self, file_path, source_dir):
        items = []
        lint_proj_dir = os.environ.get(PROJECT_DIR_ENV)
        if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
            return items
        warning_data = ET.ElementTree(file=file_path)
        for bug in warning_data.iter(tag="issue"):
            rule = bug.attrib.get("id")
            msg = bug.attrib.get("message")
            if rule == "LintError":
                LogPrinter.warning("Lint Error msg: %s" % msg)
                continue
            if len(bug) == 0:
                LogPrinter.warning("The rule %s doesn't find the location" % rule)
                continue
            locations = bug.getchildren()  # 旧方法只获取最后一个文件行号，此方法获取所有行号
            for location in locations:
                if not location.tag == "location":
                    continue
                path = location.get("file")
                if not location.get("line"):
                    if path.endswith(".java") or path.endswith(".class"):
                        LogPrinter.warning("%s: can't find the accurate source position" % path)
                        continue
                    line = 1  # 图片文件或资源文件若无行号，则给一个1.
                else:
                    line = int(location.get("line"))
                if os.path.isabs(path):
                    path = os.path.relpath(path, source_dir)
                if lint_proj_dir:
                    path = os.path.join(lint_proj_dir, path)
                items.append({"path": path, "rule": rule, "msg": msg, "line": line})
        return items


tool = AndroidLint

if __name__ == "__main__":
    pass
