# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
在结果中添加文件负责人信息。
用户可以在代码库中不同目录下添加.code.yml文件,yaml中包含以下字段内容：

#自定义文件或目录owner和c代码评审配置
file :
  # path支持文件或目录，目录以/结束。path为相对路径，支持两种开头格式：
      1. 基于代码库根目录的相对路径，以/开头；
      2. 基于.code.yml所在目录的相对路径，以./开头，或无开头标识，直接为路径。
  - path: "./classes/app/1.md"
    #文件负责人
    owners :  ["harry", "polly"]

优先级：
1. 同一个yaml文件下,如果path直接有交集，先写父目录再写子目录，越往后的路径优先级越高
2. 不同目录的yaml文件，子目录下的yaml文件高于父目录下的yaml文件
"""

import re
import json
import logging

from util.yamlib import YamlReader
from util.codeyaml.common import CodeYaml

logger = logging.getLogger(__name__)


class FileOwner(object):
    def __get_file_owners(self, yaml_files, source_dir):
        """
        逐个解析.code.yml文件，获取代码目录/文件对应的负责人信息
        :param file_dir_map:
        :param source_dir
        :return:
        """
        relpos = len(source_dir) + 1
        file_owners = []
        for item in yaml_files:
            yaml_path, dir_path = item["yaml_path"], item["dir_path"]
            try:
                file_info_list = YamlReader().read_section(yaml_path, "file")

                logger.info("file_owners(%s): %s" % (yaml_path, json.dumps(file_info_list, indent=2)))
                if file_info_list:
                    for info in file_info_list:
                        path = info["path"]

                        if path.startswith("/"):  # 基于项目根目录的相对路径
                            rel_path = path[1:]
                        else:  # 基于.code.yml文件所在目录的相对路径
                            if path.startswith("./"):
                                path = path[2:]
                            full_path = "%s/%s" % (dir_path, path)
                            rel_path = full_path[relpos:]

                        # 如果路径包含.*字符，说明是正则表达式，先实例化正则，提高匹配效率
                        if ".*" in rel_path:
                            try:
                                regex_object = re.compile(rel_path)
                            except Exception as err:
                                err_msg = "yaml file owner path(%s) format is wrong, skip: %s" % (rel_path, str(err))
                                logger.error(err_msg)
                                regex_object = None
                        else:
                            regex_object = None
                        file_owners.append(
                            {"rel_path": rel_path, "regex_object": regex_object, "owners": info["owners"]}
                        )
            except:
                logger.exception("encounter Error when analyze %s" % yaml_path)
        return file_owners

    def __find_owners(self, format_path, file_owners_list):
        """
        查找文件对应的负责人信息
        :param format_path: 代码文件的相对路径
        :param file_owners_list: 路径与负责人对照表，相对路径，支持目录（目录以/结尾）
        :return:
        """
        # 复制一份，不影响原列表
        tmp_list = file_owners_list[:]
        while tmp_list:
            # 倒序判断,保证优先级: 1.同一个yaml文件下,越往后的路径优先级越高；2.不同目录的yaml文件，子目录下的yaml配置高于父目录下的
            item = tmp_list.pop()
            rel_path = item["rel_path"]
            regex_object = item["regex_object"]
            # 有正则对象的情况下，按正则表达式匹配；否则，按照字符串匹配
            if regex_object:
                if regex_object.fullmatch(format_path):
                    return item["owners"]
            elif format_path.startswith(rel_path):
                return item["owners"]
        return None

    def add_file_owner_info(self, params, fileissues):
        """
        增加文件责任人信息
        :param fileissues:
        :return:
        """
        source_dir = params["source_dir"]
        yaml_files = CodeYaml.get_yaml_files(source_dir)
        if yaml_files:
            logger.info("根据.code.yml文件,添加文件负责人信息。代码库下有以下.code.yml文件:")
            for info in yaml_files:
                logger.info(info["yaml_path"])
            # 解析文件
            file_owners_list = self.__get_file_owners(yaml_files, source_dir)
            # 逐个查找并添加对应的文件负责人信息
            for fileissue in fileissues:
                path = fileissue.get("path")
                format_path = path.replace("\\", "/")
                file_owners = self.__find_owners(format_path, file_owners_list)
                # 添加文件负责人信息
                if file_owners:
                    # 文件负责人放在文件级别，不在issue内；转换为以英文分号分隔的字符串
                    file_owners = ";".join(file_owners)
                    fileissue["owners"] = file_owners
        return fileissues


if __name__ == "__main__":
    pass
