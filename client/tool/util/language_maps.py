# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""工具语言映射规则
"""

# CodeDog语言以及文件后缀名映射
CODEDOG_LANGUAGE_MAPS = {
    "cpp": [".cpp", ".c", ".C", ".cc", ".cxx", ".h", ".hxx", ".hpp"],
    "java": [".java"],
    "js": [".js", ".jsx", ".vue"],
    "oc": [".m", ".mm", ".h", ".hpp"],
    "php": [".php"],
    "python": [".py"],
    "cs": [".cs"],
    "ruby": [".rb", ".cgi"],
    "kotlin": [".kt"],
    "Go": [".go"],
    "Lua": [".lua"],
    "swift": [".swift"],
    "html": [".html", ".htm", ".xhtml", ".cshtml", ".vbhtml", ".rhtml", ".shtm", ".shtml"],
    "css": [".css", ".less", ".scss", ".sass", ".sss"],
    "ts": [".ts", ".tsx"],
    "scala": [".scala"],
    "visualbasic": [".vb", ".VB", ".bas", ".frm", ".cls", ".ctl"],
    "plsql": [".sql", ".pks", ".pkb"],
    "cobol": [".cob"],
    "abap": [".abap", ".ab4", ".flow", ".asprog"],
    "tsql": [".tsql"],
    "flex": [".l", ".flx", ".flex"],
    "rpg": [".rpg",".rpgle", ".RPG", ".RPGLE"],
    "apex": [".cls", ".trigger"],
    "pli": [".pli"],
    "xml": [".xml"],
    "dart": [".dart"],
    "shell": [".sh"],
}

# Cloc工具语言映射表
CLOC_LANGUAGE_MAPS = {
    "oc": ["Objective C", "Objective C++", "C", "C++", "C/C++ Header"],
    "js": ["JavaScript"],
    "c/c++": ["C", "C++", "C/C++ Header"],
    "cpp": ["C", "C++", "C/C++ Header"],
    "cs": ["C#"],
    "ts": ["TypeScript"]
}

# CPD工具语言映射表
CPD_LANGUAGE_MAPS = {
    "cpp": {
        "lang": "cpp",
        "ext": [".cpp", ".c", ".C", ".cc", ".cxx", ".h", ".hxx", ".hpp"]
    },
    "java": {
        "lang": "java",
        "ext": [".java"]
    },
    "js": {
        "lang": "ecmascript",
        "ext": [".js", ".jsx"]
    },
    "oc": {
        "lang": "objectivec",
        "ext": [".m", ".mm"]
    },
    "cs": {
        "lang": "cs",
        "ext": [".cs"]
    },
    "php": {
        "lang": "php",
        "ext": [".php"]
    },
    "python": {
        "lang": "python",
        "ext": [".py"]
    },
    "ruby": {
        "lang": "ruby",
        "ext": [".rb", ".cgi"]
    },
    "Go": {
        "lang": "go",
        "ext": [".go"]
    },
    "swift": {
        "lang": "swift",
        "ext": [".swift"]
    },
    "kotlin": {
        "lang": "kotlin",
        "ext": [".kt"]
    },
    "Lua": {
        "lang": "lua",
        "ext": [".lua"]
    },
    "scala": {
        "lang": "scala",
        "ext": [".scala"]
    },
    "plsql": {
        "lang": "plsql",
        "ext": [
            ".sql",
            ".trg",  # Triggers
            ".prc", ".fnc",  # Standalone Procedures and Functions
            ".pld",  # Oracle*Forms
            ".pls", ".plh", ".plb",  # Packages
            ".pck", ".pks", ".pkh", ".pkb",  # Packages
            ".typ", ".tyb",  # Object Types
            ".tps", ".tpb"  # Object Types
        ]
    },
    "apex": {
        "lang": "apex",
        "ext": [".cls"]
    },
    "dart": {
        "lang": "dart",
        "ext": [".dart"]
    }
}

# Lizard工具语言映射表
LIZARD_LANGUAGE_MAPS = {
    "java": {
        "lang": "java",
        "ext": [".java"]
    },
    "cs": {
        "lang": "csharp",
        "ext": [".cs"]
    },
    "cpp": {
        "lang": "cpp",
        "ext": [".c", ".cpp", ".cc", ".mm", ".cxx", ".h", ".hpp"]
    },
    "js": {
        "lang": "javascript",
        "ext": [".js"]
    },
    "oc": {
        "lang": "objectivec",
        "ext": [".m"]
    },
    "php": {
        "lang": "php",
        "ext": [".php"]
    },
    "python": {
        "lang": "python",
        "ext": [".py"]
    },
    "ruby": {
        "lang": "ruby",
        "ext": [".rb"]
    },
    "swift": {
        "lang": "swift",
        "ext": [".swift"]
    },
    "Go": {
        "lang": "go",
        "ext": [".go"]
    },
    "Lua": {
        "lang": "lua",
        "ext": [".lua"]
    },
    "scala": {
        "lang": "scala",
        "ext": [".scala"]
    }
}
