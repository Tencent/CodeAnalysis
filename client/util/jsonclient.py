# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
Json处理类
"""



import sys
import json
import logging


logger = logging.getLogger(__name__)


class JsonClient(object):
    @staticmethod
    def dump(data, file_path):
        """

        :param data:
        :param file_path:
        :return:
        """
        if sys.version_info.major == 2:
            # python2兼容
            with open(file_path, "w") as fp:
                json.dump(data, fp, indent=2, ensure_ascii=False)
        else:
            # python3兼容
            with open(file_path, "wb") as fp:
                fp.write(str.encode(json.dumps(data, indent=2, ensure_ascii=False)))

    @staticmethod
    def load(file_path):
        """

        :param file_path:
        :return:
        """
        if sys.version_info.major == 2:
            # python2兼容
            with open(file_path, 'r') as rf:
                result_json = json.load(rf)
                for key, value in result_json.items():
                    if isinstance(value, unicode):
                        result_json[key] = value.encode('utf-8')
        else:
            # python3兼容
            with open(file_path, 'r', encoding="utf-8") as rf:
                result_json = json.load(rf)

        return result_json
