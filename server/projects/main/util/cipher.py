#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================


import string


class CaesarCipher(object):
    """
    凯撒加密解密
    """

    def __crypt(self, char, key):
        """
        对单个字母加密，偏移
        @param char: {str} 单个字符
        @param key: {num} 偏移量
        @return: {str} 加密后的字符
        """
        if not char.isalpha():
            return char
        else:
            base = "A" if char.isupper() else "a"
            return chr((ord(char) - ord(base) + key) % 26 + ord(base))

    def encrypt(self, char, key):
        """
        对字符加密
        """
        return self.__crypt(char, key)

    def decrypt(self, char, key):
        """
        对字符解密
        """
        return self.__crypt(char, -key)

    def __crypt_text(self, func, text, key):
        """
       对文本加密
       @param char: {str} 文本
       @param key: {num} 偏移量
       @return: {str} 加密后的文本
       """
        lines = []
        for line in text.split("\n"):
            words = []
            for word in line.split(" "):
                chars = []
                for char in word:
                    chars.append(func(char, key))
                words.append("".join(chars))
            lines.append(" ".join(words))
        return "\n".join(lines)

    def encrypt_text(self, text, key):
        """
        对文本加密
        """
        return self.__crypt_text(self.encrypt, text, key)

    def decrypt_text(self, text, key):
        """
        对文本解密
        """
        return self.__crypt_text(self.decrypt, text, key)


class Base62Cipher(object):
    """
    62进制
    """
    digit62 = string.digits + string.ascii_letters

    # 得到的结果: '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    # 整数转化为62进制字符串
    # 入口：
    #   x : 整数
    # 返回： 字符串
    def int_to_str62(self, x):
        try:
            x = int(x)
        except:
            x = 0
        if x < 0:
            x = -x
        if x == 0:
            return "0"
        s = ""
        while x > 62:
            x1 = x % 62
            s = self.digit62[x1] + s
            x = x // 62
        if x > 0:
            s = self.digit62[x] + s
        return s

    # 62进制字符串转化为整数
    # 入口：
    #   s : 62进制字符串
    # 返回： 整数
    def str62_to_int(self, s):
        x = 0
        s = str(s).strip()
        if s == "":
            return x
        for y in s:
            k = self.digit62.find(y)
            if k >= 0:
                x = x * 62 + k
        return x
