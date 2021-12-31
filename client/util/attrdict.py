# -*- encoding: utf-8 -*-
"""task utility module"""

import logging

logger = logging.getLogger(__name__)


class AttrDict(dict):
    """
    a dict that can access item by attribute. i.e. ``foo['item'] ==foo.item``
    """
    def __init__(self, *args, **kw):
        dict.__init__(self, *args, **kw)

    def __getattr__(self, key):
        value = self[key]
        if isinstance(value, AttrDict):
            return value
        elif isinstance(value, dict):
            adict = AttrDict(value)
            self[key] = adict
            return adict
        else:
            return value

    def __setattr__(self, key, value):
        self[key] = value
