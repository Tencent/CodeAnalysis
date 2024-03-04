# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
findbugs 扫描任务
"""

import os
import zipfile

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from task.codelintmodel import CodeLintModel
from util.subprocc import SubProcController
from tool.util.compile import BasicCompile
from util.exceptions import CompileTaskError
from util.logutil import LogPrinter


class RulesToVisitors(object):
    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        self.tool_home = f"{tool_name.upper()}_HOME"

    # 获取检测类到检测模式的映射
    def class_to_pattern(self, tool_xml_data, visitors_to_pattern=None):
        raw_material = ET.fromstring(tool_xml_data)
        if not visitors_to_pattern:
            visitors_to_pattern = {}
        for detector in raw_material.iter("Detector"):
            detector_name = detector.attrib.get("class")
            report_patterns = detector.attrib.get("reports")
            acutal_visitor = detector_name[detector_name.rfind(".") + 1 :]
            if report_patterns:
                visitors_to_pattern[acutal_visitor] = report_patterns.split(",")
        return visitors_to_pattern

    def search_File(self, path, _format):
        file_list = []
        for root, _, files in os.walk(path):
            for fp in files:
                if fp.endswith(_format):
                    file_list.append(os.path.join(root, fp))
        return file_list

    def get_needed_visitors(self, pattern=None):
        """
        通过缺陷模式匹配对应的规则列表
        :param pattern:缺陷模式名
        :return:匹配的规则列表
        """
        if not pattern:
            # 全量规则扫描
            return None

        tool_jar = os.path.join(os.environ[self.tool_home], "lib", f"{self.tool_name}.jar")
        zfile = zipfile.ZipFile(tool_jar, "r")
        tool_xml_data = zfile.read("findbugs.xml")
        whole_patterns = self.class_to_pattern(tool_xml_data)

        # 获取自定义规则的配置信息
        plugin_list = self.search_File(os.path.join(os.environ[self.tool_home], "plugin"), ".jar")
        for plugin in plugin_list:
            plugin_file = zipfile.ZipFile(plugin, "r")
            plugin_tool_xml_data = plugin_file.read("findbugs.xml")
            whole_patterns = self.class_to_pattern(plugin_tool_xml_data, whole_patterns)

        visitors = []
        for key, value in whole_patterns.items():
            if list(set(value) & set(pattern)):
                visitors.append(key)
        return visitors


class Findbugs(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.sensitive_word_maps = {
            "Findbugs": "Tool",
            "findbugs": "Tool"
        }

    def compile(self, params):
        """
        编译执行函数
        :param params:
        :return:
        """
        LogPrinter.info("Tool compile start.")
        build_cmd = params.get("build_cmd")
        if not build_cmd:
            raise CompileTaskError("编译语言项目执行静态分析需要输入编译命令，请填入编译命令后重试！")
        BasicCompile(params, sensitive=self.sensitive, sensitive_word_maps=self.sensitive_word_maps,
                     build_cmd=BasicCompile.generate_shell_file(build_cmd)).compile()
        LogPrinter.info("Tool compile done.")
        return True

    def analyze(self, params):

        source_dir = params["source_dir"]
        enabled_rules = params["rules"]
        error_output = os.path.join(os.path.curdir, "findbugs_result.xml")

        # analyze step
        tool_name = "findbugs"
        visitors = RulesToVisitors(tool_name).get_needed_visitors(enabled_rules)
        # findbugs的兼容性：这里需要使用原生的java -jar xx才能适配win|linux下的按指定检测器检测(使用wrapper脚本会有问题)
        scan_cmd = [
            "java",
            "-jar",
            os.path.join(os.environ["FINDBUGS_HOME"], "lib", "findbugs.jar"),
            "-textui",
            "-low",
            "-exitcode",
            "-nested:false",
            "-xml:withMessages",
        ]
        if visitors:
            scan_cmd.append("-visitors")
            scan_cmd.append(",".join(visitors))
        scan_cmd.extend(["-output", error_output, source_dir])
        SubProcController(scan_cmd).wait()

        # format step
        ctf = ClassToFilename(source_dir)
        items = Findbugs.data_handle(error_output, enabled_rules, ctf)
        return items

    @staticmethod
    def data_handle(error_output, enabled_rules, ctf):
        """结果处理
        """
        if not os.path.exists(error_output) or os.stat(error_output).st_size == 0:
            LogPrinter.info("result is empty")
            return []
        raw_warning = ET.ElementTree(file=error_output)
        items = []
        for bug in raw_warning.iter(tag="BugInstance"):
            path = None
            msg = None
            line = None
            FILE_NOT_FOUND = False
            rule = bug.attrib.get("type")
            # 通过缺陷模式反推出的检测器所对应的缺陷模式集合是指定缺陷模式的父集(即规则名与缺陷模式是1对多的关系)，故这里需要过滤
            if enabled_rules and rule not in enabled_rules:
                continue
            for node in bug:
                if node.tag == "SourceLine":
                    line = node.attrib.get("start")
                    path = ctf.get_file_path_from_sourcepath(node.attrib.get("sourcepath"))
                    if not path:
                        path = ctf.get_file_path_from_classname(node.attrib.get("classname"))
                    if not path or not line:
                        FILE_NOT_FOUND = True
                        break
                    line = int(line)
                elif node.tag == "LongMessage":
                    msg = node.text
            if FILE_NOT_FOUND:
                continue
            items.append({"path": path, "rule": rule, "msg": msg, "line": line})
        return items
        


class ClassToFilename(object):
    def __init__(self, scan_dir):
        """

        :param scan_dir:
        """
        self._scan_dir = scan_dir
        self._source_files = self._get_java_source_files()

    def _get_specified_ext_files(self, ext):
        ret = []
        for dirpath, _, filenames in os.walk(self._scan_dir):
            for f in filenames:
                if f.endswith(ext):
                    ret.append(os.path.relpath(os.path.join(dirpath, f), self._scan_dir).replace("\\", "/"))
        return ret

    def _get_java_source_files(self):
        return self._get_specified_ext_files(".java")

    def get_file_path_from_classname(self, classname):
        """
        当文件为None，或者class文件对应的java文件不在文件列表中，则返回None
        :param classname:
        :return:
        """
        if not classname:
            return None
        if classname.find("$") > -1:
            # 取class主类名
            classname = classname.split("$")[0]
        else:
            classname = classname.replace(".class", "")
        sourcepath = classname.replace(".", "/") + ".java"
        return self.get_file_path_from_sourcepath(sourcepath)

    def get_file_path_from_sourcepath(self, sourcepath):
        """
        当文件为None，或者java文件不在文件列表中，则返回None
        :param sourcepath:
        :return:
        """
        if not sourcepath:
            return None
        sourcepath = sourcepath.replace("\\", "/")
        for source_file in self._source_files:
            if source_file.endswith(sourcepath):
                return source_file
        return None


tool = Findbugs

if __name__ == "__main__":
    pass
