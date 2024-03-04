# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
clang 扫描任务
"""

import os
import shlex

from task.basic.common import subprocc_log
from task.codelintmodel import CodeLintModel
from tool.util.clangutil import PlistParser
from tool.util.compile import BasicCompile
from tool.util.xcodeswitch import XcodeSwitch
from util.errcode import E_NODE_TASK_CONFIG
from util.exceptions import TaskError, CompileTaskError
from util.logutil import LogPrinter
from util.subprocc import SubProcController


class Clang(CodeLintModel):
    """Clang扫描任务
    """
    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.sensitive_word_maps = {
            "clang": "Tool",
            "Clang": "Tool"
        }
        pass

    def analyze(self, params):
        """执行clang扫描任务

        :param params: 需包含下面键值：
           'rules'： lint扫描的规则列表
           'incr_scan' : 是否增量扫描

        :return: return a :py:class:`IssueResponse`
        """
        # 根据项目环境变量选择合适的xcode版本
        XcodeSwitch.set_xcodebuild_version()

        source_dir = params['source_dir']
        rules = params['rules']
        pre_cmd = params.get('pre_cmd')
        build_cmd = params.get('build_cmd')
        build_args = shlex.split(build_cmd)
        work_dir = os.getcwd()

        # 如果编译命令为空,会导致shlex.split(None)操作卡顿
        if not build_cmd:
            raise TaskError(code=E_NODE_TASK_CONFIG, msg=u'编译命令为空,请先填写xcodebuild命令!')

        if build_args and 'xcodebuild' not in build_args:
            raise TaskError(code=E_NODE_TASK_CONFIG, msg=u'编译命令填写错误,请填写xcodebuild命令!')
        if not build_args:
            build_args = ['xcodebuild']

        # get compild cwd from env var
        build_cwd = os.environ.get('BUILD_CWD', None)
        compile_cwd = os.path.join(source_dir, build_cwd) if build_cwd else source_dir

        # 执行前置命令
        if pre_cmd:
            LogPrinter.info('run pre command ...')
            pre_cmd = BasicCompile.generate_shell_file(pre_cmd, shell_name="tca_pre_cmd")
            LogPrinter.info('run pre cmd shell file: %s' % pre_cmd)
            sp = SubProcController(
                shlex.split(pre_cmd),
                cwd=compile_cwd,
                stdout_line_callback=subprocc_log,
                stderr_line_callback=subprocc_log,
                stdout_filepath=None,
                stderr_filepath=None
            )
            sp.wait()
            if sp.returncode != 0:
                LogPrinter.info("Pre command run error!")
                raise CompileTaskError(msg=f"前置命令执行失败，请确认命令能否在代码根目录下成功执行: {pre_cmd}")

        # 执行xcodebuild analyze
        LogPrinter.info('analyze project ...')
        build_cmd = build_args + ['CLANG_STATIC_ANALYZER_MODE_ON_ANALYZE_ACTION=shallow', 'analyze']
        build_log = os.path.join(work_dir, 'clang_analyze.log')

        LogPrinter.info('run cmd: %s' % ' '.join(build_cmd))
        sp = SubProcController(
            build_cmd,
            cwd=compile_cwd,
            stdout_filepath=build_log,
            stderr_line_callback=subprocc_log,
            stdout_line_callback=subprocc_log,
            stderr_filepath=None
        )
        sp.wait()
        if sp.returncode != 0:
            LogPrinter.info("Analyze Failed!")
            raise CompileTaskError(msg=f"编译命令执行失败，请确认编译命令能否在代码根目录下成功执行: {' '.join(build_cmd)}")

        plist_paths = PlistParser().collect_plist_paths(build_log)

        # 格式化结果
        LogPrinter.info('format issues...')
        issues = self.format_result(rules, source_dir, plist_paths)

        LogPrinter.debug("there are %s issues." % (len(issues)))
        return issues

    def format_result(self, rules, source_dir, plist_paths):
        """格式化工具执行结果
        """
        # 支持通过环境变量，配置是否启用全量规则
        use_all_rules = True if os.environ.get('CLANG_ALL_RULES', "False") == "True" else False
        if use_all_rules:
            LogPrinter.info("全量规则分析,不需要过滤规则.")
        issues = []
        for plist_path in plist_paths:
            try:
                if os.path.getsize(plist_path) < 512:
                    continue
            except (IOError, OSError):
                continue
            result = PlistParser().parse_plist(plist_path, source_dir, rules, use_all_rules)
            issues.extend(result)
        return issues

    def check_tool_usable(self, tool_params):
        spc = SubProcController(command=["xcodebuild", "-version"])
        spc.wait()
        if spc.returncode != 0:
            return []
        else:
            return ["analyze"]


tool = Clang

if __name__ == '__main___':
    pass
