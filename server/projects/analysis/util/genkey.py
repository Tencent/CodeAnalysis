# -*- coding: utf-8 -*-
"""
Key generation
"""
import hashlib


def gen_path_key(path):
    """generate key for file path
    """
    path = path.encode("utf-8")
    return hashlib.sha1(path).hexdigest()
