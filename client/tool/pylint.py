# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
pylint 扫描任务
"""

import hashlib
import json
import os
import shlex
import sys
import uuid

from task.basic.common import subprocc_log
from task.codelintmodel import CodeLintModel
from tool.util.pythontool import PythonTool
from util.envset import EnvSet
from util.logutil import LogPrinter
from util.errcode import E_NODE_CUSTOM_TOOL
from util.exceptions import AnalyzeTaskError, TaskError
from util.pathlib import PathMgr
from util.subprocc import SubProcController
from util.textutil import CodecClient

logger = LogPrinter


class Pylint(CodeLintModel):

    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.issues = []
        self.sensitive_word_maps = {
            "Pylint": "Tool",
            "pylint": "Tool"
        }

    def _path_is_right(self, file_path, scan_paths):
        """
        检查文件路径是否符合在需要扫描的文件列表中
        :param path:
        :param scan_paths:
        :return:
        """
        scan_paths = [path.replace(os.sep, '/') for path in scan_paths]
        return file_path.replace(os.sep, '/') in scan_paths

    def pre_cmd(self, params, build_cwd):
        """
        执行前置命令
        :return:
        """
        pre_cmd = params.get("pre_cmd", None)
        if not pre_cmd:
            return
        logger.info("do pre_cmd.")
        if isinstance(pre_cmd, str):
            pre_cmd = shlex.split(pre_cmd)
        logger.info("run pre cmd: %s" % " ".join(pre_cmd))
        SubProcController(
            pre_cmd,
            cwd=build_cwd,
            stdout_line_callback=subprocc_log,
            stderr_line_callback=subprocc_log,
            env=EnvSet().get_origin_env(),
        ).wait()

    def analyze(self, params):
        '''
        分析执行函数
        :param params: 分析所需要的资源 1.项目地址 2.工作地址 3.分析参数
        :return:
        '''
        source_dir = params['source_dir']
        self.pre_cmd(params, source_dir)
        self.work_dir = os.getcwd()
        rules = params['rules']

        toscans = PythonTool.get_scan_files(params)
        if not toscans:
            logger.debug("To-be-scanned diff files is empty ")
            return []

        python = PythonTool.check_python("pylint")

        # 输出pylint版本
        self.print_log("当前使用的Pylint版本:")
        SubProcController([python, "-m", "pylint", "--version"], stdout_line_callback=self.print_log).wait()

        pylint_custom_files = self._add_custom_rules()
        cmd_args, setting_file = self._get_cmd_args(source_dir, pylint_custom_files, python, rules)

        items = []
        # pylint结果解析异常JSONDecodeError, linux某些终端下会在josn开头添加 [?1034h 或 ^[[?1034h[
        if sys.platform in ("linux", "linux2"):
            os.environ['TERM'] = ''
        for file in toscans:
            self.run_pylint_scan(cmd_args, file)

        relpos = len(source_dir) + 1
        for issue in self.issues:
            rule = issue['symbol']
            # 未使用配置文件扫描时，过滤掉不在规则列表中的issue
            if not setting_file:
                if rule not in rules:
                    continue

            path = issue['path'][relpos:]
            msg = issue['message']
            line = issue['line']
            column = issue['column']
            items.append({'path': path, 'rule': rule, 'msg': msg, 'line': line, 'column': column})
        items = self.__hash_del_dup(items)
        return items

    def _add_custom_rules(self):
        # 2020/1/8 添加pylint自定义规则
        # 1. 在PYTHONPATH中添加pylint_custom_home
        # 2. 在pylint --load-plugins=中添加相对于PYTHONPATH的相对路径，然后去掉.py
        ext = ".py"
        pylint_custom_files = list()
        python_path = []
        pylint_custom_home = os.environ.get('PYLINT_CUSTOM_HOME', None)
        pylint_convention_home = os.environ.get("PYLINT_CONVENTION_HOME", None)
        if pylint_custom_home:
            pylint_custom_files.extend([f[len(pylint_custom_home) + 1:-len(ext)] for f in
                                        PathMgr().get_dir_files(pylint_custom_home, ext)])
            python_path.append(pylint_custom_home)
        if pylint_convention_home:
            pylint_custom_files.extend([f[len(pylint_convention_home) + 1:-len(ext)] for f in
                                        PathMgr().get_dir_files(pylint_convention_home, ext)])
            python_path.append(pylint_convention_home)

        # 设置到Python搜索路径中
        # 可以指向项目自身，比如PYTHONPATH=$SOURCE_DIR/lib:$SOURCE_DIR/compute
        # python_path = [source_dir, pylint_custom_home, pylint_convention_home]
        if os.environ.get("PYTHONPATH", None):
            python_path.append(os.environ["PYTHONPATH"])
        os.environ["PYTHONPATH"] = os.pathsep.join(python_path)
        return pylint_custom_files

    def _get_cmd_args(self, source_dir, pylint_custom_files, python, rules):
        """
        get pylint args
        """
        EXTENSION_PKG_WHITELIST = os.environ.get("PYLINT_EXTENSION_PKG_WHITELIST", None)
        PYLINT_OPTION_PARAMS = os.environ.get('PYLINT_OPTION_PARAMS', None)
        # pylint在windows、python2环境下执行时，若结果中包含中文字符，一般是文件路径有中文字符，
        # 可能在输出结果时出现编码问题，是工具bug，此时建议在Mac、linux上运行工具
        cmd_args = [python, '-m', 'pylint', '-f', 'json', '--reports=n', '--exit-zero', ]
        if pylint_custom_files:
            cmd_args.append("--load-plugins=%s" % ",".join(pylint_custom_files))

        # 支持设置依赖包白名单
        if EXTENSION_PKG_WHITELIST:
            cmd_args.append("--extension-pkg-whitelist=" + EXTENSION_PKG_WHITELIST)

        tool_config_files_dir = os.getenv("TOOL_CONFIG_FILES_HOME")
        # 初始化配置文件
        setting_file = None

        # 用户指定配置文件
        user_config_file = os.getenv("PYLINT_CONFIG_FILE", None)
        if user_config_file:
            user_config_file = os.path.join(source_dir, user_config_file)
            if os.path.exists(user_config_file):
                setting_file = user_config_file

        if setting_file:
            cmd_args.append("--rcfile=%s" % setting_file)
            logger.info("using pylint config file: %s" % setting_file)
        else:
            # 支持设置pylint的额外设置
            # 比如：--max-line-length=240
            # 添加 --max-line-length配置，支持代码规范
            cmd_args.append('--max-line-length=120')
            if PYLINT_OPTION_PARAMS:
                cmd_args.extend(shlex.split(PYLINT_OPTION_PARAMS))
            if rules:
                cmd_args.append('--disable=all')
                cmd_args.append('-e')
                cmd_args.append(','.join(rules))
        return cmd_args, setting_file

    def run_pylint_scan(self, cmd, file,):
        """
        运行pylint
        """
        error_output = "global_"+uuid.uuid1().hex+".json"
        logger.info(cmd + [file])
        sp = SubProcController(command=cmd + [file],
                               cwd=self.work_dir,
                               return_code_callback=self.on_status,
                               stdout_filepath=error_output,
                               stderr_line_callback=self.stderr_callback)
        sp.wait()
        if not os.path.exists(error_output) or os.stat(error_output).st_size==0:
            logger.info("result is empty")
            return
        with open(error_output, 'r') as f:
            fc = f.read()
            issues = json.loads(fc)
        self.issues.extend(issues)
        os.remove(error_output)

    def __hash_del_dup(self, issues):
        """
        通过计算 hash 去重
        :param issues: 字典列表
        :return:
        """
        hash_issues = {}
        for item in issues:
            hash_str = "%s-%s-%s-%s-%s" % (item["path"], item["rule"], item["msg"], item["line"], item["column"])
            encode_str = CodecClient().encode(hash_str)
            hash_key = hashlib.sha1(encode_str).hexdigest()
            if hash_key not in hash_issues:
                hash_issues[hash_key] = item

        return list(hash_issues.values())

    def __get_stdout_log(self, subPc):
        """

        :param subPc:
        :return: stdout中的log
        """
        spcOut = subPc.get_stdout()
        if not spcOut:
            return ""
        log = spcOut.read()
        spcOut.close()
        return log

    def stderr_callback(self, line):
        """
        报错回调处理
        :param line:
        :return:
        """
        self.print_log(line)
        if line.find("UnicodeDecodeError") != -1 and sys.platform=="win32":
            logger.error("遇到编码问题！猜测是pylint在windows、Python2下无法处理中文文件路径BUG, 建议改为在Mac、Linux下运行。")
            raise TaskError(code=E_NODE_CUSTOM_TOOL, msg='pylint工具编码BUG，建议改为在Mac、Linux下运行')
        elif line.find("error: no such option: --exit-zero")!=-1:
            raise TaskError(code=E_NODE_CUSTOM_TOOL, msg='版本较低，建议客户升级Pylint，参考命令: pip install --upgrade pylint')
        elif line.find("ImportError") != -1:
            raise TaskError(code=E_NODE_CUSTOM_TOOL, msg="存在代码文件和Python系统模块同名，导致pylint引用失败，请勿把sourcedir加入到PYTHONPATH中.")
        elif line.find("TypeError") != -1 or line.find("RecursionError") != -1:
            logger.error("工具bug，某些文件无法处理，待官方修复升级后解决。临时处理方式：定位到无法分析的异常代码文件,加入到过滤路径中。")

    def on_status(self, pid, rtcode):
        """
        pylint返回码回调函数
        设置--exit-zero，成功扫描都会返回0，扫描失败便返回非0
        需要1.9.3版本以上;其他版本是1或者>=32
        :param pid:
        :param rtcode:
        :return:
        """
        # pylint返回码
        # 0	no error
        # 1	    fatal message issued
        # 2	    error message issued
        # 4	    warning message issued
        # 8	    refactor message issued
        # 16	convention message issued
        # 32	usage error
        #           “internal error while receiving resultsfrom child linter” “Error occured, stopping the linter.”
        #           “<return of linter.help()>”
        #           “Jobs number <#> should be greater than 0”
        if rtcode == 32:
            raise AnalyzeTaskError(' cmd return exit code %d' % rtcode)

    def check_tool_usable(self, tool_params):
        """
        这里判断机器是否支持运行pylint，三端保持一致
        1. 支持的话，便使用机器上的默认python和pylint扫描
        2. 不支持的话，记载环境变量，使用Puppy自己的Pylint环境
        3. 还不支持的话，就发布任务到公线机器扫描，公线机器维护一套自己的python环境
        可以通过$?或者%errorlevel%来检验
        :return:
        """
        return PythonTool.check_tool_usable("pylint")


tool = Pylint

if __name__ == '__main__':
    pass
