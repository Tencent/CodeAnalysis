#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
JVM Proxy:
JVM不会复用http_proxy等配置，需要进行转换。
"""

import os
import re


class JVMProxy(object):
    @staticmethod
    def get_proxy_args():
        """
        解析代理环境变量
        """
        proxy_args = []
        pattern = re.compile(r"https?://((.*):(.*)@)?(.*):(\d+)")

        # 解析http_proxy
        http_proxy = os.environ.get("HTTP_PROXY")
        if http_proxy is None:
            http_proxy = os.environ.get("http_proxy")
        if http_proxy is not None:
            match = pattern.match(http_proxy)
            if match:
                if match.group(1):
                    proxy_args.append(f"-Dhttp.proxyUser={match.group(2)}")
                    proxy_args.append(f"-Dhttp.proxyPassword={match.group(3)}")
                proxy_args.append(f"-Dhttp.proxyHost={match.group(4)}")
                proxy_args.append(f"-Dhttp.proxyPort={match.group(5)}")

        https_proxy = os.environ.get("HTTPS_PROXY")
        if https_proxy is None:
            https_proxy = os.environ.get("https_proxy")
        if https_proxy is not None:
            match = pattern.match(https_proxy)
            if match:
                if match.group(1):
                    proxy_args.append(f"-Dhttps.proxyUser={match.group(2)}")
                    proxy_args.append(f"-Dhttps.proxyPassword={match.group(3)}")
                proxy_args.append(f"-Dhttps.proxyHost={match.group(4)}")
                proxy_args.append(f"-Dhttps.proxyPort={match.group(5)}")

        return proxy_args


if __name__ == "__main__":
    pass
