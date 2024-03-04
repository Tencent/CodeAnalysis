# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
工具作用：扫描.py文件开头没有编码格式
修改指引：增加指定明确的编码格式。

"""


import os


class NoEncodingFormat(object):
    def run(self, params, scan_files, rule_name):
        """
        :param params: 任务参数
        :param scan_files: 需要扫描的文件列表
        :param rule_name: 规则名,通过外部传递
        :return: [
                   {'path':...,
                    'line':...,
                    'column':...,
                    'msg':...,
                    'rule':...
                   },
                   ...
                ]
        """
        issues = []

        for file_path in scan_files:
            # 过滤不需要扫描的文件
            file_name = os.path.basename(file_path)
            if not file_name.lower().endswith('.py'):
                continue
            if file_name == "__init__.py":
                continue

            # 初始化需要返回json列表/行数/列数
            codeline = 1
            codecol = 1

            #然后开始逐行读取判断
            with open(file_path,'r') as pyfile:
                firstline = pyfile.readline()
                if 'coding' not in firstline:
                    # 排除第一行是‘#!/usr/bin/python’的情况,所以要再读一行
                    secondline = pyfile.readline()
                    if 'coding' not in secondline:
                        item = {}
                        item['msg'] = u'py文件缺少编码格式'
                        item['path'] = file_path
                        item['line'] = codeline
                        item['column'] = codecol
                        item['rule'] = rule_name
                        issues.append(item)
        return issues


checker = NoEncodingFormat

if __name__ == '__main__':
    pass
