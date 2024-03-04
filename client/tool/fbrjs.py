#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
FbRjs:扫描项目中的reactjs的版本号。要求大于等于16.0.0
"""

import json
import os
import re
import linecache

from util.errcode import E_NODE_TASK_CONFIG
from util.exceptions import TaskError
from util.pathlib import PathMgr
from util.pathfilter import FilterPathUtil
from task.codelintmodel import CodeLintModel
from util.logutil import LogPrinter


logger = LogPrinter

class Fbrjs(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.sensitive_word_maps = {
            "fbrjs": "Tool",
            "Fbrjs": "Tool"
        }

    def analyze(self, params):
        """
        扫描源码中是否包含react
        :param params:
        :return:
        """
        source_dir = params.source_dir
        filter_mgr = FilterPathUtil(params)
        relpos = len(source_dir) + 1

        issues = []
        package_json_list = []
        self._get_package_json(source_dir, package_json_list)
        package_json_list = [path for path in package_json_list if not filter_mgr.should_filter_path(path[relpos:])]
        LogPrinter.info(f"搜索到的package文件有: f{package_json_list}")
        if not package_json_list:
            # 项目根目录下有package.json文件，扫描项目中的react的js文件
            LogPrinter.debug("no package.json")
            toscans = PathMgr().get_dir_files(source_dir, (".js", ".jsx"))
            for file in toscans:
                reacrJsFile = re.match(".*/[^/]*react[^/]*$", file, re.I)
                if not reacrJsFile:
                    continue
                jsContent = open(file, "r").read().strip()
                versionMatch = re.match(r"(^/\*.*?v((\d{1,2})\.\d{1,2}\.\d{1,2})).*?\*/", jsContent, re.I | re.U | re.S)
                if versionMatch and int(versionMatch.group(3)) < 16 and versionMatch.group(2) != "15.6.2":
                    path = file[relpos:]
                    if filter_mgr.should_filter_path(path):
                        continue
                    msg = (
                        "该项目使用的ReactJs的版本号是:"
                        + versionMatch.group(2)
                        + ",版本号小于16.0.0或者不为15.6.2，需要更新到16.0.0版本以上或者为15.6.2版本。对应模块为："
                        + file
                    )
                    issues.append(
                        {
                            "path": path,
                            "rule": "FbRjs",
                            "msg": msg,
                            "line": versionMatch.group(1).count("\n") + 1,
                            "column": 100,
                        }
                    )
        else:
            LogPrinter.debug("have package.json")
            self._scan_package_json(issues, package_json_list, relpos, filter_mgr)

        LogPrinter.debug(issues)
        return issues

    def _scan_package_json(self, issues, package_json_list, relpos, filter_mgr):
        """
        项目根目录下有package.json文件，遍历json，看是否包含react关键字
        :return:
        """
        for package_json in package_json_list:
            LogPrinter.info(f"正在扫描: {package_json}")
            with open(package_json, "r") as f:
                try:
                    packageJsonContent = json.loads(f.read())
                except json.decoder.JSONDecodeError as err:
                    logger.info("项目文件 %s 格式有误读取失败" % package_json)
                    raise TaskError(code=E_NODE_TASK_CONFIG, msg='json读取失败%s' % str(err))
            if not isinstance(packageJsonContent, dict):
                continue

            strList = linecache.getlines(package_json)

            for (k, v) in packageJsonContent.items():
                kmatch = re.match(".*dependencies", k, re.I)
                if not kmatch:
                    continue
                LogPrinter.debug(kmatch.group())
                if not isinstance(v, dict):
                    continue
                for (k1, v1) in v.items():
                    # 如不是字符串，则跳过
                    if not isinstance(v1, str):
                        continue
                    reactMatch = re.match(r"^react((-dom((-server)|(-fiber))?)|(-with-addons))?$", k1, re.I)
                    if not reactMatch:
                        continue
                    LogPrinter.info(f"当前value是: {v1}")
                    versionMatch = re.match(r"\D*((\d{1,2})(\.\d{1,2}){0,2})", v1, re.I | re.U)
                    if versionMatch and int(versionMatch.group(2)) < 16 and versionMatch.group(1) != "15.6.2":
                        path = package_json[relpos:]
                        if filter_mgr.should_filter_path(path):
                            continue
                        lineContent = '"' + k1 + '": "' + v1 + '",'
                        LogPrinter.debug(lineContent)
                        for lineCount, lineStr in enumerate(strList):
                            if lineStr.strip() == lineContent:
                                # LogPrinter.debug('在', packageJson, '文件的第', lineCount + 1, '行')
                                msg = (
                                    "该项目使用的ReactJs的版本号是:"
                                    + versionMatch.group(1)
                                    + ",版本号小于16.0.0或者不为15.6.2，需要更新到16.0.0版本以上或者为15.6.2版本。对应模块为："
                                    + k1
                                )
                                issues.append(
                                    {"path": path, "rule": "FbRjs", "msg": msg, "line": lineCount + 1, "column": 0}
                                )

    def _get_package_json(self, root_dir, toscans):
        """
        查找项目目录下的package.json
        :param root_dir:
        :param toscans:
        :return:
        """
        for fileOrDir in os.listdir(root_dir):
            path = os.path.join(root_dir, fileOrDir)
            if os.path.isdir(path):
                self._get_package_json(path, toscans)
            elif fileOrDir == "package.json":
                toscans.append(path)


tool = Fbrjs

if __name__ == "__main__":
    pass
