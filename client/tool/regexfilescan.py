
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================
# -*- encoding: utf8 -*-
""" 正则匹配文件路径(支持自定义规则)
"""

import os
import re

from task.basic.datahandler.blamer import FILE_LAST_CHANGE_BLAME
from task.codelintmodel import CodeLintModel
from task.scmmgr import SCMMgr
from util.pathlib import PathMgr
from util.pathfilter import WildcardPathFilter
from task.basic.datahandler.filter import REVISION_FILTER
from util.configlib import ConfigReader
from util.pathfilter import FilterPathUtil
from util.logutil import LogPrinter

logger = LogPrinter


class RegexScanner(object):
    """使用正则匹配检查代码的分析器
    """
    @staticmethod
    def scan_file_path(rel_path, rules):
        """ 对文件相对路径执行正则匹配分析
        """
        rel_path = rel_path.replace(os.sep, '/')
        issues = []
        for name, params in rules.items():
            msg_template = params['msg']
            pattern = params['reg_pattern']
            match = pattern.search(rel_path)
            if match:
                # msg_template里不包含%s，则不需要匹配，直接显示信息
                if '%s' not in msg_template:
                    message = msg_template
                else:
                    cap_text_list = match.groups()
                    try:
                        message = msg_template % cap_text_list
                    except:
                        # 如果捕获的分组和msg不匹配（分组为空;或msg中的%s数和分组数不相等），则捕获匹配的整个字符串
                        cap_text_list = match.group()
                        # 再次尝试与msg匹配,如果还是不匹配,则使用默认提示信息进行匹配
                        try:
                            message = msg_template % cap_text_list
                        except:
                            message = u"发现不规范文件: %s" % cap_text_list
                issue = {
                    'path': rel_path,
                    'rule': name,
                    'msg': message,
                    'line': 0,
                    'column': 0
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
                'msg': msg
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
        rules_check_path = {}

        for rule_name, params in rules.items():
            # 根据include和exclude判断path是否需要过滤
            filter_util = WildcardPathFilter(path_include=params['include'], path_exclude=params['exclude'])
            if filter_util.should_filter_path(relative_path):
                continue
            rules_check_path[rule_name] = params

        if not rules_check_path:
            return []

        results = []
        # 对文件路径进行正则匹配
        if rules_check_path:
            issues = RegexScanner.scan_file_path(relative_path, rules_check_path)
            results.extend(issues)

        return results


class RegexFileScan(CodeLintModel):
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
                logger.error(f"{rule_name}规则参数为空,跳过该规则.")
                continue
            if "[regexcheck]" in rule['params']:
                rule_params = rule['params']
            else:
                rule_params = "[regexcheck]\r\n" + rule['params']
            rule_params_dict = ConfigReader(cfg_string=rule_params).read('regexcheck')

            reg_exp = rule_params_dict.get('regex', '')
            if not reg_exp:
                logger.error(f"{rule_name}规则参数有误,未填写正则表达式,跳过该规则.")
                continue
            reg_pattern = re.compile(reg_exp)
            exclude_paths = rule_params_dict.get('exclude', '')
            exclude_paths = [p.strip() for p in exclude_paths.split(';') if p.strip()] if exclude_paths else []
            include_paths = rule_params_dict.get('include', '')
            include_paths = [p.strip() for p in include_paths.split(';') if p.strip()] if include_paths else []
            # 大小写不敏感,可以支持True|true|False|false等
            msg = rule_params_dict.get('msg', "发现不规范文件: %s")
            rules[rule_name] = {
                'reg_pattern': reg_pattern,
                'exclude': exclude_paths,
                'include': include_paths,
                'msg': msg
            }
        return rules

    def analyze(self, params):
        """执行分析任务

        :param params: 需包含下面键值：
           'rules'： lint分析的规则列表
           'incr_scan' : 是否增量分析

        :return: return a :py:class:`IssueResponse`
        """
        source_dir = params['source_dir']
        incr_scan = params['incr_scan']
        rules = self.__format_rules(params['rule_list'])

        logger.info('获取需要分析的文件')

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

        # 执行分析工具
        logger.debug('逐个文件执行正则匹配')

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
        '''
        通过覆盖该函数来选择过滤类型
        目前存在的过滤类型有：
        1. NO_FILTER  不需要过滤
        2. DIFF_FILTER 将非修改的代码文件进行过滤
        3. REVISION_FILTER 通过起始版本号进行过滤
        4. PATH_FILTER 通过用户设置的黑白名单进行过滤
        过滤选项可以多选，但NO_FILTER为阻止使用过滤器
        :return:
        '''
        return [REVISION_FILTER]

    def set_blame_type(self):
        '''
        通过覆盖该函数来选择blame类型
        目前存在blame类型有：
        1. NO_BLAME 不需要blame
        2. NORMAL_BLAME 常规blame
        3. FILE_LAST_CHANGE_BLAME 将文件最后一个修改人作为责任人
        由于blame类型互斥，所以既能返回一个值
        :return:
        '''
        return FILE_LAST_CHANGE_BLAME


tool = RegexFileScan

if __name__ == '__main__':
    pass
