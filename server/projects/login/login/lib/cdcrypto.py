# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
cdcrypto 密码加解密模块
"""

import pyaes
from binascii import b2a_hex, a2b_hex


def __encode(content):
    if type(content) == str:
        content = content.encode("utf-8")
    return content


def __decode(content):
    if type(content) == bytes:
        content = content.decode("utf-8")
    return content


def encrypt(plain_password, key):
    """使用key对password明文进行加密"""
    if plain_password is None or plain_password == "":
        return plain_password
    key = __encode(key)
    aes = pyaes.AESModeOfOperationCTR(key)
    pwd = b2a_hex(aes.encrypt(plain_password))
    return __decode(pwd)


def decrypt(cipher_password, key):
    """使用key对password密文进行解密"""
    if cipher_password is None or cipher_password == "":
        return cipher_password
    key = __encode(key)
    aes = pyaes.AESModeOfOperationCTR(key)
    pwd = aes.decrypt(a2b_hex(cipher_password))
    return __decode(pwd)
