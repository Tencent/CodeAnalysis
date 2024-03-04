# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
支持的语言类型
"""


class LanguageType(object):
    # 语言名称映射关系
    # key: 前端展示名称
    # value - user_input: 支持用户输入的名称的小写形式，包括简写，使用前需要先将用户输入字符串转换成小写
    # value - server_name: server端支持的名称，传给server使用
    LANGUAGE_DICT = {
        "ABAP": {"user_input": ["abap"], "server_name": "abap"},
        "Apex": {"user_input": ["apex"], "server_name": "apex"},
        "C/C++":       {"user_input": ["c/c++", "c/cpp", "c", "c++", "cpp"], "server_name": "cpp"},
        "C#": {"user_input": ["c#"], "server_name": "cs"},
        "COBOL": {"user_input": ["cobol"], "server_name": "cobol"},
        "Css": {"user_input": ["css"], "server_name": "css"},
        "Dart": {"user_input": ["dart"], "server_name": "dart"},
        "Flex": {"user_input": ["flex"], "server_name": "flex"},
        "Go": {"user_input": ["go"], "server_name": "go"},
        "Html": {"user_input": ["html"], "server_name": "html"},
        "Java":        {"user_input": ["java"], "server_name": "java"},
        "JavaScript":  {"user_input": ["javascript"], "server_name": "js"},
        "Kotlin": {"user_input": ["kotlin"], "server_name": "kotlin"},
        "Lua": {"user_input": ["lua"], "server_name": "lua"},
        "Objective-C": {"user_input": ["objective-c", "oc"], "server_name": "oc"},
        "PHP":         {"user_input": ["php"], "server_name": "php"},
        "PL/I": {"user_input": ["pl/i", "pli"], "server_name": "pli"},
        "PL/SQL": {"user_input": ["pl/sql"], "server_name": "plsql"},
        "Python":      {"user_input": ["python"], "server_name": "python"},
        "RPG": {"user_input": ["rpg"], "server_name": "rpg"},
        "Ruby":        {"user_input": ["ruby"], "server_name": "ruby"},
        "Scala": {"user_input": ["scala"], "server_name": "scala"},
        "Shell": {"user_input": ["shell"], "server_name": "shell"},
        "Swift":       {"user_input": ["swift"], "server_name": "swift"},
        "T-SQL": {"user_input": ["t-sql", "tsql"], "server_name": "tsql"},
        "TypeScript":  {"user_input": ["typescript", "ts"], "server_name": "ts"},
        "VisualBasic": {"user_input": ["visualbasic", "vb"], "server_name": "visualbasic"},
        "XML": {"user_input": ["xml"], "server_name": "xml"}
    }

    # 前端展示语言名称,按字母序排序
    INPUT_LANGUAGE_NAMES = sorted(list(LANGUAGE_DICT.keys()))


# scanlang工具 与 codedog 语言名称映射关系
# key:   scanlang工具识别的语言类型名
# value: codedog支持用户输入的语言类型名
# 如果util.languagetype中的codedog支持的语言类型有更新,该映射表也需要更新
LangMap = {
    "C": "C/C++",
    "C++": "C/C++",
    "C#": "C#",
    "CSS": "Css",
    "Go": "Go",
    "HTML": "Html",
    "Kotlin": "Kotlin",
    "Java": "Java",
    "JavaScript": "JavaScript",
    "Lua": "Lua",
    "Objective-C": "Objective-C",
    "Objective-Cpp": "Objective-C",
    "PHP": "PHP",
    "Python": "Python",
    "Ruby": "Ruby",
    "Scala": "Scala",
    "Swift": "Swift",
    "TypeScript": "TypeScript",
    "VisualBasic": "VisualBasic"
}


if __name__ == '__main__':
    print(LanguageType.INPUT_LANGUAGE_NAMES)
    print(','.join(LanguageType.INPUT_LANGUAGE_NAMES))
