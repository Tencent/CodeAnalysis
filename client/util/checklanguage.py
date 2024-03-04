# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
根据后缀名自动识别项目语言
"""


import os
import logging

from util.scanlang.scanlang import ScanLang
from util.scanlang.langconfig import LANGUAGES
from util.languagetype import LanguageType, LangMap
from util.pathfilter import FilterPathUtil

logger = logging.getLogger(__name__)


class LanguageChecker(object):
    """
    语言识别类
    """
    @staticmethod
    def recognize_language(source_dir, task_params, language_max=None):
        """
        根据代码目录下的文件后缀名识别项目包含的代码语言
        :param source_dir:
        :param task_params:
        :param language_max: 结果中包含的语言个数，如果有设置，只取最多的 max_lang 个语言
        :return:
        """
        # 先添加SOURCE_DIR环境变量，方便后续FilterPathUtil过滤时获取.code.yml文件使用
        os.environ["SOURCE_DIR"] = source_dir
        filter_mgr = FilterPathUtil(task_params)
        scan_result = ScanLang(source_dir).scan()
        lang_data = {}
        for name, files in scan_result["languages"].items():
            file_count = len(files)
            if file_count > 0 and name in LangMap:
                format_name = LangMap[name]
                if format_name in lang_data:
                    lang_data[format_name].extend(files)
                else:
                    lang_data[format_name] = files

        relpos = len(source_dir) + 1
        filtered_lang_data = {}
        # 根据过滤路径，过滤掉不需要扫描的文件
        for name, files in lang_data.items():
            incude_files = filter_mgr.get_include_files(files, relpos)
            if incude_files:
                filtered_lang_data[name] = incude_files

        # 计算各语言的文件数
        lang_files_count = {}
        for name, files in filtered_lang_data.items():
            lang_files_count[name] = len(files)

        # 按照文件数对语言排序
        sorted_lang_list = sorted(lang_files_count.items(),
                                  key=lambda lang_files_count:lang_files_count[1],
                                  reverse=True)
        logger.info("各语言对应的代码文件数如下:")
        for name, file_cnt in sorted_lang_list:
            logger.info("%s: %s" % (name, file_cnt))

        lang_name_list = [name for name, cnt in sorted_lang_list]
        # 如果限制了语言数量，且超过上限，取最多的几个语言数据
        if language_max and len(lang_name_list) > language_max:
            selected_lang_names = lang_name_list[:language_max]
            logger.info("取文件数最多的 %s 种语言，作为项目的主要语言: %s" % (language_max, selected_lang_names))
            sorted_lang_data = {}
            for name, files in filtered_lang_data.items():
                if name in selected_lang_names:
                    sorted_lang_data[name] = files
            return sorted_lang_data
        else:
            return filtered_lang_data

    @staticmethod
    def get_file_language_type(file_path):
        """
        根据文件名后缀，识别代码语言类型
        :param file_path:
        :return:
        """
        ext = os.path.splitext(file_path)[1].lower()
        # 根据后缀名识别出语言类型
        language_type = LANGUAGES.get(ext, None)
        if language_type:
            # scanlang里面的语言名称格式
            type_name = language_type.name
            if type_name in LangMap:
                # 前端展示的语言名称格式
                input_type_name = LangMap[type_name]
                if input_type_name in LanguageType.LANGUAGE_DICT:
                    # server端支持的名称格式
                    return LanguageType.LANGUAGE_DICT[input_type_name].get("server_name")
        # 未识别的语言类型，返回None
        return None


if __name__ == '__main__':
    pass
