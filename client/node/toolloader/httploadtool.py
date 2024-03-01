# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
通过http方式拉取工具
"""

import os

from util.logutil import LogPrinter
from util.api.fileserver import RetryFileServer
from util.exceptions import FileServerError
from util.pathlib import PathMgr
from util.zipmgr import Zip


class HttpToolLoader(object):
    """通过http方式拉取工具，如果目录已存在，不拉取"""
    @staticmethod
    def download_tool(tool_url, dest_dir):
        if os.path.exists(dest_dir):
            # 工具目录存在时，直接复用，不重新拉取（如需更新，先删除工具目录）
            LogPrinter.debug(f"tool dir({os.path.basename(dest_dir)}) from zip can be reused.")
            return

        tool_root_dir = os.path.dirname(dest_dir)
        if not os.path.exists(tool_root_dir):  # 如果上层目录不存在,先创建
            os.makedirs(tool_root_dir)
        zip_file_name = tool_url.split('/')[-1]
        dest_zip_file_path = os.path.join(tool_root_dir, zip_file_name)

        file_server = RetryFileServer(retry_times=2).get_server(server_url=tool_url)
        file_server.download_big_file("", dest_zip_file_path)

        if os.path.exists(dest_zip_file_path):
            LogPrinter.debug(f"download {tool_url} to {dest_zip_file_path}")
            # 使用7z解压
            Zip().decompress_by_7z(dest_zip_file_path, tool_root_dir)
            LogPrinter.debug(f"unzip {dest_zip_file_path} to {dest_dir}")
            PathMgr().safe_rmpath(dest_zip_file_path)
        else:
            raise FileServerError(f"download {tool_url} failed!")


if __name__ == '__main__':
    pass
