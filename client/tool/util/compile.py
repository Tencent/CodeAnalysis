# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
对tool执行项目编译的公共处理进行封装
"""


import re
import os
import shlex
import queue
import platform
import stat

from util.envset import EnvSet
from util.pathlib import PathMgr
from util.exceptions import CompileTaskError
from util.logutil import LogPrinter
from util.subprocc import SubProcController
from util.tooldisplay import ToolDisplay

logger = LogPrinter


class BasicCompile(object):

    build_log_end = queue.Queue(20)
    stop_on_output_flag = False

    def __init__(self, params, sensitive, sensitive_word_maps, build_cmd=None, shell=True):
        """
        编译模块构造函数
        :param params:
        """
        self.params = params
        self.sensitive = sensitive
        self.sensitive_word_maps = sensitive_word_maps
        self.shell = shell
        # 编译条件1： 编译命令
        if build_cmd:
            self.build_cmd = build_cmd
        else:
            self.build_cmd = params["build_cmd"]
        if not self.build_cmd:
            raise CompileTaskError("编译语言项目执行静态分析需要输入编译命令，请填入编译命令后重试！")
        # 编译条件2： 编译项目路径
        self.build_cwd = params["source_dir"]
        build_cwd = os.environ.get("BUILD_CWD", None)
        self.build_cwd = os.path.join(self.build_cwd, build_cwd) if build_cwd else self.build_cwd
        # 编译条件3： 编译中断设置
        self.stop_on_output = os.environ.get("STOP_ON_OUTPUT")
        # 编译条件4： 执行前置命令
        self.pre_cmd()

    @staticmethod
    def generate_shell_file(cmd, log_flag=True, shell_name="tca_build"):
        """
        将编译命令保存到bash/bat的脚本文件中,并赋予可执行权限,返回执行该脚本文件的命令
        :param cmd: 编译命令字符串
        :param log_flag: 是否输出命令，默认输出
        :param shell_name: 生成的shell文件名
        :return: 执行该脚本文件的命令
        """
        work_dir = os.getcwd()
        if platform.system() == "Windows":
            file_name = f"{shell_name}.bat"
        else:
            file_name = f"{shell_name}.sh"
        shell_filepath = os.path.join(work_dir, file_name)
        # 格式化文件路径
        shell_filepath = PathMgr().format_path(shell_filepath)
        with open(shell_filepath, "w") as wf:
            wf.write(cmd)
        # 给文件授权可执行权限
        os.chmod(shell_filepath, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

        if log_flag:
            logger.info("Cmd:\n%s" % cmd)
            logger.info("Generated shell file: %s" % shell_filepath)

        if platform.system() == "Windows":
            return shell_filepath
        else:
            return "bash %s" % shell_filepath

    def pre_cmd(self):
        pre_cmd = self.params.get("pre_cmd", None)
        if not pre_cmd:
            return
        logger.info("do pre_cmd.")
        # 写入到shell文件后再执行，以支持多行命令
        pre_cmd = BasicCompile.generate_shell_file(pre_cmd, shell_name="tca_pre_cmd")
        if isinstance(pre_cmd, str):
            pre_cmd = shlex.split(pre_cmd)
        logger.info("run pre cmd shell file: %s" % " ".join(pre_cmd))
        SubProcController(
            pre_cmd,
            cwd=self.build_cwd,
            stdout_line_callback=self.print_log,
            stderr_line_callback=self.print_log,
            env=EnvSet().get_origin_env(),
            shell=self.shell,
        ).wait()

    def compile(self, build_out="subprocc_stdout.log", build_err="subprocc_stderr.log"):
        """
        执行编译操作
        :return:
        """
        build_cmd = self.build_cmd
        if isinstance(build_cmd, str):
            build_cmd = shlex.split(build_cmd)
        logger.info("basic compile start.")
        stop_on_output_str = self.stop_on_output

        if stop_on_output_str:
            self.print_log("subprocc stop_on_output mode: %s" % build_cmd)
            stop_on_output_str = "[^(STOP_ON_OUTPUT=)]" + stop_on_output_str + "|^" + stop_on_output_str
            pattern = re.compile(stop_on_output_str)

            def compile_cmd_callback(line):
                self.print_log(line)
                if self.build_log_end.full():
                    self.build_log_end.get()
                self.build_log_end.put_nowait(line)
                if pattern.search(line):
                    logger.info("terminate cmd on pattern %s" % stop_on_output_str)
                    spc.stop()
                    self.stop_on_output_flag = True

        else:
            self.print_log("subprocc normal mode: %s" % build_cmd)

            def compile_cmd_callback(line):
                self.print_log(line)
                if self.build_log_end.full():
                    self.build_log_end.get()
                self.build_log_end.put_nowait(line)

        self.print_log("run build cmd: %s" % " ".join(build_cmd))
        spc = SubProcController(
            build_cmd,
            cwd=self.build_cwd,
            stdout_line_callback=compile_cmd_callback,
            stderr_line_callback=compile_cmd_callback,
            stdout_filepath=build_out,
            stderr_filepath=build_err,
            env=EnvSet().get_origin_env(),
            shell=self.shell,
        )
        spc.wait()
        # 0 为常规返回码， -9为ant的返回码
        if self.stop_on_output_flag:
            logger.info("编译成功！")
            logger.info("basic compile done.")
            return

        self.handle_log(spc.returncode)

        logger.info("basic compile done.")

    def handle_log(self, returncode):
        """
        处理编译log，判断是否编译成功
        """
        exist_error_flag = False
        exist_success_flag = False
        exist_100_flag = False
        cov_no_file_emitted = False
        # 遍历编译日志队列
        while not self.build_log_end.empty():
            build_log_line = self.build_log_end.get()
            # 增加编译脚本找不到命令的情况
            if (
                build_log_line.lower().find("error") != -1
                or build_log_line.lower().find("build failed") != -1
                or build_log_line.lower().find(": command not found") != -1
                or build_log_line.lower().find(": 未找到命令") != -1
            ):
                exist_error_flag = True
            if build_log_line.lower().find("build successful") != -1:
                exist_success_flag = True
            if build_log_line.lower().find("units (100%)") != -1:
                exist_100_flag = True
            if build_log_line.lower().find("no files were emitted") != -1:
                cov_no_file_emitted = True

        logger.info("exist_error_flag : %s" % exist_error_flag)
        logger.info("exist_success_flag : %s" % exist_success_flag)
        logger.info("exist_100_flag : %s" % exist_100_flag)
        logger.info("cov_no_file_emitted : %s" % cov_no_file_emitted)

        success_returncode = [0, -9]
        if exist_100_flag:
            logger.info("编译成功！")
        elif returncode not in success_returncode and exist_error_flag:
            logger.info("编译结束，rc为：%d" % returncode)
            raise CompileTaskError(msg="项目编译失败，请确认当前版本是否能在本地进行编译！")
        elif returncode in success_returncode and exist_error_flag:
            logger.error("编译结束，可能存在异常，请注意，rc为%d" % returncode)
        elif exist_success_flag:
            logger.info("编译成功！")
        if cov_no_file_emitted:
            # 输出idir/build-log.txt内容，方便调试
            build_log = os.path.join(self.params["work_dir"], "idir", "build-log.txt")
            if os.path.exists(build_log):
                logger.info("idir/build-log.txt内容:")
                f = open(build_log)
                # 逐行读取，遇到无法解码的行，捕获异常并跳过（一次性读取，如果有无法解码的行，会异常）
                while True:
                    try:
                        line = f.readline()
                        if not line:  # 读到文件末尾,退出
                            break
                        else:
                            self.print_log(line)
                    except Exception as err:
                        logger.warning("readline error(%s), skip this line." % str(err))
                f.close()

            raise CompileTaskError(
                msg="项目编译失败，Tool监控编译时，未发现任何代码文件进行了编译，有可能是增量编译无任何代码文件改动导致，建议执行全量编译命令或者删除data/sourcedirs文件夹下所有文件！"
            )

    def print_log(self, message):
        """
        将日志中的敏感词替换掉，再打印日志
        :param message:
        :return:
        """
        ToolDisplay.print_log(self.sensitive, self.sensitive_word_maps, message)
