# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
checkstyle 扫描任务
"""

import os
import re
import sys
import threading
import uuid

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from task.scmmgr import SCMMgr
from util.pathfilter import FilterPathUtil
from task.codelintmodel import CodeLintModel
from util.subprocc import SubProcController
from util.exceptions import AnalyzeTaskError
from util.configlib import ConfigReader
from util.scanlang.callback_queue import CallbackQueue
from util.logutil import LogPrinter


class CheckStyle(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.model_config_file = os.path.join(os.environ["CHECKSTYLE_HOME"], "config", "model.xml")
        self.sensitive_word_maps = {"checkstyle": "Tool", "Checkstyle": "Tool"}

    def analyze(self, params):
        source_dir = params["source_dir"]
        envs = os.environ
        rule_list = params["rule_list"]
        incr_scan = params["incr_scan"]
        path_exclude = params.path_filters.get("exclusion", [])
        path_include = params.path_filters.get("inclusion", [])
        checkstyle_home = envs.get("CHECKSTYLE_HOME")

        # analyze step
        config_file = self.generate_config(rule_list)

        # 指定内置的配置文件
        config_type = envs.get("CHECKSTYLE_TYPE", None)
        if config_type:
            config_file = os.path.join(checkstyle_home, "config", "%s_checks.xml" % config_type)
        # 指定代码库中的checkstyle配置文件
        if "CHECKSTYLE_CONFIG" in envs:
            config_file = os.path.join(source_dir, envs.get("CHECKSTYLE_CONFIG"))
        LogPrinter.info("config file: %s" % config_file)

        scan_cmd = [
            os.path.join(os.environ["JDK_8_HOME"], "bin", "java"),
            "-jar",
            os.path.join(os.environ["CHECKSTYLE_HOME"], "checkstyle.jar"),
            "-c",
            config_file,
            "--debug",
        ]

        if path_exclude:
            for path in path_exclude:
                # 这里是为了适配win下路径分隔符\的情况，才需要path.replace("/", os.sep)
                scan_cmd.append('--exclude-regexp="%s"' % path.replace("/", os.sep))

        # 支持增全量
        toscans = []
        want_suffix = ".java"
        if incr_scan:
            diffs = SCMMgr(params).get_scm_diff()
            toscans = [
                os.path.join(source_dir, diff.path).replace(os.sep, "/")
                for diff in diffs
                if diff.path.endswith(tuple(want_suffix)) and diff.state != "del"
            ]
            relpos = len(source_dir) + 1
            toscans = FilterPathUtil(params).get_include_files(toscans, relpos)
        else:
            toscans = [source_dir]
        # sh参数个数有限制
        if sys.platform == "win32" and len(max(toscans)) > 32500:
            toscans = [source_dir]

        if not toscans:
            LogPrinter.debug("To-be-scanned files is empty ")
            return []

        issues = ThreadRunner(scan_cmd, source_dir, params).run(toscans)
        return issues

    def insert_rule(self, node, rule_name, params):
        """
        在xml节点中插入规则子节点
        :param node:
        :param rule_name:
        :param params:
        :return:
        """
        if params is None:
            params = ""

        # 每个规则可以多次设置，以<br>做换行分隔
        rule_params = params.split("<br>")
        for param in rule_params:
            if "[checkstyle]" in param:
                rule_params = param
            else:
                rule_params = "[checkstyle]\r\n" + param
            rule_params_dict = ConfigReader(cfg_string=rule_params).read("checkstyle")

            child_node = ET.Element("module")
            child_node.set("name", rule_name)
            if rule_params_dict:
                for property_name in rule_params_dict:
                    property_node = ET.Element("property")
                    property_node.set("name", property_name)
                    property_node.set("value", rule_params_dict[property_name])
                    child_node.append(property_node)
            node.append(child_node)

    def generate_config(self, rules):
        """
        生成checkstyle-配置文件
        :param rules:
        :return:
        """
        # 这些规则仅存放于TreeWalker同级
        special_rule_set = [
            "Header",
            "RegexpHeader",
            "JavadocPackage",
            "UniqueProperties",
            "Translation",
            "NewlineAtEndOfFile",
            "RegexpMultiline",
            "RegexpOnFilename",
            "RegexpSingleline",
            "FileLength",
            "FileTabCharacter",
            "LineLength",
            "OrderedProperties",
        ]
        special_rule = []

        # 1. 读取空模板
        config_file = os.path.join(os.path.abspath(os.curdir), "config.xml")
        if not os.path.exists(self.model_config_file):
            raise AnalyzeTaskError(
                f"The template configuration file {self.model_config_file} does not exist, please check! "
            )
        open(config_file, "wb").write(open(self.model_config_file, "rb").read())

        config_data = ET.ElementTree(file=config_file)
        root = config_data.getroot()
        # 添加扫描文件后缀
        property_node = ET.Element("property")
        property_node.set("name", "fileExtensions")
        property_node.set("value", "java, properties, xml")
        root.append(property_node)

        # 2. 普通规则处理 （TreeWalker子节点）
        main_node = root.find('module[@name="TreeWalker"]')
        for rule in rules:
            # 去掉规则名中的后缀
            if rule["name"].find("_") != -1:
                rule["name"] = rule["name"][: rule["name"].find("_")]
            if not rule["name"] in special_rule_set:
                self.insert_rule(main_node, rule["name"], rule.get("params", None))
            else:
                special_rule.append(rule)

        # 3. 针对特殊的规则单独处理
        if special_rule:
            for rule in special_rule:
                self.insert_rule(root, rule["name"], rule.get("params", None))

        config_data.write(config_file)
        # config需要增加注释才可以运行
        f = open(config_file, "r")
        lines = f.readlines()
        f.close()
        f = open(config_file, "w")
        f.writelines(
            [
                '<?xml version="1.0" encoding="UTF-8"?>\n',
                (
                    '<!DOCTYPE module PUBLIC "-//Puppy Crawl//DTD Check Configuration 1.2//EN" '
                    '"http://www.puppycrawl.com/dtds/configuration_1_2.dtd">\n'
                ),
            ]
        )
        f.writelines(lines)
        f.close()

        return config_file


class CheckStyleRunner(object):
    def __init__(self):
        pass

    def run_checkstyle_on_file(self, file_path, scan_cmd, source_dir, params):
        """
        多线程执行checkstyle
        """
        issues = []
        # 临时输出文件，使用uuid防止重名
        tmp_log = "{}_log.txt".format(os.path.join(os.path.abspath(os.curdir), uuid.uuid1().hex))
        tmp_tool_output = "{}_output.txt".format(os.path.join(os.path.abspath(os.curdir), uuid.uuid1().hex))
        cmd = scan_cmd + ["-o", tmp_tool_output, file_path]
        LogPrinter.info("scan file: %s" % file_path)

        CheckStyle(params).print_log("cmd: %s" % " ".join(cmd))
        spc = SubProcController(
            cmd,
            cwd=source_dir,
            stdout_line_callback=CheckStyle(params).print_log,
            stderr_line_callback=CheckStyle(params).print_log,
            stderr_filepath=tmp_log,
        )
        spc.wait()
        err_issue = self.error_handle(params, spc, file_path)
        if err_issue:
            issues.append(err_issue)

        if not os.path.exists(tmp_tool_output) or os.stat(tmp_tool_output).st_size == 0:
            LogPrinter.info("result is empty ")
            return issues

        # 整理issue 通过输入规则列表进行筛除
        checkstyle_output_file = open(tmp_tool_output, "r", encoding="UTF-8")
        line = checkstyle_output_file.readline()
        while line:
            issue = self.get_issue(line)
            if issue and self.issue_filter(issue):
                issue["path"] = os.path.relpath(issue["path"], source_dir)
                issues.append(issue)
            line = checkstyle_output_file.readline()
        checkstyle_output_file.close()  # 关闭文件
        try:
            os.remove(tmp_tool_output)
        except:
            LogPrinter.info("删除文件 %s 失败" % tmp_tool_output)
        return issues

    def error_handle(self, params, spc, file_path):
        """
        异常处理
        :param params:
        :param spc:
        :return:
        """
        source_dir = params["source_dir"]
        if spc.returncode == 0:
            return
        spc_err = spc.get_stderr()
        if not spc_err:
            log = ""
        else:
            log = spc_err.read()
            spc_err.close()
        if (
            log.find(
                "com.puppycrawl.tools.checkstyle.api.CheckstyleException: " "Exception was thrown while processing"
            )
            != -1
        ):
            msg = "CheckStyle工具解析异常，请确保Java文件语法正确"
            line_num = 1
            for line in log.split("\n"):
                if line.find("Caused by: line ") != -1:
                    line_num = self.format_parse_error(line)
                    msg += line
            return {
                "rule": "JavaParseError",
                "path": os.path.relpath(file_path, source_dir),
                "line": line_num,
                "column": 1,
                "msg": msg,
            }
        elif (
            log.find(
                "com.puppycrawl.tools.checkstyle.api.CheckstyleException: "
                "NoViableAltException occurred during the analysis of file"
            )
            != -1
        ):
            raise AnalyzeTaskError("CheckStyle工具解析异常，请排查log确保对应文件语法是否正确。")

        elif (
            log.find("com.puppycrawl.tools.checkstyle.api.CheckstyleException: " "cannot initialize module TreeWalker")
            != -1
        ):
            raise AnalyzeTaskError("CheckStyle工具执行异常，配置文件有误，可能是规则名称不匹配。")
        elif log.find("com.puppycrawl.tools.checkstyle.api.CheckstyleException:") != -1:
            raise AnalyzeTaskError("CheckStyle工具执行异常。")
        return None

    def get_issue(self, line):
        """
        对checkstyle工具的输出文本进行逐行解析
        :param line:
        :return:
        """
        if not line.startswith("["):
            return None
        rule_name_start = line.rfind("[")
        rule_name_end = line.rfind("]")
        if rule_name_start > rule_name_end:
            LogPrinter.error("parser error: %s" % line)
        rule_name = line[rule_name_start + 1 : rule_name_end]

        # 适配windows的路径C:\
        if sys.platform == "win32":
            tmp = ":".join(line.split(":")[:2])
            path_end = len(tmp)
            file_path = tmp.split()[1]
        else:
            path_end = line.find(":", 0, rule_name_start)
            file_path = " ".join(line[:path_end].split()[1:])

        line_end = line.find(":", path_end + 1, rule_name_start)
        line_num = line[path_end + 1 : line_end]

        column_end = line.find(":", line_end + 1, rule_name_start)
        column_num = line[line_end + 1 : column_end]
        if not column_num.isdigit():
            column_end = line_end
            column_num = 0

        issue_msg = line[column_end + 1 : rule_name_start].strip()

        return {
            "path": file_path,
            "rule": rule_name,
            "line": int(line_num),
            "column": int(column_num),
            "msg": issue_msg,
        }

    def issue_filter(self, issue):
        rule_set = {"FileLength", "FileTabCharacter"}
        if not issue:
            return False
        # 过滤1：如果FileLength上报的非java文件则过滤掉
        if issue["rule"] in rule_set and not issue["path"].endswith(".java"):
            return False
        return True

    def format_parse_error(self, line):
        """
        用于解析checkstyle语法解析报错，并提issues

        """
        pattern = "line (.*?):"
        regex = re.compile(pattern)
        line = re.findall(regex, line)
        if line:
            try:
                int(line[0])
            except:
                return 1
            return int(line[0])
        else:
            return 1


class ThreadRunner(object):
    # 多线程执行checkstyle 类
    def __init__(self, scan_cmd, source_dir, params):
        self.scan_cmd = scan_cmd
        self.source_dir = source_dir
        self.issues = []
        self.params = params
        self.mutex = threading.Lock()  # 线程锁

    def __scan_file_callback_(self, file_path):
        file_result = CheckStyleRunner().run_checkstyle_on_file(file_path, self.scan_cmd, self.source_dir, self.params)
        self.mutex.acquire()  # 上锁
        self.issues.extend(file_result)
        self.mutex.release()  # 解锁

    def run(self, toscans):
        # 多线程执行类
        callback_queue = CallbackQueue(min_threads=20, max_threads=1000)
        LogPrinter.info("toscans : %s" % toscans)
        for path in toscans:
            LogPrinter.info("path: %s" % path)
            callback_queue.append(self.__scan_file_callback_, path)
        callback_queue.wait_for_all_callbacks_to_be_execute_and_destroy()
        return self.issues


tool = CheckStyle

if __name__ == "__main__":
    pass
