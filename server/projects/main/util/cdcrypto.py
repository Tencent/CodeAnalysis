# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
util.cdcrypto 密码加解密模块
"""

from base64 import b64decode
from binascii import b2a_hex, a2b_hex

import Crypto
import pyaes
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

from util import errcode
from util.exceptions import ServerError


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
    if key is None:
        raise ServerError(errcode.E_SERVER, "Encrypt key should not be none.")
    key = __encode(key)
    aes = pyaes.AESModeOfOperationCTR(key)
    pwd = b2a_hex(aes.encrypt(plain_password))
    return __decode(pwd)


def decrypt(cipher_password, key):
    """使用key对password密文进行解密"""
    if cipher_password is None or cipher_password == "":
        return cipher_password
    if key is None:
        raise ServerError(errcode.E_SERVER, "Decrypt key should not be none.")
    key = __encode(key)
    aes = pyaes.AESModeOfOperationCTR(key)
    pwd = aes.decrypt(a2b_hex(cipher_password))
    return __decode(pwd)


def rsa_encrypt(plain_text, key):
    """ras 加密"""
    pass


def rsa_decrypt(cipher_password, key, base64encode=True):
    """rsa 解密"""
    if base64encode:
        cipher_password = b64decode(cipher_password)
    key = RSA.importKey(key)
    cipher = PKCS1_OAEP.new(key)
    modBits = Crypto.Util.number.size(key.n)
    k = Crypto.Util.number.ceil_div(modBits, 8)
    message = b""
    for i in range(0, len(cipher_password), k):
        message += cipher.decrypt(cipher_password[i:i+k])
    return message
