# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

'''
代码文件编码检查任务
规则名: WrongEncoding
'''

import os
import logging

logger = logging.getLogger(__name__)

class EncodingCheck(object):
    def __can_be_decode(self, path):
        """判断文件是否能被utf-8解码
        """
        with open(path, 'rb') as fp:
            try:
                file_text = fp.read()
                file_text.decode(encoding='UTF-8')
                return True
            except UnicodeDecodeError:
                return False

    def run(self, params, scan_files, rule_name):
        """扫描主函数

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
        logger.info('逐个文件检查编码格式')
        for file_path in scan_files:
            # 2020/1/2 可能文件不存在，是个软连接
            if not os.path.exists(file_path):
                continue
            if not self.__can_be_decode(file_path):
                issues.append({
                    'path': file_path,
                    'line': 0,
                    'column': 0,
                    'msg': 'File encoding is wrong, should be utf-8.',
                    'rule': 'WrongEncoding'
                })

        logger.debug(issues)
        return issues

checker = EncodingCheck

if __name__ == '__main__':
    pass
