# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
工具作用：扫描py中有没使用的导入和import *
修改指引：规范使用导入功能。

"""
import os
from util.textutil import CodecClient, CommentsManager


class NoUsedImport(object):
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

            # 初始化需要返回json列表/行数/列数
            line_num = 0
            import_list = []
            # 先把所有的内容取进列表中
            with open(file_path, 'rb') as rf:
                file_text = CodecClient().decode(rf.read())
                # 根据代码类型过滤注释
                code_nocomment = CommentsManager(file_path, file_text).remove_comments()
                filelines = code_nocomment.splitlines()

            # 检查耗性能的import方式,并收集其他的import模块
            for textline in filelines:
                line_num += 1
                textline = textline.strip()  # 去掉每行头尾空白及换行符
                # 读取的一行是否含有import *，如果有则报错
                if 'import ' in textline and '*' in textline:
                    issues.append({
                        'msg': '因为性能问题，建议不要写import *，导入需要使用的类或方法就好。',
                        'path': file_path,
                        'line': line_num,
                        'column': 1,
                        'rule': rule_name
                    })
                # 针对正常的导入，收集到列表中
                if 'import ' in textline and '*' not in textline:
                    tmp_import_list = textline.split(',')  # 处理一行导入多个的情况
                    tmp_import_list = [item.strip() for item in tmp_import_list]  # 删除空格
                    tmp_import_list[0] = tmp_import_list[0].split()[-1]  # 处理首个字符串
                    import_list.extend(tmp_import_list)

            # 统计每个import模块出现的次数和出现的行号
            import_list = list(set(import_list))  # 去重
            import_count = {}
            for item in import_list:
                import_count[item] = {"count": 0, "line_num": 1}

            line_num = 0
            for line in filelines:
                line_num += 1
                for item in import_list:
                    if item in line:
                        import_count[item]["count"] += 1
                        import_count[item]["line_num"] = line_num

            # 因为会在导入自己的那行文本时加1，如果没有使用则文中出现1次，如果有使用则出现大于1次
            for key, value in import_count.items():
                if value["count"] == 1:
                    issues.append({
                        'msg': u'发现未使用过的import模块，建议删除',
                        'path': file_path,
                        'line': value["line_num"],
                        'column': 1,
                        'rule': rule_name
                    })

        return issues


checker = NoUsedImport

if __name__ == '__main__':
    pass
