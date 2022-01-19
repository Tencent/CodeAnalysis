# -*- encoding=utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
压缩和解压缩模块
"""


import os
import logging
import zipfile

logger = logging.getLogger(__name__)

class ZipMgr(object):
    def zip_dir(self, dir_path, zip_filepath):
        """
        压缩目录,也支持压缩单个文件
        :param dir_path: 目录路径,或单个文件路径
        :param zip_filepath: 压缩后的文件路径
        :return: 压缩后的文件路径
        """
        dir_path = os.path.realpath(dir_path)
        zip_filepath = os.path.realpath(zip_filepath)

        filelist = []
        if os.path.isfile(dir_path):
            filelist.append(dir_path)
        else :
            for root, dirs, files in os.walk(dir_path):
                for name in files:
                    filelist.append(os.path.join(root, name))

        zf = zipfile.ZipFile(zip_filepath, "w", zipfile.zlib.DEFLATED)
        pre_len = len(os.path.dirname(dir_path))
        for tar in filelist:
            arcname = tar[pre_len:].strip(os.path.sep)
            zf.write(tar,arcname)
        zf.close()
        return zip_filepath


    def unzip_file(self, zip_filepath, unzip_to_dir):
        """
        加压缩到指定目录
        :param zip_filepath: 压缩文件
        :param unzip_to_dir: 解压缩后的目录路径
        :return: 解压缩后的目录路径
        """
        zip_filepath = os.path.realpath(zip_filepath)
        unzip_to_dir = os.path.realpath(unzip_to_dir)
        if not os.path.exists(unzip_to_dir):
            os.mkdir(unzip_to_dir)
        zfobj = zipfile.ZipFile(zip_filepath)
        for name in zfobj.namelist():
            name = name.replace(os.sep,'/')

            if name.endswith('/'):
                os.mkdir(os.path.join(unzip_to_dir, name))
            else:
                ext_filename = os.path.join(unzip_to_dir, name)
                ext_dir= os.path.dirname(ext_filename)
                if not os.path.exists(ext_dir) :
                    os.mkdir(ext_dir)
                outfile = open(ext_filename, 'wb')
                outfile.write(zfobj.read(name))
                outfile.close()
        return unzip_to_dir

if __name__ == '__main__':
    pass
