# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
配置tool内部调用需要的环境变量
"""


import os
import sys
import logging

from node.app import settings
from util.envset import EnvSet
from task.basic.common import subprocc_log
from util.subprocc import SubProcController

logger = logging.getLogger(__name__)


class ToolEnvSet(object):
    """环境变量配置"""

    @staticmethod
    def set_go_env(params, force_inner=False):
        """
        自动识别机器go环境:
        1. 优先使用本地机器环境中的Go环境
        2. 本地机器没有go的话，便使用CodeDog自带的go环境
        :param params:
        :param force_inner: 强制使用内置的go环境
        :return:
        """
        source_dir = params.source_dir
        tool_name = params["tool_name"]
        go_home = os.path.basename(os.environ.get("GO_HOME", None))
        go_path = os.environ.get("GOPATH", None)
        go_root = os.environ.get("GOROOT", None)

        # 判断本地go环境是否可用
        # 不可用，或者该机器没有go环境的话，便使用codedog维护的go环境
        if force_inner or SubProcController(["go", "version"]).wait() != 0:
            logger.info("建议客户将所有第三方依赖库存放到src/vendor目录下，这样可以保证编译时能够被依赖到。")
            EnvSet().set_tool_env(
                {
                    tool_name: {
                        "env_path": {"GOROOT": go_home},
                        "env_value": {},
                        "path": ["%s/bin" % go_home, f"{go_home}/go/bin"],
                        "tool_url": [],
                    }
                }
            )
            if not go_path:
                go_path = []
            else:
                # 可以在CodeDog平台上面设置GOPATH指向代码库内的目录
                # 比如：GOPATH=$SOURCE_DIR/imcomm:$SOURCE_DIR:$SOURCE_DIR/third:$GOPATH
                go_path = go_path.split(os.pathsep)
            go_path.extend([os.path.join(settings.TOOL_BASE_DIR, "%s/go" % go_home), source_dir])
            os.environ["GOPATH"] = os.pathsep.join(go_path)

            if not go_root:
                os.environ["GOROOT"] = os.path.join(settings.TOOL_BASE_DIR, go_home)
        elif not go_path or not go_root:
            # 机器有go环境，但没有设置GOPATH
            logger.info(
                "建议客户机器设置GOPATH指向go项目根目录和项目依赖路径，最好将所有第三方依赖库存放到项目的src/vendor目录下，保证项目编译通过，以及设置GOROOT指向go安装位置，以防工具执行失败。"
            )

        logger.info("当前使用的Go版本如下所示:")
        SubProcController(
            ["go", "version"], stdout_line_callback=subprocc_log, stderr_line_callback=subprocc_log
        ).wait()
        logger.info("GOROOT: %s", os.environ.get("GOROOT", ""))
        logger.info("GOPATH: %s", os.environ.get("GOPATH", ""))

    @staticmethod
    def is_py_avail(pyname="python", version=None):
        """
        判断本地机器是否存在对应版本的python环境
        :param pyname: 默认是python, 还可能是python2, python3
        :param version: None, 2或3, 默认是None, None表示不需要判断版本
        :return:
        """
        spc = SubProcController([pyname, "--version"])
        spc.wait()
        so = spc.get_stdout()
        if so:
            log = so.read()
            so.close()
        else:
            log = ""
        if spc.returncode == 0:
            if version is None:
                return True
            if log.find("Python " + str(version) + ".") != -1:
                return True
        return False

    @classmethod
    def auto_set_py_env(cls, version=3):
        """
        如果机器中有python环境，则使用机器环境。否则加载Puppy自身Python环境到环境变量中
        :param params:
        :param version: 2或3，默认是3
        :return:
        """
        if ToolEnvSet.is_py_avail(version=version):
            return
        cls.set_py_env(version)

    @staticmethod
    def set_py_env(version=3):
        python_home = "PYTHON%s7_HOME" % str(version)
        logger.info("正在启用CodeDog内置的Python环境")
        if sys.platform == "win32":
            path = [os.path.join(os.environ.get(python_home), "Scripts"), os.environ.get(python_home)]
        else:
            path = [os.path.join(os.environ.get(python_home), "bin")]
        EnvSet().set_tool_env({"tool": {"env_path": {}, "env_value": {}, "path": path, "tool_url": []}})

    @staticmethod
    def search_tool_env(key):
        """
        遍历搜索多版本工具环境变量，然后设置为公共环境变量。
        比如：搜寻NODE_HOME_12_16_3，然后设置为NODE_HOME
        因为多版本的node会公用NODE_HOME这个环境变量key
        :param key:
        :return:
        """
        envs = os.environ

        value = envs.get(key, None)
        logger.info(f"当前该环境变量为：{key}={value}")
        if value and value.startswith(settings.TOOL_BASE_DIR):
            return value
        for env_key in envs:
            if not env_key.startswith(key):
                continue
            value = envs.get(env_key, None)
            if value and value.startswith(settings.TOOL_BASE_DIR):
                envs[key] = value
                logger.info(f"{key}={value}")
                return value
