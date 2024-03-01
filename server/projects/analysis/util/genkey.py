# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
Key generation
"""
import hashlib


def gen_path_key(path):
    """generate key for file path
    """
    path = path.encode("utf-8")
    return hashlib.sha1(path).hexdigest()
