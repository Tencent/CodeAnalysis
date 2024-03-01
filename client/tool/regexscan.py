# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

""" regexscan 正则匹配扫描工具
"""

import os
import io
import re

from task.codelintmodel import CodeLintModel
from task.scmmgr import SCMMgr
from util.pathlib import PathMgr
from util.pathfilter import WildcardPathFilter
from util.textutil import CODE_EXT, CommentsManager, CodecClient
from task.basic.datahandler.filter import REVISION_FILTER, PATH_FILTER
from util.configlib import ConfigReader
from util.pathfilter import FilterPathUtil
from util.logutil import LogPrinter

logger = LogPrinter


class RegexScanner(object):
    """使用正则匹配检查代码的扫描器
    """
    @staticmethod
    def scan_line(line, rules):
        """ 对单行代码执行正则匹配扫描
        """
        issues = []
        for name, params in rules.items():
            msg_template = params['msg']
            pattern = params['reg_pattern']
            match = pattern.search(line)
            if match:
                # msg_template里不包含%s，则不需要匹配，直接显示信息
                if '%s' not in msg_template:
                    message = msg_template
                else:
                    cap_text_list = match.groups()
                    try:
                        message = msg_template % cap_text_list
                    except:
                        cap_text_list = match.group()
                        try:
                            message = msg_template % cap_text_list
                        except:
                            message = u"Irregular codes found: %s" % cap_text_list
                issue = {
                    'rule': name,
                    'msg': message,
                    'column': 1
                }
                issues.append(issue)
        return issues

    @staticmethod
    def scan_file(source_dir, file_path, rules):
        """对单个代码文件进行正则匹配
        :param source_dir: 项目代码根目录
        :param file_path: 单个代码文件路径
        :param rules: {
            rule_name: {
                'reg_pattern': reg_pattern,
                'exclude': exclude_paths,
                'include': include_paths,
                'msg': msg,
                'ignore_comment': True|False
            }
        }
        :return: [{
                    "path":文件相对路径,
                    "line":行号,
                    "column":列号,
                    "msg":提示信息,
                    "rule":规则名
                  },
                  ...
                ]
        """
        source_dir = source_dir.replace(os.sep, '/').rstrip('/')
        file_path = file_path.replace(os.sep, '/')
        relpos = len(source_dir) + 1
        relative_path = file_path[relpos:]
        rules_exclude_comment = {}
        rules_include_comment = {}

        for rule_name, params in rules.items():
            filter_util = WildcardPathFilter(path_include=params['include'], path_exclude=params['exclude'])
            if filter_util.should_filter_path(relative_path):
                continue
            if params['ignore_comment']:
                rules_exclude_comment[rule_name] = params
            else:
                rules_include_comment[rule_name] = params
        if not rules_exclude_comment and not rules_include_comment:
            return []
        results = []
        if not os.path.isfile(file_path):
            logger.debug("%s is not a file,filter!" % file_path)
            return []
        with io.open(file_path, 'rb') as fp:
            file_text = CodecClient().decode(fp.read())
            if rules_exclude_comment:
                code_nocomment = CommentsManager(file_path, file_text).remove_comments()
                issues = RegexScanner.scan_file_text(relative_path, code_nocomment, rules_exclude_comment)
                results.extend(issues)
            if rules_include_comment:
                issues = RegexScanner.scan_file_text(relative_path, file_text, rules_include_comment)
                results.extend(issues)
        return results

    @staticmethod
    def scan_file_text(rel_path, file_text, rules):
        """
        对单个文件内容逐行做正则匹配
        :param rel_path:
        :param file_text:
        :param rules:
        :return:
        """
        file_result = []
        for lineno, line in enumerate(file_text.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            line_result = RegexScanner.scan_line(line, rules)
            if line_result:
                for issue in line_result:
                    issue['path'] = rel_path
                    issue['line'] = lineno
                    file_result.append(issue)
        return file_result


class RegexScan(CodeLintModel):
    def __format_rules(self, rule_list):
        """把[{'name':str, 'params':str}...]格式的rule_list转换为 rule_name-value的格式，并把reg_exp编译好
        :param rule_list: [{'name':str, 'params':str}...]
        :return: {
            rule_name: {
                'reg_pattern': reg_pattern,
                'exclude': exclude_paths,
                'include': include_paths,
                'msg': msg,
                'ignore_comment': True|False
            }
        }
        """
        rules = {}
        for rule in rule_list:
            rule_name = rule['name']
            if not rule.get('params'):
                logger.error(f"{rule_name} rule parameter is empty, check for existing rules.")
                continue
            if "[regexcheck]" in rule['params']:
                rule_params = rule['params']
            else:
                rule_params = "[regexcheck]\r\n" + rule['params']
            rule_params_dict = ConfigReader(cfg_string=rule_params).read('regexcheck')

            reg_exp = rule_params_dict.get('regex', '')
            if not reg_exp:
                logger.error(f"{rule_name} rule parameter is wrong, not fill in the regular expression, skip this rule.")
                continue
            reg_pattern = re.compile(reg_exp)
            exclude_paths = rule_params_dict.get('exclude', '')
            exclude_paths = [p.strip() for p in exclude_paths.split(';') if p.strip()] if exclude_paths else []
            include_paths = rule_params_dict.get('include', '')
            include_paths = [p.strip() for p in include_paths.split(';') if p.strip()] if include_paths else []
            # 大小写不敏感,可以支持True|true|False|false等
            ignore_comment = True if rule_params_dict.get('ignore_comment', 'False').lower() == 'true' else False
            msg = rule_params_dict.get('msg', "Irregular codes found: %s")
            rules[rule_name] = {
                'reg_pattern': reg_pattern,
                'exclude': exclude_paths,
                'include': include_paths,
                'msg': msg,
                'ignore_comment': ignore_comment
            }
        return rules

    def analyze(self, params):
        """执行扫描任务

        :param params: 需包含下面键值：
           'rules'： lint扫描的规则列表
           'incr_scan' : 是否增量扫描

        :return: return a :py:class:`IssueResponse`
        """
        source_dir = params['source_dir']
        incr_scan = params['incr_scan']
        rules = self.__format_rules(params['rule_list'])

        if incr_scan:
            diffs = SCMMgr(params).get_scm_diff()
            toscans = [os.path.join(source_dir, diff.path) for diff in diffs if diff.state != 'del']
        else:
            toscans = PathMgr().get_dir_files(source_dir)

        # filter include and exclude path
        relpos = len(source_dir) + 1
        toscans = FilterPathUtil(params).get_include_files(toscans, relpos)

        if not toscans:
            logger.debug("To-be-scanned files is empty ")
            return []

        logger.debug("files to scan: %d" % len(toscans))

        # 执行扫描工具
        issues = []
        for file_path in toscans:
            file_issues = RegexScanner.scan_file(source_dir, file_path, rules)
            if file_issues:
                issues.extend(file_issues)

        if not issues:
            logger.info("result is empty.")

        logger.debug(issues)
        return issues

    def set_filter_type_list(self):
        """
        通过覆盖该函数来选择过滤类型
        目前存在的过滤类型有：
        1. NO_FILTER  不需要过滤
        2. DIFF_FILTER 将非修改的代码文件进行过滤
        3. REVISION_FILTER 通过起始版本号进行过滤
        4. PATH_FILTER 通过用户设置的黑白名单进行过滤
        过滤选项可以多选，但NO_FILTER为阻止使用过滤器
        :return:
        """
        # 已经过滤文件和diff增量,不需要重复过滤,只需要根据revision过滤
        return [REVISION_FILTER, PATH_FILTER]


tool = RegexScan

if __name__ == '__main__':
    pass
