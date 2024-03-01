# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
切换xcode版本
"""


import os
import logging

from task.basic.common import subprocc_log
from util.subprocc import SubProcController

logger = logging.getLogger(__name__)

class XcodeSwitch(object):
    @staticmethod
    def set_xcodebuild_version():
        """
        根据项目环境变量 XCODE_VERSION 选择对应版本的xcodebuild命令
        :return: 将项目对应版本的xcodebuild路径加载到path环境变量最前面
        """
        xcode_version = os.environ.get('XCODE_VERSION', None)
        if xcode_version:
            xcode_path = "/Applications/Xcode_%s.app/Contents/Developer/usr/bin" % xcode_version
            if os.path.exists(xcode_path):
                path_env = os.environ["PATH"]
                os.environ["PATH"] = os.pathsep.join([xcode_path, path_env])
                # logger.info(">>> PATH: %s" % os.environ.get("PATH"))
            else:
                logger.info("Xcode版本(%s)不存在,将使用系统默认的Xcode版本.", xcode_path)
            # 查看当前使用的xcode版本
            logger.info("查看当前使用的Xcode版本...")
            SubProcController(command=["xcodebuild", "-version"],
                              stdout_line_callback=subprocc_log,
                              stderr_line_callback=subprocc_log,
                              stdout_filepath=None,
                              stderr_filepath=None).wait()
            logger.info("如果Xcode版本与项目不匹配,请在CodeDog项目配置中设置XCODE_VERSION环境变量,如 XCODE_VERSION=10.1")
