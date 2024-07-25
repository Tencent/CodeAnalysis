# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
高性能压缩模块
"""

import logging
import os
import platform
import zipfile

from settings.base import WORK_DIR
from util.subprocc import SubProcController
from util.exceptions import ZIPError, TransferModuleError, NodeConfigError
from util.pathlib import PathMgr
from util.envset import EnvSet

logger = logging.getLogger(__name__)

# 压缩解压的时间上限
ZIP_TIME_LIMIT = 30 * 60
ZIP_HOME = "ZIP_HOME"


class Zip(object):
    def __init__(self):
        """
        检查工具的存在与是否可用
        """
        # logger.info("初始化zip模块中...")
        if not os.environ.get(ZIP_HOME, False):
            raise NodeConfigError("the node does not have ZIP tool, please check.")
        self.ZIP_TOOL_NAME = "7z"
        if platform.platform().find("debian") >= 0:
            logger.info("platform: %s" % platform.platform())
            logger.info(
                "检测到在ubuntu系统中调用zip，因此将调用7z_ubuntu。（7z_ubuntu可能存在兼容问题，如果异常，请自行安装:sudo apt-get install p7zip-full）"
            )
            self.ZIP_TOOL_NAME = "7z_ubuntu"

    def compress(self, path, zip_file):
        """
        基于7z实现的压缩，默认使用16线程极速压缩
        :param path: 被压缩的资源路径
        :param zip_file: 压缩完成生成的文件
        :return:
        """
        logger.info("zip模块执行压缩操作...")
        args = [
            os.path.join(os.environ[ZIP_HOME], self.ZIP_TOOL_NAME),
            "a",
            "-t7z",
            zip_file,
            "%s/*" % path,
            "-mmt16",
            "-mx1",
        ]
        if os.path.exists(zip_file):
            PathMgr().rmpath(zip_file)
        try:
            args = PathMgr().format_cmd_arg_list(args)
            process = SubProcController(
                args,
                print_enable=False,
                shell=False,
                stdout_filepath=None,
                stderr_filepath=None,
                stdout_line_callback=self.compress_subprocc_log,
                stderr_line_callback=self.compress_subprocc_log,
                env=EnvSet().get_origin_env(),
            )
            process.wait(ZIP_TIME_LIMIT)
        except FileNotFoundError:
            self.zipfile_compress(path, zip_file)
        if not os.path.exists(zip_file):
            err_msg = "compress error! zip file is empty, please check! 如果是ubuntu环境，7z_ubuntu可能存在兼容问题，" \
                      "请自行安装:sudo apt-get install p7zip-full"
            logger.error(err_msg)
            raise ZIPError(err_msg)
        return True

    def decompress_by_7z(self, zip_file, path, print_enable=False):
        """
        基于7z实现的解压，使用默认参数（因为没得选）
        :param zip_file: 被解压的压缩包
        :param path: 解压到指定位置
        :param print_enable: 是否输出日志
        :return:
        """
        args = [os.path.join(os.environ[ZIP_HOME], self.ZIP_TOOL_NAME), "x", "-y", "-o" + path, zip_file]

        args = PathMgr().format_cmd_arg_list(args)
        if print_enable:
            output = self.subprocc_log
        else:
            output = None
        process = SubProcController(
            args,
            print_enable=False,
            shell=False,
            stdout_filepath=None,
            stderr_filepath=None,
            stdout_line_callback=output,
            stderr_line_callback=self.subprocc_log,
            env=EnvSet().get_origin_env(),
        )
        process.wait(ZIP_TIME_LIMIT)
        if not os.path.exists(path):
            err_msg = "decompress error! zip file is empty, please check file transfer! " \
                      "如果是ubuntu环境，7z_ubuntu可能存在兼容问题，请自行安装:sudo apt-get install p7zip-full"
            logger.error(err_msg)
            raise TransferModuleError(err_msg)

    def decompress(self, zip_file, path):
        logger.info("zip模块执行解压操作...")
        # 20190927 bug-fixed, 防止在当前目录下删除当前目录，出现权限异常情况
        cur_dir = os.getcwd()
        cur_dir_is_changed = False
        if PathMgr().format_path(cur_dir) == PathMgr().format_path(path):
            logger.info("Decompress dir is current dir, can not delete it directory, change to parent directory first.")
            # 如果要删除的是当前工作目录，先切换到上层目录，再删除
            os.chdir("..")
            cur_dir_is_changed = True

        try:
            if os.path.exists(path):
                PathMgr().rmpath(path)

            self.decompress_by_7z(zip_file, path, print_enable=True)
        finally:
            # 恢复进入到当前工作目录
            logger.info("Go back to the current working directory.")
            if cur_dir_is_changed and os.path.exists(cur_dir):
                os.chdir(cur_dir)
        return True

    def subprocc_log(self, line):
        logger.info(line)
        if line.find("Can not open the file as archive"):
            raise TransferModuleError("解压失败，压缩文件损坏或格式不对")
    
    def compress_subprocc_log(self, line):
        logger.info(line)

    @staticmethod
    def zipfile_compress(path, zip_file):
        """
        通过zipfile执行压缩
        :param path:
        :param zip_file:
        :return:
        """
        logger.info("通zipfile执行压缩.")
        zp = zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED)
        for dirpath, dirnames, filenames in os.walk(path):
            fpath = dirpath.replace(path, "")  # 这一句很重要，不replace的话，就从根目录开始复制
            fpath = fpath and fpath + os.sep or ""  # 这句话理解我也点郁闷，实现当前文件夹以及包含的所有文件的压缩
            for filename in filenames:
                zp.write(os.path.join(dirpath, filename), fpath + filename)
        zp.close()


if __name__ == "__main__":
    pass
