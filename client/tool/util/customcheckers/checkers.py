# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""customscan工具的 规则-检查器 映射表  {rule_name: checker_module, ...}

"""
rule_checker = {
    # 检查文件头是否有Copyright信息
    "CopyrightChecker": "copyright_check",
    # 检查文件编码是否是utf-8
    "WrongEncoding": "encodingcheck",
    # 检查项目中行数过长的文件
    "FileTooLong": "file_too_long",
    # 检查项目中是否包含不该有的文件或者目录
    "FilesFound": "files_found",
    # 检查项目中是否包含必备的文件或者目录
    "FilesNotFound": "files_not_found",
    # 检查项目中行数过长的函数
    "FunctionTooLong": "function_too_long",
    # 检查git库里的大文件
    "LFSChecker": "lfs_check",
    # 检查代码文件中的注释占比是否符合要求
    "LowCommentRatio": "low_comment_ratio",
    # 检查文件换行符为CRLF
    "NewlineChecker": "newline_check",
    "NoEncodingFormat": "no_encoding_format",
    "NoUsedImport": "no_used_import"
}
