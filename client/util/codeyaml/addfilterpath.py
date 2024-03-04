# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
读取项目根目录下的.code.yml文件,获取过滤路径，添加到项目过滤路径中
"""

from util.yamlib import YamlReader
from util.logutil import LogPrinter
from util.codeyaml.common import CodeYaml


class AddFilterPath(object):
    @staticmethod
    def modify_filters(task_params, path_filters):
        """
        根据.code.yml文件配置，修改过滤路径
        :param task_params:
        :param path_filters:
        :return:
        """
        yaml_filters = AddFilterPath.__get_regex_paths(task_params["source_dir"])
        test_source = yaml_filters["test_source"]
        auto_generate_source = yaml_filters["auto_generate_source"]
        third_party_source = yaml_filters["third_party_source"]

        # 1. 代码度量：过滤测试代码、自动生成代码、第三方代码
        LogPrinter.info("Codemetric only scans main code "
                        "(exclude test_source, auto_generate_source, third_party_source).")
        for path_list in [test_source, auto_generate_source, third_party_source]:
            path_filters["metric_exclusion"].extend(path_list)
            path_filters["yaml_filters"]["metric_exclusion"].extend(path_list)

        # 2. 代码检查：按照任务参数选择性过滤
        # code_yaml_filter参数值：
        #     None & 1 - 只扫描业务、测试代码
        #     2 - 只扫描业务代码
        #     3 - 只扫描测试代码
        filter_type = task_params.get("code_yaml_filter")
        # 2.1 默认过滤自动生成代码和第三方代码
        for path_list in [auto_generate_source, third_party_source]:
            path_filters["exclusion"].extend(path_list)
            path_filters["yaml_filters"]["lint_exclusion"].extend(path_list)
        # 2.2 测试代码和业务代码根据参数过滤
        if filter_type == 1:  # 扫描测试代码和业务代码
            LogPrinter.info("Codelint only scans main and test code.")
        elif filter_type is None or filter_type == 2:  # 只扫描业务代码
            LogPrinter.info("Codelint only scans main code.")
            path_filters["exclusion"].extend(test_source)
            path_filters["yaml_filters"]["lint_exclusion"].extend(test_source)
        elif filter_type == 3:  # 只扫描测试代码
            LogPrinter.info("Codelint only scans test code.")
            path_filters["inclusion"].extend(test_source)
            path_filters["yaml_filters"]["lint_inclusion"].extend(test_source)
        else:  # 业务代码和测试代码都不扫描，忽略
            LogPrinter.error("Task param is wrong! code_yaml_filter=%s(expect 1, 2 or 3)" % filter_type)

    @staticmethod
    def __get_regex_paths(source_dir):
        """
        根据.code.yml，增加过滤路径，更新path_filters
        :return: yaml_filters
        """
        # 初始化
        yaml_filters = {
            "test_source": [],  # 测试代码
            "auto_generate_source": [],  # 工具或框架自动生成的代码
            "third_party_source": []  # 第三方代码
        }

        yaml_file = CodeYaml.get_yaml_filepath(source_dir)

        try:
            if yaml_file:
                LogPrinter.info("Filter paths according to .code.yml ...")
                exclude_src = YamlReader().read_section(yaml_file, "source")
                if exclude_src:
                    for src_type, src_config in exclude_src.items():
                        if src_type in yaml_filters:  # 判断是需要的字段
                            LogPrinter.info(f"{src_type} : {src_config}")
                            if src_config:
                                filepath_list = src_config.get("filepath_regex")
                                if filepath_list:
                                    for path_pattern in filepath_list:
                                        # 特殊处理,删除开头的/(此处/开头表示从代码根目录开始的相对路径)
                                        if path_pattern.startswith('/'):
                                            path_pattern = path_pattern[1:]
                                        # 特殊处理,删除开头的./(此处./开头表示从当前目录开始的相对路径)
                                        if path_pattern.startswith('./'):
                                            path_pattern = path_pattern[2:]
                                        # 过滤掉空字符串的情况
                                        if len(path_pattern) > 0:
                                            yaml_filters[src_type].append(path_pattern)
        except Exception as err:
            err_msg = "根据代码目录下的.code.yml文件更新过滤路径出现异常,请检查yaml文件格式是否有误!"
            LogPrinter.error("%s %s" % (err_msg, str(err)))
            # raise ConfigError("%s %s" % (err_msg, str(err)))
            LogPrinter.warning(".code.yml文件解析失败，将导致其中的过滤配置不生效!")
        finally:
            return yaml_filters


if __name__ == '__main__':
    pass
