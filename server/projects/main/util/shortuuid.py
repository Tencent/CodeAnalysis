# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""生成项目编号UUID
"""
import string
from os import urandom
from struct import unpack


class ShortIDGenerator(object):

    @classmethod
    def generate_urandom_8(cls):
        """获取8位随机值
        """
        return unpack("<Q", urandom(8))[0]

    @classmethod
    def base62(cls, num):
        """ Short ID generator - v5: Base62-Encoded Urandom """
        if num <= 0:
            result = "0"
        else:
            alphabet = string.digits + string.ascii_uppercase + string.ascii_lowercase
            key = []
            while num > 0:
                num, rem = divmod(num, 62)
                key.append(alphabet[rem])
            result = "".join(reversed(key))
        return result

    @classmethod
    def generate_short_id_v1(cls):
        return cls.base62(cls.generate_urandom_8())


