# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""yaml文件读写工具类
"""

import yaml
import logging

logger = logging.getLogger(__name__)


class YamlReader(object):
    def read_section(self, filepath, section):
        """
        逐行读取解析，只获取需要的section对应的内容，section只支持顶层的字段
        :param filepath:
        :param section:
        :return:
        """
        section_lines = []
        in_section = False

        with open(filepath, 'r', encoding='utf-8') as rf:
            line = rf.readline()
            while line:
                if line.strip().startswith('#'):
                    # 注释行,忽略
                    # print("[comment]%s" % line)
                    pass
                elif line.startswith((section+':', section+' ')):
                    # print('[start]%s' % line)
                    section_lines.append(line)
                    in_section = True
                elif in_section:
                    if line.startswith((' ', '-', '\n', '\r\n')):
                        # print('[in]%s' % line)
                        section_lines.append(line)
                    else:
                        # print('[end]%s' % line)
                        break
                line = rf.readline()
        if section_lines:
            section_str = '\n'.join(section_lines)
            section_dict = yaml.safe_load(section_str)
            return section_dict[section]
        else:
            return {}


if __name__ == '__main__':
    import json
    import time

    print("[ 逐行读取 ] :")
    print("-" * 50)
    file_path = "***/.code.yml"
    section_name = "file"
    start_time = time.time()
    data = YamlReader().read_section(file_path, section_name)
    use_time = time.time() - start_time
    print("-" * 50)
    print(json.dumps(data, indent=2))
    print("-" * 50)
    print("逐行读取后加载 use time: %s" % use_time)
    print("-" * 50)

    # 对比
    # print("\n[ 全量加载 ] :")
    # start_time = time.time()
    # with open(file_path, 'r', encoding='utf-8') as fp:
    #     data = yaml.safe_load(fp)
    # use_time = time.time() - start_time
    # print("-" * 50)
    # print(json.dumps(data[section_name], indent=2))
    # print("-" * 50)
    # print("全量加载 use time: %s" % use_time)
