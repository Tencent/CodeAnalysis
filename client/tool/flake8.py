# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
flake8 扫描任务
当前版本 flake8(3.7.9)
"""

import os
import sys
import shlex
from multiprocessing import cpu_count

from task.codelintmodel import CodeLintModel
from tool.util.pythontool import PythonTool
from util.logutil import LogPrinter
from util.subprocc import SubProcController
from util.exceptions import AnalyzeTaskError
from util.pathlib import PathMgr

logger = LogPrinter


# codedog flag 用于解析拆分输出结果
CODEDOG_FLAG = '[CODEDOG]'


class Flake8(CodeLintModel):

    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.sensitive_word_maps = {
            "Flake8": "Tool",
            "flake8": "Tool"
        }
        pass

    def analyze(self, params):
        '''
        分析执行函数
        :param params: 分析所需要的资源 1.项目地址 2.工作地址 3.分析参数
        :return:
        '''
        source_dir = params['source_dir']
        work_dir = os.getcwd()
        rules = params['rules']

        toscans = PythonTool.get_scan_files(params)

        if not toscans:
            logger.debug("To-be-scanned diff files is empty ")
            return []

        cmd_args_list = self._get_cmd_args(source_dir, toscans, rules)

        # 结果解析异常JSONDecodeError, linux某些终端下会在josn开头添加 [?1034h 或 ^[[?1034h[
        if sys.platform in ("linux", "linux2"):
            os.environ['TERM'] = ''

        relpos = len(source_dir) + 1
        items = []
        for i in range(len(cmd_args_list)):
            error_output = os.path.join(work_dir, 'result_'+str(i)+'.json')
            # self.print_log("cmd: %s" % ' '.join(cmd_args_list[i]))
            logger.info("cmd_len: %d" % len(' '.join(cmd_args_list[i])))
            sp = SubProcController(command=cmd_args_list[i],
                                   cwd=work_dir,
                                   return_code_callback=self.on_status,
                                   stdout_filepath=error_output,
                                   stdout_line_callback=self.print_log,
                                   stderr_line_callback=self.stderr_callback)
            sp.wait()

            if not os.path.exists(error_output) or os.stat(error_output).st_size == 0:
                logger.info("result_"+str(i)+".json - result is empty")
                continue
            try:
                with open(error_output, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except:
                with open(error_output, 'r', encoding='gbk') as f:
                    lines = f.readlines()
            for line in lines:
                if line.find(CODEDOG_FLAG) >= 0:
                    issue = line.split(CODEDOG_FLAG)
                    try:
                        assert len(issue)==5
                    except AssertionError:
                        logger.info("格式化错误信息失败，错误为: %s" % line)
                        continue
                    # flake输出格式为:
                    # {path}[CODEDOG]{line}[CODEDOG]{col}[CODEDOG]{rule}[CODEDOG]{msg}
                    items.append({
                        'path': issue[0][relpos:],
                        'rule': issue[3],
                        'msg': issue[4],
                        'line': int(issue[1]),
                        'column': int(issue[2])
                        })
        return items

    def _get_cmd_args(self, source_dir, toscans, rules):
        python = PythonTool.check_python("flake8")
        # 不使用json格式防止项目配置文件里有
        # flake输出格式为:
        # {path}[CODEDOG]{line}[CODEDOG]{col}[CODEDOG]{rule}[CODEDOG]{msg}
        cmd_args = [python, '-m', 'flake8',
                    '--format="%(path)s[CODEDOG]%(row)d[CODEDOG]%(col)d[CODEDOG]%(code)s[CODEDOG]%(text)s"',
                    '--exit-zero',
                    '--show-source',
                    '--jobs=' + str(cpu_count())]

        tool_config_files_dir = os.getenv("TOOL_CONFIG_FILES_HOME")
        # 初始化配置文件
        setting_file = None

        # 用户指定配置文件
        user_config_file = os.getenv("FLAKE8_CONFIG_FILE", None)
        if user_config_file:
            user_config_file = os.path.join(source_dir, user_config_file)
            if os.path.exists(user_config_file):
                setting_file = user_config_file

        if setting_file:
            logger.info("using flake8 config file: %s" % setting_file)
            cmd_args.append("--config=%s" % setting_file)
        else:
            # 支持额外的扫描参数,比如：--max-line-length=120
            FLAKE8_OPTION_PARAMS = os.environ.get("FLAKE8_OPTION_PARAMS", None)
            if FLAKE8_OPTION_PARAMS:
                cmd_args.extend(shlex.split(FLAKE8_OPTION_PARAMS))
            # 指定扫描规则
            if rules:
                cmd_args.append('--select=%s' % ','.join(rules))

        # 获取命令行最长限制
        CMD_ARG_MAX = PathMgr().get_cmd_arg_max()
        # 设置环境变量，方便项目接入时候修改
        if os.environ.get("FLAKE8_ARG_MAX", None):
            CMD_ARG_MAX = int(os.environ.get("FLAKE8_ARG_MAX"))
        logger.info("命令行长度限制：%d" % CMD_ARG_MAX)
        cmd_args_list = PathMgr().get_cmd_args_list(cmd_args, toscans, CMD_ARG_MAX)
        return cmd_args_list

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
        if line.find("UnicodeDecodeError")!=-1 and sys.platform=="win32":
            logger.error("遇到编码问题！猜测是在windows、Python2下无法处理中文文件路径BUG, 建议改为在Mac、Linux下运行。")
            raise AnalyzeTaskError('工具编码BUG，建议改为在Mac、Linux下运行')

    def on_status(self, pid, rtcode):
        """
        flake8返回码回调函数
        设置--exit-zero，成功扫描都会返回0，扫描失败便返回非0
        :param pid:
        :param rtcode:
        :return:
        """
        if rtcode != 0:
            raise AnalyzeTaskError('return exit code %d' % rtcode)

    def check_tool_usable(self, tool_params):
        """
        这里判断机器是否支持运行flake8，三端保持一致
        1. 支持的话，便使用机器上的默认python和flake8分析
        2. 不支持的话，记载环境变量，使用Puppy自己的flake8环境
        3. 还不支持的话，就发布任务到公线机器分析，公线机器维护一套自己的python环境
        可以通过$?或者%errorlevel%来检验
        :return:
        """
        return PythonTool.check_tool_usable("flake8")


tool = Flake8

if __name__ == '__main__':
    pass
