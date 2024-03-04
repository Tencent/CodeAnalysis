# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - base models
"""
# 第三方
from django.db import models

# 项目内
from apps.base.basemodel import CDBaseModel


class Language(models.Model):
    """语言表
    """

    class LanguageEnum(object):
        CPP = 'cpp'
        JAVA = 'java'
        JAVASCRIPT = 'js'
        OBJECTIVEC = 'oc'
        PHP = 'php'
        PYTHON = 'python'
        CSHARP = 'cs'
        RUBY = 'ruby'
        KOTLIN = 'kotlin'
        GO = 'Go'
        LUA = 'Lua'
        SWIFT = 'swift'
        HTML = 'html'
        CSS = 'css'
        TYPESCRIPT = 'ts'
        SCALA = 'scala'
        VISUALBASIC = 'visualbasic'
        PLSQL = 'plsql'
        COBOL = 'cobol'
        ABAP = 'abap'
        TSQL = 'tsql'
        FLEX = 'flex'
        RPG = 'rpg'
        APEX = 'apex'
        PLI = 'pli'
        XML = 'xml'
        DART = 'dart'
        SHELL = 'shell'
        PB = 'protobuf'
        SQL = 'sql'
        WASM = "wasm"
        RUST = "rust"

    LANGUAGE_CHOICES = (
        (LanguageEnum.CPP, 'C/C++'),
        (LanguageEnum.JAVA, 'Java'),
        (LanguageEnum.JAVASCRIPT, 'JavaScript'),
        (LanguageEnum.OBJECTIVEC, 'Objective-C'),
        (LanguageEnum.PHP, 'PHP'),
        (LanguageEnum.PYTHON, 'Python'),
        (LanguageEnum.CSHARP, 'C#'),
        (LanguageEnum.RUBY, 'Ruby'),
        (LanguageEnum.KOTLIN, 'Kotlin'),
        (LanguageEnum.GO, 'Go'),
        (LanguageEnum.LUA, 'Lua'),
        (LanguageEnum.SWIFT, 'Swift'),
        (LanguageEnum.HTML, 'Html'),
        (LanguageEnum.CSS, 'Css'),
        (LanguageEnum.TYPESCRIPT, 'TypeScript'),
        (LanguageEnum.SCALA, 'Scala'),
        (LanguageEnum.VISUALBASIC, 'Visual Basic'),
        (LanguageEnum.PLSQL, 'PL/SQL'),
        (LanguageEnum.COBOL, 'COBOL'),
        (LanguageEnum.ABAP, 'ABAP'),
        (LanguageEnum.TSQL, 'T-SQL'),
        (LanguageEnum.FLEX, 'Flex'),
        (LanguageEnum.RPG, 'RPG'),
        (LanguageEnum.APEX, 'Apex'),
        (LanguageEnum.PLI, 'PL/I'),
        (LanguageEnum.XML, 'XML'),
        (LanguageEnum.DART, "Dart"),
        (LanguageEnum.SHELL, "Shell"),
        (LanguageEnum.PB, "Protocol Buffers"),
        (LanguageEnum.SQL, "SQL"),
        (LanguageEnum.WASM, "WebAssembly"),
        (LanguageEnum.RUST, "Rust"),
    )

    name = models.CharField(max_length=32, help_text='程序语言', choices=LANGUAGE_CHOICES, null=True)

    def __str__(self):
        return self.get_name_display()


class Label(models.Model):
    """标签表
    """
    name = models.CharField(max_length=64, unique=True, help_text='标签名')

    def __str__(self):
        return self.name


class ScanApp(CDBaseModel):
    """项目扫描应用列表
    """
    name = models.CharField("扫描应用名", max_length=32, unique=True, help_text="必须是codedog/apps/下的包名")
    label = models.CharField("扫描应用显示名", max_length=64)
    desc = models.CharField("应用描述", max_length=128, null=True)

    def __str__(self):
        return self.label


class Process(models.Model):
    """子进程表
    """
    name = models.CharField(max_length=64, help_text="名称", unique=True)
    display_name = models.CharField(max_length=64, help_text="展示名称")
    priority = models.IntegerField(help_text="优先级")

    def __str__(self):
        return self.display_name


class CheckToolWhiteKey(models.Model):
    """工具可被使用的白名单表
    """
    tool_key = models.CharField(max_length=64, help_text="工具key值，org_'<org_id>'")
    tool_id = models.IntegerField(help_text="工具id")

    class Meta:
        unique_together = ("tool_key", "tool_id")
