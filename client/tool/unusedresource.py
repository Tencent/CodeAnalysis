# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

""" UnusedResource 扫描项目中未使用的资源文件
"""

import os
import re
import configparser

from task.scmmgr import SCMMgr
from util.textutil import CodecClient, CommentsManager
from task.codelintmodel import CodeLintModel
from task.basic.datahandler.filter import REVISION_FILTER, PATH_FILTER
from task.basic.datahandler.blamer import FILE_LAST_CHANGE_BLAME
from util.pathfilter import FilterPathUtil
from util.logutil import LogPrinter

logger = LogPrinter


class UnusedResource(CodeLintModel):
    def __format_rules(self, rule_list):
        """把[{'name':str, 'params':str}...]格式的rule_list转换为 rule_name-value的格式
        :param rule_list: [{'name':str, 'params':str}...]
        :return: {
            rule_name: {
                'res_suffix': res_exts,
                'code_suffix': code_exts
            }
        }
        """
        rules = {}
        for rule in rule_list:
            rule_name = rule['name']
            rule_params = "[UnusedResource]\r\n" + rule['params']
            rule_params_dict = {}
            cfg = configparser.RawConfigParser()
            cfg.read_string(rule_params)

            for key, value in cfg.items('UnusedResource'):
                rule_params_dict[key] = value

            res_exts = rule_params_dict.get('res_suffix', '')
            res_exts = [p.strip() for p in res_exts.split(';') if p.strip()] if res_exts else []
            res_exts = tuple(set(res_exts))  # 去重并转换成tuple
            code_exts = rule_params_dict.get('code_suffix', '')
            code_exts = [p.strip() for p in code_exts.split(';') if p.strip()] if code_exts else []
            code_exts = tuple(set(code_exts))  # 去重并转换成tuple

            rules[rule_name] = {
                'res_suffix': res_exts,
                'code_suffix': code_exts,
            }
        return rules

    def __get_scan_files(self, root_dir, code_suffixs, res_suffixs):
        """获取需要扫描的代码文件和资源文件列表
        """
        root_dir = root_dir.rstrip('\\/')
        code_files = set()
        res_files = set()
        for dirpath, _, filenames in os.walk(root_dir):
            for f in filenames:
                if f.lower().endswith(code_suffixs):
                    fullpath = os.path.join(dirpath, f).replace(os.sep, '/')
                    code_files.add(fullpath)
                if f.lower().endswith(res_suffixs) and '.bundle' not in dirpath:  # 过滤掉.bundle第三方目录中的资源
                    fullpath = os.path.join(dirpath, f).replace(os.sep, '/')
                    res_files.add(fullpath)
        code_files = list(code_files)
        res_files = list(res_files)
        return code_files, res_files

    def __format_file_name(self, res_file_path, reg_num_ptn):
        """对文件路径进行处理,只截取代码引用时会出现的字符串部分

        :param res_file_path: 资源文件全路径
        :param reg_num_ptn: 匹配字符串末尾的数字的正则表达式实例
        :return: 引用时的文件名字符串
        """
        # 删除引用时可能没有的部分(例如"my_pic@3x.png","my_pic~ipad.png",引用时可能只出现"my_pic")
        file_name = os.path.basename(res_file_path)
        file_name = os.path.splitext(file_name)[0]
        file_name = file_name.split('@')[0]
        file_name = file_name.split('~')[0]
        # 删除引用时可能没有的末尾数字(例如"my_ico1","my_ico2",引用时数字部分是变量:"my_ico%d")
        end_num_list = re.findall(reg_num_ptn, file_name)
        if end_num_list:
            end_num = end_num_list[0]
            file_name = file_name[:-len(end_num)]
        return file_name

    def __scan_unused_resources(self, source_dir, code_files, res_files, rules):
        """检查未使用到的资源文件
        :param source_dir: 项目代码根目录
        :param code_files: 代码和配置文件列表
        :param res_files: 资源文件列表
        :param rules: {
            rule_name: {
                'res_suffix': res_exts,
                'code_suffix': code_exts
            }
        }
        :param checker: 扫描工具名
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
        relpos = len(source_dir) + 1

        # 匹配字符串末尾的数字
        num_ptn = re.compile(r"\d+$")

        # 只支持单个规则,如果传递了多个规则,只取第一个规则名作为所有问题的规则名
        rule_name = list(rules.keys())[0]
        # 未使用的资源文件列表,初始化为所有资源文件,后续从列表中逐个删除已使用的文件
        unused_res_files = res_files

        for file_path in code_files:
            # 判断是否是一个文件,过滤掉链接文件,否则会出现打开异常 - IOError: [Errno 2] No such file or directory
            if not os.path.isfile(file_path):
                logger.debug("%s is not a file,filter!" % file_path)
                continue
            with open(file_path, 'rb') as fp:
                file_text = CodecClient().decode(fp.read())
                # 根据代码类型过滤注释
                code_nocomment = CommentsManager(file_path, file_text).remove_comments()
                # 判断资源文件是否使用
                for res_file in unused_res_files[:]:
                    file_name_str = self.__format_file_name(res_file, num_ptn)
                    if file_name_str in code_nocomment:
                        unused_res_files.remove(res_file)
        issues = []
        for res_file in unused_res_files:
            rel_path = res_file[relpos:]
            issues.append({
                'path': rel_path,
                'line': 0,
                'column': 0,
                'msg': u'%s 未使用过,建议删除.' % rel_path,
                'rule': rule_name
            })
        return issues

    def analyze(self, params):
        '''执行扫描任务

        :param params: 需包含下面键值：
           'rules'： lint扫描的规则列表
           'incr_scan' : 是否增量扫描

        :return: return a :py:class:`IssueResponse`
        '''
        source_dir = params['source_dir']
        incr_scan = params['incr_scan']
        rules = self.__format_rules(params['rule_list'])

        logger.info('获取需要扫描的文件')
        code_file_suffixs = ()
        res_file_suffixs = ()
        for rule_name, rule_param in rules.items():
            code_file_suffixs += rule_param['code_suffix']
            res_file_suffixs += rule_param['res_suffix']
        code_file_suffixs = tuple(set(code_file_suffixs))  # 去重
        res_file_suffixs = tuple(set(res_file_suffixs))  # 去重
        code_files, res_files = self.__get_scan_files(source_dir, code_file_suffixs, res_file_suffixs)

        # 增量扫描过滤资源文件
        if incr_scan:
            diffs = SCMMgr(params).get_scm_diff()
            diff_files = [os.path.join(source_dir, diff.path).replace(os.sep, '/')
                          for diff in diffs if diff.state != 'del']
            res_files = [p for p in res_files if p in diff_files]

        # 根据项目的include和exclude配置,过滤资源文件
        relpos = len(source_dir) + 1
        res_files = FilterPathUtil(params).get_include_files(res_files, relpos)

        if not res_files:
            logger.debug("To-be-scanned files is empty ")
            return []

        logger.debug("resource files to scan: %d" % len(res_files))

        # 执行扫描工具
        logger.info('查找未使用的资源文件')
        issues = self.__scan_unused_resources(source_dir, code_files, res_files, rules)

        if not issues:
            logger.info("result is empty ")

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
        # 已经过滤文件和diff增量,不需要重复过滤,只需要根据revision过滤
        return [REVISION_FILTER, PATH_FILTER]

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


tool = UnusedResource

if __name__ == '__main__':
    pass
