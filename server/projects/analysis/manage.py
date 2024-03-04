#!/usr/bin/env python
# coding:utf-8
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

import os
import sys


if __name__ == "__main__":

    django_setting_module = os.environ.get("DJANGO_SETTINGS_MODULE", "codedog.settings.local")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", django_setting_module)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
