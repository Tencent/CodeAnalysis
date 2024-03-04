# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""处理编码
"""


def encode_with_ignore(text):
    """采用ignore方式处理编码
    """
    if isinstance(text, str):
        text = text.encode("utf-8", "ignore").decode("utf-8")
    return text
