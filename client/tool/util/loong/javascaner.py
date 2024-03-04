#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================


from tool.util.loong.bcparser import ByteCodeParser
from tool.util.loong.astparser import ASTParser
from util.logutil import LogPrinter


logger = LogPrinter


class JavaScaner:

    ap = None
    ast = None
    diff_files = None

    def __init__(self, source_dir, out_dir=None, jar_mode=False):
        self.source_dir = source_dir
        self.jar_mode = jar_mode
        self.ap = ByteCodeParser(self.source_dir, out_dir)
        self.ast = ASTParser(self.source_dir, out_dir)

    def parser(self, need_bc=True, need_ast=False, need_field=False):
        if need_bc:
            self.ap.parser(need_field)
        if need_ast:
            self.ast.parser()

    def set_diff_files(self, diff_files):
        self.diff_files = diff_files


if __name__ == "__main__":
    pass
