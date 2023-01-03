# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

# cppcheck2.6版本启动器
#                                  __                    __        _____   
#                                 [  |                  [  |  _   / ___ `. 
#  .---.  _ .--.   _ .--.   .---.  | |--.  .---.  .---.  | | / ] |_/___) | 
# / /'`\][ '/'`\ \[ '/'`\ \/ /'`\] | .-. |/ /__\\/ /'`\] | '' <   .'____.' 
# | \__.  | \__/ | | \__/ || \__.  | | | || \__.,| \__.  | |`\ \ / /_____  
# '.___.' | ;.__/  | ;.__/ '.___.'[___]|__]'.__.''.___.'[__|  \_]|_______| 
#        [__|     [__|                                                     

import os

from tool.cppcheck import Cppcheck


class CppCheck2(Cppcheck):

    def __init__(self, params):
        cppcheck2_home = os.environ.get("CPPCHECK2_HOME")
        os.environ["CPPCHECK_HOME"] = cppcheck2_home
        super().__init__(params)


tool = CppCheck2

if __name__ == '__main__':
    pass
