# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
cdcrypto 密码加解密模块
"""


from binascii import a2b_hex

import pyaes


def __encode(content):
    if type(content) == str:
        content = content.encode("utf-8")
    return content


def __decode(content):
    if type(content) == bytes:
        content = content.decode("utf-8")
    return content


def decrypt(cipher_password, key):
    """使用key对password密文进行解密"""
    if cipher_password is None:
        return None
    if key is None:
        raise Exception("Decrypt key should not be none.")
    key = __encode(key)
    aes = pyaes.AESModeOfOperationCTR(key)
    pwd = aes.decrypt(a2b_hex(cipher_password))
    return __decode(pwd)
