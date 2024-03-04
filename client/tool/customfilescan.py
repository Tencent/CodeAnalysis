# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""自定义规则工具，应用自定义规则扫描, 适用于文件结果的自定义规则(问题定位到文件,责任人通过文件最后修改人获取)
"""


from tool.customscan import CustomScan
from task.basic.datahandler.blamer import FILE_LAST_CHANGE_BLAME
from util.logutil import LogPrinter

logger = LogPrinter


class CustomFileScan(CustomScan):
    """
    文件型自定义规则扫描工具,继承自CustomScan
    """
    def set_blame_type(self):
        '''
        通过覆盖该函数来选择blame类型
        目前存在blame类型有：
        1. NO_BLAME 不需要blame
        2. NORMAL_BLAME 常规blame
        3. FILE_LAST_CHANGE_BLAME 将文件最后一个修改人作为责任人
        由于blame类型互斥，所以既能返回一个值
        :return:
        '''
        return FILE_LAST_CHANGE_BLAME


tool = CustomFileScan

if __name__ == '__main__':
    pass
