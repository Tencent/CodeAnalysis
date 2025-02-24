# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
GolangCI-Lint is a linters aggregator.
It's fast: on average 5 times faster than gometalinter.
It's easy to integrate and use, has nice output and has a minimum number of false positives.
It supports go modules.
"""

import os
import sys
import json
import yaml
import shlex

from shutil import copyfile
from multiprocessing import cpu_count

from node.app import settings
from util.logutil import LogPrinter
from util.pathfilter import FilterPathUtil
from task.codelintmodel import CodeLintModel
from util.subprocc import SubProcController
from tool.util.compile import BasicCompile
from tool.util.toolenvset import ToolEnvSet
from util.envset import EnvSet
from util.errcode import E_NODE_TASK_BUILD
from task.basic.common import subprocc_log
from util.configlib import ConfigReader
from util.exceptions import TaskError

logger = LogPrinter


class Golangcilint(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.sensitive_word_maps = {
            "GoLangCi-Lint": "Tool",
            "golangci-lint": "Tool",
            "golangcilint": "Tool",
        }

    def compile(self, params):
        """
        编译执行函数
        :param params:
        :return:
        """
        source_dir = params.source_dir
        ToolEnvSet.set_go_env(params)
        build_cmd = params.get("build_cmd", None)
        # 需要确保Go项目在机器上能够编译成功，确保执行扫描时候能够找到依赖
        build_cmd = shlex.split(BasicCompile.generate_shell_file(build_cmd)) if build_cmd else ["go", "build", "./..."]
        logger.info("build cmd: %s" % " ".join(build_cmd))
        rtcode = SubProcController(
            build_cmd,
            cwd=source_dir,
            env=EnvSet().get_origin_env(),
            stdout_line_callback=subprocc_log,
            stderr_line_callback=subprocc_log,
        ).wait()
        if rtcode != 0:
            logger.error("go项目编译失败，建议客户保证项目编译通过，否则可能导致部分依赖编译的规则出现漏报！")
        return True

    def analyze(self, params):
        """
        分析执行函数
        :param params:
        :return:
        """
        source_dir = params.source_dir
        golangcilint_home = os.environ.get("GOLANGCILINT_HOME")
        # 多版本运行
        if "GOLANGCILINT_VERSION" in os.environ:
            version = os.environ.get("GOLANGCILINT_VERSION")
            version_path = "golangci-lint-{}".format(version)
            golangcilint_home = os.path.join(settings.TOOL_BASE_DIR, version_path)
        golangcilint_bin = os.path.join(golangcilint_home, "golangci-lint")
        if sys.platform == "win32":
            golangcilint_bin += ".exe"
        work_dir = params.work_dir
        rules = params["rules"]
        incr_scan = params["incr_scan"]
        last_revision = params["scm_last_revision"]
        # puppy通配符转换为的正则在该工具会出错
        re_path_exclude = params.path_filters.get("re_exclusion", [])
        wild_path_exclude = params.path_filters.get("wildcard_exclusion", [])
        re_path_exclude.extend(params.path_filters.get("yaml_filters").get("lint_exclusion", []))
        re_path_exclude.extend([exclude.replace("*", ".*") for exclude in wild_path_exclude])
        path_include = params.path_filters.get("wildcard_inclusion", [])
        filter_mgr = FilterPathUtil(params)
        error_output = os.path.join(work_dir, "result.json")

        ToolEnvSet.set_go_env(params)
        self.print_log("当前使用的golangci-lint为: %s" % golangcilint_bin)
        scan_cmd = [
            golangcilint_bin,
            "run",
            "--verbose",
            "--out-format=json",
            "--issues-exit-code=0",
            "--print-resources-usage",
            "--concurrency=%s" % str(cpu_count()),
        ]

        config_file = self.config(params)
        if config_file:
            scan_cmd.extend(["--config", config_file])

        # 设置扫描增量
        if incr_scan and last_revision:
            # 扫描指定版本以后的版本变化文件
            scan_cmd.extend(["--new-from-rev", last_revision])

        # 工具额外配置
        # --exclude 可以过滤issue，支持正则
        # 从vendor中查找依赖
        # GOLANGCILINT_OPTION_PARAMS=--modules-download-mode=vendor
        if os.environ.get("GOLANGCILINT_OPTION_PARAMS", None):
            scan_cmd.extend(shlex.split(os.environ.get("GOLANGCILINT_OPTION_PARAMS")))

        # 设置扫描前过滤
        if re_path_exclude:
            # 支持正则表达式
            # --skip-dirs 过滤目录，直接写目录相对路径即可, 逗号分割或者多次赋值：--skip-dirs=type_tests,extra,any_tests
            # 扫描前过滤
            # --skip-files 过滤文件，正则表达式, 逗号分割或者多次赋值：--skip-files=type_tests/.*.go,misc_tests/.*
            # 也会执行扫描，不过是后续过滤掉对应文件的issue
            exclusion = list()
            for path in re_path_exclude:
                exclusion.append("--skip-files=%s" % path)
            scan_cmd.extend(exclusion)

        # 由于工具扫描前会搜索所有文件的依赖，包括已经设置--skip-files的文件, 导致会检索一些不相关的依赖而执行失败
        # 使用...和指定文件扫描，结果会有区别。优先是...
        if path_include:
            # 只支持dir/.*这种匹配模式
            scan_cmd.extend([path.replace("/*", "/...") for path in path_include])
        else:
            # 增量时候扫描文件，部分小工具只能扫描目录，会扫描失败，所以该会全量
            scan_cmd.append("./...")

        self.print_log("scan_cmd: %s" % " ".join(scan_cmd))
        SubProcController(
            scan_cmd,
            cwd=source_dir,
            env=EnvSet().get_origin_env(),
            stdout_filepath=error_output,
            stderr_line_callback=self._err_callback,
            shell=True,
        ).wait()

        # 处理结果
        if not os.path.exists(error_output) or os.stat(error_output).st_size == 0:
            logger.info("result is empty ")
            return []
        with open(error_output, "r") as f:
            raw_warning_json = json.loads(f.read())

        # 结果为None时候，返回空数组
        if not raw_warning_json.get("Issues"):
            return []

        issues = []
        for raw_warning in raw_warning_json.get("Issues", []):
            path = raw_warning["Pos"]["Filename"]
            rule = raw_warning["FromLinter"]
            if filter_mgr.should_filter_path(path) or rule not in rules:
                continue
            msg = raw_warning["Text"]
            line = int(raw_warning["Pos"]["Line"])
            column = int(raw_warning["Pos"]["Column"])
            issues.append({"path": path, "rule": rule, "msg": msg, "line": line, "column": column})
        logger.info(issues)

        return issues

    def _err_callback(self, line):
        """
        工具运行时候的异常回调
        :param line:
        :return:
        """
        self.print_log(line)

        if line.find("Running error: context loading failed:") != -1:
            raise TaskError(code=E_NODE_TASK_BUILD, msg="该工具没有查找到项目完整的依赖导致扫描失败，请确保项目能在该机器上查找到完整的依赖包并正常编译成功。")

    def config(self, params):
        """
        1. 支持配置文件--no-config --config PATH
        2. 默认使用CodeDog自己维护的配置文件
        3. 设置环境变量，使用以备份的配置文件
        4. 设置环境变量，使用代码库中的配置文件
        注意：过滤和增量扫描是公共模块，对所有配置文件都有效，所以不放在配置文件里面
        :param params:
        :return:
        """
        source_dir = params.source_dir
        work_dir = params.work_dir
        rules = params["rules"]
        rule_list = params["rule_list"]
        envs = os.environ
        config_home = os.path.join(envs.get("GOLANGCILINT_HOME"), "config")

        os.environ["GL_DEBUG"] = "linters_output"
        os.environ["GOPACKAGESPRINTGOLISTERRORS"] = "1"
        os.environ["GO111MODULE"] = "auto"

        config_type = envs.get("GOLANGCILINT_TYPE", None)
        # custom
        if config_type == "custom":
            return None
        elif config_type:
            return os.path.join(config_home, "%s_golangci.yml" % config_type)

        if "GOLANGCILINT_CONFIG" in envs:
            return os.path.join(source_dir, envs.get("GOLANGCILINT_CONFIG"))

        config_file = os.path.join(work_dir, ".golangci.yml")
        if os.path.exists(config_file):
            os.remove(config_file)
        copyfile(os.path.join(config_home, ".golangci.example.yml"), config_file)
        f = open(config_file)
        config = yaml.safe_load(f)
        f.close()

        config["linters"]["enable"] = [rule for rule in rules]
        for rule in rule_list:
            # 采用json格式读取参数
            try:
                if rule["params"]:
                    config["linters-settings"][rule["name"]] = json.loads(rule["params"])
            except json.decoder.JSONDecodeError:
                logger.info("json decoder failed,")
                if "[block]" in rule["params"]:
                    rule_params = rule["params"]
                else:
                    rule_params = "[block]\r\n" + rule["params"]
                rule_params_dict = ConfigReader(cfg_string=rule_params).read("block")
                config["linters-settings"][rule["name"]] = rule_params_dict

        f = open(config_file, "w")
        yaml.dump(config, f, default_flow_style=False)
        f.close()

        return config_file


tool = Golangcilint

if __name__ == "__main__":
    pass
