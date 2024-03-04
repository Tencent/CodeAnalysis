# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""拉取quickscan git仓库
"""

import os
import logging

from node.app import settings
from node.toolloader.gitload import GitLoader

logger = logging.getLogger(__name__)


class QuickScanConfigLoader(object):
    @staticmethod
    def load_config():
        git_url = "https://github.com/TCATools/quickscan.git"
        logger.info("load quickscan task config: %s" % git_url)
        src_dir = os.path.join(settings.TOOL_BASE_DIR, 'quickscan')
        GitLoader(scm_url=git_url, dest_dir=src_dir, print_enable=False).load()


if __name__ == '__main__':
    QuickScanConfigLoader.load_config()
