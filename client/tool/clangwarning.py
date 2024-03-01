# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
clangwarning 扫描任务
本地编译,获取编译警告信息
"""

import os
import shlex

from task.codelintmodel import CodeLintModel
from util.errcode import E_NODE_TASK_CONFIG
from util.subprocc import SubProcController
from util.exceptions import TaskError, CompileTaskError
from task.basic.common import subprocc_log
from tool.util.xcodeswitch import XcodeSwitch
from util.logutil import LogPrinter
from tool.util.compile import BasicCompile
from tool.util.warninganalyzer import BuildLogAnalyzer


class ClangWarning(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)

    def __run_clang(self, params, source_dir, rules):
        """通过 xcodebuild 进行编译

        :param params:任务参数
        :param source_dir:源码目录
        :param rules:扫描规则
        :return: build_log_path
        """
        work_dir = os.getcwd()
        build_cmd = params.get('build_cmd', None)
        pre_cmd = params.get('pre_cmd', None)

        build_log_path = os.path.join(work_dir, 'build.log')
        build_err_path = os.path.join(work_dir, 'build.err')

        # get compile cwd
        build_cwd = os.environ.get('BUILD_CWD', None)
        compile_cwd = os.path.join(source_dir, build_cwd) if build_cwd else source_dir
        LogPrinter.debug("compild_cwd: %s" % (compile_cwd))

        if not build_cmd:
            build_cmd = 'xcodebuild'
        elif 'xcodebuild' not in build_cmd:
            raise TaskError(code=E_NODE_TASK_CONFIG, msg=u'编译命令不正确,请填写一行xcodebuild命令.')

        # pre-process step
        if pre_cmd:
            LogPrinter.info('run pre command ...')
            pre_cmd = BasicCompile.generate_shell_file(pre_cmd, shell_name="tca_pre_cmd")
            LogPrinter.info('run pre cmd shell file: %s' % pre_cmd)
            spc = SubProcController(
                command=shlex.split(pre_cmd),
                cwd=compile_cwd,
                stdout_line_callback=subprocc_log,
                stderr_line_callback=subprocc_log,
                stdout_filepath=None,
                stderr_filepath=None
            )
            spc.wait()

        LogPrinter.info('start to compile ...')
        # 指定警告类型编译,例如: xcodebuild buildsetting=-Wincompatible-pointer-types,-Wshorten-64-to-32,-Wunused-variable
        warning_arg = ",".join(["-W%s" % rule for rule in rules])
        compile_cmd = "%s buildsetting=%s" % (build_cmd, warning_arg)

        LogPrinter.info('run cmd: %s' % compile_cmd)

        # 编译日志同时输出到task.log和build.log中,分别供查看和结果解析
        spc = SubProcController(
            command=shlex.split(compile_cmd),
            cwd=compile_cwd,
            stdout_filepath=build_log_path,
            stderr_filepath=build_err_path,
            stdout_line_callback=subprocc_log,
            stderr_line_callback=subprocc_log
            )
        spc.wait()
        if not os.path.exists(build_log_path):
            raise CompileTaskError(msg="编译失败,未生成结果文件(build.log),请进入任务页面下载日志查看失败原因.")

        return build_log_path

    def compile(self, params):
        """执行 clangwarning 扫描任务
        :param request: 任务请求
        :return: return a :py:class:`IssueResponse`
        """
        # 根据项目环境变量选择合适的xcode版本
        XcodeSwitch.set_xcodebuild_version()

        rules = params['rules']
        source_dir = params['source_dir']

        # 1.clang编译项目
        build_log_path = self.__run_clang(params, source_dir, rules)
        LogPrinter.debug("build_log_path: %s" % (build_log_path))

        # 2.解析构建日志
        LogPrinter.info('analyze build log ...')
        issues = BuildLogAnalyzer().analyze_log_file(source_dir, rules, build_log_path)

        return issues

    def check_tool_usable(self, tool_params):
        spc = SubProcController(command=["xcodebuild", "-version"])
        spc.wait()
        if spc.returncode != 0:
            return []
        else:
            return ["compile"]


tool = ClangWarning

if __name__ == '__main___':
    pass
