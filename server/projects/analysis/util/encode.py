# -*- coding: utf-8 -*-
"""处理编码
"""


def encode_with_ignore(text):
    """采用ignore方式处理编码
    """
    if isinstance(text, str):
        text = text.encode("utf-8", "ignore").decode("utf-8")
    return text
