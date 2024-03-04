# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
检查项目中的大文件是否储存在LFS服务器
"""


import os
import logging
import json

from task.basic.common import subprocc_log
from tool.util.language_maps import CODEDOG_LANGUAGE_MAPS
from util.exceptions import AnalyzeTaskError
from util.subprocc import SubProcController


logger = logging.getLogger(__name__)


class LFSChecker(object):
    def run(self, params, scan_files, rule_name):
        """
        :param params:
        :param scan_files:
        :param rule_name:
        :return json:
        """
        source_dir = params.get("source_dir")
        # 获取规则参数选取过滤或只扫描指定后缀文件，默认过滤所有代码文件
        exc_files, inc_files, size = self.__get_rule_params(params["rule_list"], rule_name)
        logger.info(exc_files)
        big_files = self.__find_all_files(params, size, exc_files, inc_files)
        issues = list()
        logger.info("big files %s", big_files)
        if big_files:
            # 读取lfs配置
            lfs_config = os.path.join(source_dir, ".gitattributes")
            lfs_files = set()
            # 有些库没有开启lfs情况
            if not os.path.exists(lfs_config):
                for big_file in big_files:
                    issues.append(
                        {
                            "column": 0,
                            "line": 0,
                            "msg": "较大的文件建议采用LFS储存形式",
                            "rule": "LFSChecker",
                            "path": big_file,
                            "refs": [],
                        }
                    )
                logger.info("result: %s", issues)
                return issues
            with open(lfs_config, "r") as f:
                lines = f.readlines()
                for line in lines:
                    # 可能存在末尾空行
                    if line:
                        lfs_files.add(self.__format_lfs_file(line))
            logger.info("LFS文件包括: %s", lfs_files)
            for big_file in big_files:
                if os.path.basename(big_file) not in lfs_files:
                    issues.append(
                        {
                            "column": 0,
                            "line": 0,
                            "msg": "较大的文件建议采用LFS储存形式",
                            "rule": "LFSChecker",
                            "path": big_file,
                            "refs": [],
                        }
                    )
        logger.info("result: %s", issues)
        return issues

    def __format_lfs_file(self, line):
        """
        用于读取gitattributes配置中的文件名
        """
        return line.split(" ")[0]  # 以空格区分第一个便是文件名

    def __find_all_files(self, params, size, exc_files, inc_files):
        """
        :param params:
        :param size:
        :return list:
        """
        big_files = []
        work_dir = params["work_dir"]
        source_dir = params["source_dir"]
        find_cmd = ["find", source_dir, "-type", "f", "-size", "+{}".format(size)]
        error_output = os.path.join(work_dir, "output.txt")
        # windows环境换用其他命令
        if os.name == "nt":
            find_cmd = [
                "for",
                "/r",
                source_dir,
                "%a",
                "in",
                "(*)",
                "do",
                "@if",
                "%~za",
                "gtr",
                self.__trans_size(size),
                "echo",
                "%~fa",
            ]
        logger.debug("cmd:%s", " ".join(find_cmd))
        sp = SubProcController(
            command=find_cmd, cwd=work_dir, stdout_filepath=error_output, stdout_line_callback=subprocc_log,
        )
        sp.wait()
        if not os.path.exists(error_output):
            logger.info("不存在大文件")
            return []
        with open(error_output, "r") as f:
            lines = f.readlines()
            # 去除换行符
            lines = "".join(lines).split("\n")[0:-1]  # 去除最后的空字符
            # 判断是否只扫描一种大文件格式
            if inc_files:
                for line in lines:
                    if line.find(".git") != -1:
                        continue
                    ext = os.path.os.path.splitext(line)[-1]
                    if ext in inc_files:
                        big_files.append(os.path.join(source_dir, line))
            # 没有include则查看是否有要屏蔽的文件后缀，默认屏蔽所有的代码文件
            else:
                for line in lines:
                    if line.find(".git") != -1:
                        continue
                    ext = os.path.os.path.splitext(line)[-1]
                    if ext not in exc_files:
                        big_files.append(os.path.join(source_dir, line))
        return big_files

    def __get_rule_params(self, rule_list, rule_name):
        """
        用来过滤代码文件和指定文件后缀
        :param rule_list:
        :param rule_name:
        :return tuple(exc_files, inc_files, size):
        """
        exc_files = []
        inc_files = []
        size = "10M"
        rule_param = {}
        # 获取规则参数
        for rule in rule_list:
            if rule["name"] == rule_name:
                rule_param = rule["params"]
        # 过滤所有代码文件
        for ext in CODEDOG_LANGUAGE_MAPS.values():
            exc_files.extend(ext)
        # 规则参数采用json格式，解析参数
        if rule_param:
            try:
                rule_param = json.loads(rule_param)
            except json.decoder.JSONDecodeError:
                logger.error("规则%s参数,请使用Json格式", rule_name)
                raise AnalyzeTaskError("规则参数解析错误")
            exclude = rule_param.get("exclude")
            include = rule_param.get("include")
            if type(exclude) is list:
                exc_files.extend(exclude)
            elif type(exclude) is str:
                exc_files.append(exclude)
            if type(include) is list:
                inc_files.extend(include)
            elif type(include) is str:
                inc_files.append(include)
            size = rule_param.get("size") if rule_param.get("size") else "10M"
        return (set(exc_files), set(inc_files), size)

    def __trans_size(self, size):
        """
        大小转换为windows格式
        """
        if size.endswith("M"):
            return str(int(size[0:-1]) * 1024 * 1024)
        elif size.endwith("G"):
            return str(int(size[0:-1]) * 1024 * 1024 * 1024)
        elif size.endwith("K"):
            return str(int(size[0:-1]) * 1024)


checker = LFSChecker

if __name__ == "__main__":
    pass
