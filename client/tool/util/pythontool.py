# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
Python内置工具的通用方法
"""

import os
import sys

from task.scmmgr import SCMMgr
from util.envset import EnvSet
from util.logutil import LogPrinter
from util.pathlib import PathMgr
from util.subprocc import SubProcController
from util.pathfilter import FilterPathUtil


class PythonTool(object):
    @staticmethod
    def check_tool_usable(tool_name):
        """
        这里判断机器是否支持运行工具，三端保持一致
        1. 支持的话，便使用机器上的默认python和pylint分析
        2. 不支持的话，记载环境变量，使用Puppy自己的Pylint环境
        3. 还不支持的话，就发布任务到公线机器分析，公线机器维护一套自己的python环境
        可以通过$?或者%errorlevel%来检验
        :return:
        """
        python_version = PythonTool.get_python_version_from_env()

        # 判断本地Python环境是否可用
        if PythonTool.is_python_available(tool_name, python_version=python_version):
            return ["analyze"]

        # python --version执行失败，或者不是对应版本的情况, 使用python2 --version
        if PythonTool.is_python_available(tool_name, python_version=python_version, with_version=True):
            return ["analyze"]

        # 本地Python环境不可用，使用puppy自身的Python环境，判断Puppy自身的Python环境在该机器上是否可用
        # 加载环境变量
        PythonTool.add_python_env(tool_name)
        if PythonTool.is_python_available(tool_name, python_version=python_version, with_version=True):
            return ["analyze"]

        # 该机器不支持分析
        return []

    @staticmethod
    def get_python_version_from_env():
        """
        从环境变量中获取python版本号,环境变量只支持2或3
        :return: <str> "2"|"3"
        """
        # 支持从环境变量指定python版本
        python_version = os.environ.get('PYLINT_PYTHON_VERSION')
        if python_version is None:
            # 支持通过PYTHON_VERSION环境变量设置python版本
            python_version = os.environ.get('PYTHON_VERSION')
        if python_version not in ["2", "3"]:  # 环境变量只支持2或3
            python_version = "3"
        return python_version

    @staticmethod
    def check_python(tool_name):
        """判断当前使用的python版本"""
        python_version = PythonTool.get_python_version_from_env()

        # 公线机器的话，默认是python3; 客户机器的话，直接使用客户自己环境中的python版本
        python = "python"
        # 判断本地Python环境是否可用, 默认使用python3
        if not PythonTool.is_python_available(tool_name, python_version=python_version):
            # python不可用，判断python2或者python3是否可用
            python += str(python_version)
            if not PythonTool.is_python_available(tool_name, python_version=python_version, with_version=True):
                # 使用puppy自身的python环境
                PythonTool.add_python_env(tool_name)
        return python

    @staticmethod
    def is_local_python_command_available(python_cmd="python3", python_version="3"):
        """
        判断本地python命令是否可用
        """
        std_output_filepath = "check_python_output.log"
        if os.path.exists(std_output_filepath):
            PathMgr().safe_rmpath(std_output_filepath)
        # python3 命令输出在stdout, python2 命令输出在stderr,所以这里需要把stdout、stderr输出到一个文件，方便后面从该文件获取输出
        cmd_args = [python_cmd, "--version"]
        # LogPrinter.info(f'run cmd: {cmd_args}')
        subProC = SubProcController(cmd_args,
                                    stdout_line_callback=LogPrinter.info,
                                    stderr_line_callback=LogPrinter.info,
                                    stderr_filepath=std_output_filepath,
                                    stdout_filepath=std_output_filepath)
        subProC.wait()
        cmd_output = PythonTool.get_stdout_log(subProC).find("Python " + str(python_version) + ".")
        if subProC.returncode == 0 and cmd_output != -1:
            return True
        else:
            return False

    @staticmethod
    def is_python_available(tool_name, python_version="3", with_version=False):
        """
        基于传入的python版本，判断工具是否可用
        :param tool_name: 工具名称
        :param python_version: "2", "3"
        :param with_version: python是否带上版本号，如python3
        :return:
        """
        python_cmd = "python"
        if with_version:
            python_cmd += str(python_version)

        if PythonTool.is_local_python_command_available(python_cmd, python_version):
            # 本地Python环境可用，接下来判断是否安装pylint
            cmd_args = [python_cmd, "-m", tool_name, "--version"]
            LogPrinter.info(f'run cmd: {cmd_args}')
            if SubProcController(cmd_args,
                                 stdout_line_callback=LogPrinter.info,
                                 stderr_line_callback=LogPrinter.info).wait() != 0:
                if tool_name == "flake8":
                    message = "建议客户本地安装flake8工具，安装命令：pip install flake8 && pip install flake8-json"
                else:
                    message = f"建议客户本地安装{tool_name}工具，安装命令：pip install {tool_name}"
                LogPrinter.info(message)
            else:
                # 本地pylint环境可用
                return True
        return False

    @staticmethod
    def add_python_env(tool_name):
        """
        加载Puppy自身Python环境到环境变量中
        :return:
        """
        path_envs = []
        pythone27_home = os.environ.get("PYTHON27_HOME")
        python37_home = os.environ.get("PYTHON37_HOME")
        LogPrinter.info("正在启用CodeDog内置的Python环境")
        if sys.platform == "win32":
            if pythone27_home:
                path_envs.append(os.path.join(pythone27_home, "Scripts"))
                path_envs.append(pythone27_home)
            if python37_home:
                path_envs.append(os.path.join(python37_home, "Scripts"))
                path_envs.append(python37_home)
        else:
            if pythone27_home:
                path_envs.append(os.path.join(pythone27_home, "bin"))
            if python37_home:
                path_envs.append(os.path.join(python37_home, "bin"))
        if path_envs:
            EnvSet().set_tool_env({
                tool_name:
                    {
                        "env_path": {},
                        "env_value": {},
                        "path": path_envs,
                        "tool_url": []
                    }
            })

    @staticmethod
    def get_stdout_log(subPc):
        """
        获取subprocess的输出
        :param subPc:
        :return: stdout中的log
        """
        spcOut = subPc.get_stdout()
        if not spcOut:
            return ""
        log = spcOut.read()
        # LogPrinter.info(f"check python: {log}")
        spcOut.close()
        return log

    @staticmethod
    def get_scan_files(params):
        source_dir = params['source_dir']
        incr_scan = params['incr_scan']
        relpos = len(source_dir) + 1
        want_suffix = ['.py']
        # 获取需要扫描的文件
        if incr_scan:
            diffs = SCMMgr(params).get_scm_diff()
            toscans = [diff.path.replace(os.sep, '/') for diff in diffs
                       if diff.path.endswith(tuple(want_suffix)) and diff.state != 'del']
        else:
            toscans = [path.replace(os.sep, '/')[relpos:]
                       for path in PathMgr().get_dir_files(source_dir, tuple(want_suffix))]

        toscans = [os.path.join(source_dir, path) for path in toscans]

        # filter include and exclude path
        toscans = FilterPathUtil(params).get_include_files(toscans, relpos)

        # bugfix - 在文件前后加上双引号，变成字符串，防止文件路径中有空格，pylint无法扫描
        toscans = [PythonTool.handle_path_with_space(path) for path in toscans]

        LogPrinter.info('待扫描文件数: %d' % len(toscans))
        return toscans

    @staticmethod
    def handle_path_with_space(path):
        """
        处理文件路径中包含空格的情况，同时要适配windows下cmd的格式，""(双引号)
        :param path:
        :return:
        """
        return "\""+path+"\""
