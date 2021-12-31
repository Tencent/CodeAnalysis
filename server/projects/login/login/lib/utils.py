# -*- coding: utf-8 -*-
"""
login lib - utils
"""
import re
import random
import string


def id_generator(size=6, chars=string.digits):
    """随机生成数字密码，默认6位
    """
    return "".join(random.choice(chars) for x in range(size))


def parse_jsonp(jsonp_str):
    try:
        return re.search(r"^[^(]*?\((.*)\)[^)]*$", jsonp_str).group(1)
    except Exception:
        raise ValueError("无效数据！")
