# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
忽略格式：

（以C++代码为例，以单行注释符号'//'开头，其他语言按照各自的单行注释符号开头）
// NOCA:rule1(ignore reason),rule2(ignore reason),...

格式说明:
● 注释位置：可以放在问题代码行的行末，也可以放在问题代码行的前一行。文件类型的规则，问题会报出在首行，可以在文件任一行添加注释，建议放在前几行。
● NOCA：忽略标记，后面使用英文冒号与规则名分隔。
● 规则名：规则名，多个规则用英文逗号分隔。
● 忽略原因：放在英文括号中，跟在规则名后面，用来说明忽略该规则问题的原因。

举例
（1）忽略单个规则
// NOCA:rule1(工具误报:此处已经是驼峰了)

（2）忽略多个规则
// NOCA:rule2(设计如此:为了更高的性能),rule3(其他:老代码先不改)

====================================================================================
旧版格式（保留该逻辑做兼容）：
如果issue所在的代码行的上一行有注释说明该行的问题可以忽略，则在issue中标注为忽略状态
注释行demo:
            # CodeAnalysisIgnore
            # CodeAnalysisIgnore-pylint
            # CodeAnalysisIgnore-pylint:unbalanced-tuple-unpacking
====================================================================================

"""

import os
import re

from task.basic.datahandler.handlerbase import HandlerBase
from util.exceptions import DataHandleTaskError
from util.scanlang.callback_queue import CallbackQueue
from util.textutil import CodecClient, CommentsManager, StringMgr
from util.logutil import LogPrinter

# ignore类型

NO_ISSUE_IGNORE = 0
CODELINT_ISSUE_IGNORE = 1

# 如果有注释标记忽略，设置issue["resolution"]=8
COMMENTIGNORE = 8


class IgnoreCheck(object):
    """
    新版忽略格式：
    // NOCA:rule1(ignore reason),rule2(ignore reason),...
    正则表达式为
        规则名：[\w\.\-]+
        (ignore reason)：\([^\)]+\)
    """

    def __init__(self):
        self._ignore_prefix = "NOCA"
        each_rule_pattern = r"([\w\.\-/]+)\s*\(([^\)]+)\)"
        self._noca_pattern = re.compile(r"\bNOCA\s*:\s*" + each_rule_pattern + r"(,\s*" + each_rule_pattern + r")*")
        self._rule_pattern = re.compile(each_rule_pattern)

    def scan_file(self, source_dir, fileissue):
        """
        扫描单个文件，根据注释忽略issue
        :param source_dir:
        :param fileissue:
        :return:
        """
        issues = fileissue.get("issues")
        if not issues:
            return

        path = fileissue.get("path")
        full_path = os.path.join(source_dir, path)
        with open(full_path, "rb") as rf:
            # 读取文件内容并解码为字符串
            file_text = CodecClient().decode(rf.read())
            file_lines = file_text.splitlines()
            file_len = len(file_lines)

        if not file_len:  # 空文件，跳过
            return

        # 收集需要解析的代码行
        check_lines = set()
        # 收集文件类型的规则名
        file_type_rules = set()
        for issue in issues:
            line_no = int(issue["line"])
            if line_no == 0:
                file_type_rules.add(issue["rule"])
            else:
                # 将当前行加入到检查范围
                check_lines.add(line_no)
                # 如果不是首行，将上一行也加入到检查范围
                if line_no > 1:
                    check_lines.add(line_no - 1)
        # 只要存在一个文件类型的规则issue，所有行都需要解析注释
        if file_type_rules:
            check_lines = set(range(1, file_len + 1))

        # LogPrinter.info(f">> {path}, check_lines: {check_lines}")

        ignore_rules_dict = {}
        for line_no in check_lines:
            line_ignore_rules = self.__get_line_ignore_rules(
                full_path, file_lines[line_no - 1], line_no, file_type_rules
            )
            ignore_rules_dict.update(line_ignore_rules)

        for issue in issues:
            key = self.__get_key_name(issue["rule"], issue["line"], file_type_rules)
            ignore_reason = ignore_rules_dict.get(key)
            if ignore_reason:
                issue["resolution"] = COMMENTIGNORE
                issue["ignore_reason"] = ignore_reason

    def __get_line_ignore_rules(self, file_path, line_text, line_no, file_type_rules):
        """
        从单行代码文本中提取需要忽略的规则信息
        :param file_path:
        :param line_text:
        :param line_no:
        :return:
        """
        # 当前行不包含关键词，返回
        if self._ignore_prefix not in line_text:
            return {}
        comment_mgr = CommentsManager(file_path, line_text)
        comment_lines = comment_mgr.get_comments()
        # 当前行不包含注释，返回
        if not comment_lines:
            return {}
        comment = comment_lines[0]
        # 注释不包含关键词，返回
        if self._ignore_prefix not in comment:
            return {}
        # 当前行包含代码，则忽略的是当前行；否则，忽略的是下一行
        if self.__line_has_code(file_path, line_text):
            ignore_line_no = line_no
        else:
            ignore_line_no = line_no + 1
        ignore_rules = self.__match_ignore_rules(comment, ignore_line_no, file_type_rules)
        return ignore_rules

    def __line_has_code(self, file_path, line_text):
        """判断当前行是否包含代码"""
        code_text = CommentsManager(file_path, line_text).remove_comments()
        code_text = code_text.strip()
        if code_text:
            return True
        else:
            return False

    def __get_key_name(self, rule_name, line_no, file_type_rules):
        if rule_name in file_type_rules:
            return rule_name
        else:
            return f"{rule_name}#{line_no}"

    def __match_ignore_rules(self, comment, ignore_line_no, file_type_rules):
        """
        从注释中提取忽略的规则信息
        :param comment:
        :param ignore_line_no:
        :return: {"rule_name#ignore_line_no": "ignore reason", ...}
        """
        ignore_rules = {}
        noca_match = self._noca_pattern.search(comment)
        # LogPrinter.info(f">> noca_match: {noca_match}")
        if noca_match:
            noca_text = noca_match.group()
            # LogPrinter.info(f">> noca_text: {noca_text}")
            rule_match_list = self._rule_pattern.findall(noca_text)
            # LogPrinter.info(f">> rule_match_list: {rule_match_list}")
            for rule_match in rule_match_list:
                rule_name, rule_reason = rule_match[0], rule_match[1]
                key = self.__get_key_name(rule_name, ignore_line_no, file_type_rules)
                ignore_rules[key] = rule_reason
        return ignore_rules


class IssueIgnore(HandlerBase):
    """
    问题忽略处理类
    """

    def __init__(self, handle_type):

        super().__init__(handle_type)
        self._tool_name = None

    def run(self, params):
        self._tool_name = params["tool_name"]  # params的tool_name字段，是TaskMg模块初始化时存进去的
        if self.handle_type == NO_ISSUE_IGNORE:
            return params
        elif self.handle_type == CODELINT_ISSUE_IGNORE:
            return self._lint_ignore(params)
        else:
            raise DataHandleTaskError("issue ignore type is not exist: %s" % self.handle_type)

    def _lint_ignore(self, params):
        LogPrinter.info("start: igonre issues according to code comments.")
        fileissues = params["result"]
        source_dir = params["source_dir"]
        self._common_ignore(source_dir, fileissues)
        LogPrinter.info("finished: igonre issues according to code comments.")

    def _common_ignore(self, source_dir, fileissues):
        callback_queue = CallbackQueue(min_threads=20, max_threads=1000)
        ignore_check = IgnoreCheck()
        old_ignore_check = OldIgnoreCheck(self._tool_name)
        for fileissue in fileissues:
            callback_queue.append(self.__scan_file_callback__, source_dir, fileissue, ignore_check, old_ignore_check)
        callback_queue.wait_for_all_callbacks_to_be_execute_and_destroy()

    def __scan_file_callback__(self, source_dir, fileissue, ignore_check, old_ignore_check):
        """
        单个文件问题集合处理
        :param source_dir:
        :param fileissue:
        :return:
        """
        # 新版过滤格式
        ignore_check.scan_file(source_dir, fileissue)
        # 旧版过滤格式(兼容)
        old_ignore_check.scan_file(source_dir, fileissue)

    @staticmethod
    def get_tool_handle_type_name():
        return "set_issue_ignore_type"


class OldIgnoreCheck(object):
    """
    旧版注释忽略格式（兼容）
    """

    def __init__(self, tool_name):
        self._tool_name = tool_name

    def scan_file(self, source_dir, fileissue):
        issues = fileissue.get("issues")
        if issues:
            path = fileissue.get("path")
            full_path = os.path.join(source_dir, path)
            ignore_comments_dict = self._get_ignore_comments(full_path)
            if ignore_comments_dict:
                for issue in issues:
                    line_no_str = str(issue["line"])
                    # 判断是否满足该代码行的忽略规则
                    if self._line_should_be_ignored(line_no_str, issue, ignore_comments_dict):
                        issue["resolution"] = COMMENTIGNORE
                    # 判断是否满足整个文件的忽略规则
                    elif self._line_should_be_ignored("ALL_LINES", issue, ignore_comments_dict):
                        issue["resolution"] = COMMENTIGNORE

    def _line_should_be_ignored(self, line_no_str, issue, ignore_comments_dict):
        """
        判断某一行代码是否需要被忽略
        :param line_no_str:
        :param ignore_comments_dict:
        :return:
        """
        if line_no_str in ignore_comments_dict:
            tool_dict = ignore_comments_dict[line_no_str]
            if "ALL_TOOLS" in tool_dict:
                return True
            elif self._tool_name in tool_dict:
                rule_list = tool_dict[self._tool_name]
                if "ALL_RULES" in rule_list or issue["rule"] in rule_list:
                    return True
        return False

    def _get_tool_name(self, tool_str, line_ignore_prefix, file_ignore_prefix):
        """
        解析工具名字符串(即冒号前面的部分),提取工具名
        :param tool_str:
        :param line_ignore_prefix:
        :param file_ignore_prefix:
        :return:
        """
        tool_name = None

        # CodeAnalysisIgnore 或 CodeAnalysisIgnore-File
        if tool_str in [line_ignore_prefix, file_ignore_prefix]:
            tool_name = "ALL_TOOLS"
        # CodeAnalysisIgnore-File-ToolName
        elif tool_str.startswith(f"{file_ignore_prefix}-"):
            tool_name = tool_str[len(f"{file_ignore_prefix}-") :]
        # CodeAnalysisIgnore-ToolName
        elif tool_str.startswith(f"{line_ignore_prefix}-"):
            tool_name = tool_str[len(f"{line_ignore_prefix}-") :]

        if not tool_name:
            LogPrinter.error(f"wrong ignore comment format: {tool_str}")

        return tool_name

    def _analyze_ignore_word(self, line_no, ignore_word, line_ignore_prefix, file_ignore_prefix):
        """
        解析忽略字符串
        :param line_no:
        :param ignore_word:
        :param line_ignore_prefix:
        :param file_ignore_prefix:
        :return:
        """
        # 判断生效范围（整个文件或单行代码）
        if ignore_word.startswith(file_ignore_prefix):
            code_line_num = "ALL_LINES"
        else:
            code_line_num = str(line_no + 1)  # 对下一行代码生效
        # 解析工具名和规则名
        if ":" in ignore_word:
            tool_str, rule_str = ignore_word.split(":", maxsplit=1)
            rule_list = StringMgr.str_to_list(rule_str)
            if not rule_list:
                rule_list = ["ALL_RULES"]
        else:
            tool_str = ignore_word
            rule_list = ["ALL_RULES"]

        tool_name = self._get_tool_name(tool_str, line_ignore_prefix, file_ignore_prefix)
        return code_line_num, tool_name, rule_list

    def _get_ignore_comments(self, file_path):
        """
        获取单个文件中所有的忽略注释信息
        注释demo:
            # CodeAnalysisIgnore
            # CodeAnalysisIgnore-pylint
            # CodeAnalysisIgnore-pylint:unused-import
            # CodeAnalysisIgnore-File-pylint:unused-import
        :param file_path:
        :param issues:
        :return:  {"issue_line_no":
                      {
                          "tool_name": [rule1, rule2, ...]
                      }, ...
                  }
                  issue_line_no,tool_name,rule 如果为ALL_xxx，表示所有行、所有工具、某工具的所有规则
        """
        try:
            line_ignore_prefix = "CodeAnalysisIgnore"
            file_ignore_prefix = "CodeAnalysisIgnore-File"
            ignore_comments_dict = {}
            with open(file_path, "rb") as rf:
                # 读取文件内容并解码为字符串
                file_text = CodecClient().decode(rf.read())
                for line_no, line_text in enumerate(file_text.splitlines(), start=1):
                    if line_ignore_prefix in line_text:
                        if CommentsManager(file_path, line_text).is_comment_line():
                            word_list = line_text.split()
                            # 收集忽略字符串
                            ignore_word_list = [word for word in word_list if word.startswith(line_ignore_prefix)]
                            # 逐个处理忽略字符串
                            for ignore_word in ignore_word_list:
                                code_line_num, tool_name, rule_list = self._analyze_ignore_word(
                                    line_no, ignore_word, line_ignore_prefix, file_ignore_prefix
                                )
                                if code_line_num and tool_name and rule_list:
                                    # 存到ignore_comments_dict字典中
                                    if code_line_num in ignore_comments_dict:
                                        if tool_name in ignore_comments_dict[code_line_num]:
                                            ignore_comments_dict[code_line_num][tool_name].extend(rule_list)
                                        else:
                                            ignore_comments_dict[code_line_num][tool_name] = rule_list
                                    else:
                                        ignore_comments_dict[code_line_num] = {tool_name: rule_list}
            return ignore_comments_dict
        except Exception as err:
            LogPrinter.exception("get file(%s) ignore comments error: %s", (file_path, str(err)))
            return {}
