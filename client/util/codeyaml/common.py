# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
code yaml公共方法
"""

import os


class CodeYaml(object):
    # 支持的yaml文件名
    supported_yaml_names = [".code.yml", ".code.yaml"]

    @staticmethod
    def get_yaml_filepath(source_dir):
        """
        获取code yaml文件路径, 依次判断允许的文件名后缀, 文件存在则返回路径；未找到符合的文件, 返回None
        """
        for yaml_name in CodeYaml.supported_yaml_names:
            file_path = os.path.join(source_dir, yaml_name)
            if os.path.exists(file_path):
                return file_path
        return None

    @staticmethod
    def get_yaml_files(source_dir):
        """
        在代码目录下遍历获取.code.yml文件
        :param source_dir:
        :return: .code.yml文件路径与所在目录的映射关系列表，[{"yaml_path": xxx, "dir_path": xxx}, ...]
        """
        yaml_files = []
        for dirpath, dirs, filenames in os.walk(source_dir):
            for f in filenames:
                if f.lower() in CodeYaml.supported_yaml_names:
                    yaml_path = os.path.join(dirpath, f)
                    yaml_files.append(
                        {
                            "yaml_path": yaml_path,
                            "dir_path": dirpath.replace(os.sep, '/')
                        }
                    )
        # logger.info(".code.yml files: %s" % json.dumps(yaml_files, indent=2))
        return yaml_files
