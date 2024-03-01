# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
application的配置使用如下。

* 使用 :py:data:`settings` 模块变量访问配置项目::
   
     from node import app
     sourcedir = app.settings.SOURCE_DIR

application的持久化数据使用如下:

* 使用 :py:data:`persist_data` 模块变量存取持久化数据。
  这是一个类dict的变量，使用json格式序列化到文件中，因此要保证使用的数据可以被json序列化。
* 数据存取如下::

      from util import app
        
      #data get saved persist
      app.persist_data['NODE_ID'] = 123
      
      #access persist data
      node_id = app.persist_data['NODE_ID']
"""

import importlib
import json
import os
import os.path

from settings.settingtype import SettingType, LocalSetting


class Settings(object):
    def __init__(self):
        self._settings_module = None

    def __getattr__(self, name):
        if not self._settings_module:
            mod_name = SettingType().get_env()
            self._settings_module = importlib.import_module(mod_name)
            # 将本地配置更新到settings模块中
            LocalSetting().add_local_setting(self._settings_module)
        return getattr(self._settings_module, name)


settings = Settings()
'全局设置'


class PersistData(object):
    def __init__(self):
        self._data = {}
        
    def _get_data_file(self):
        data_dir = os.getenv("TCA_APP_DATA_DIR")  # 支持通过环境变量指定app数据目录，存放节点NODE_UUID唯一值
        if data_dir:
            data_dir = os.path.abspath(data_dir)
        else:
            data_dir = os.path.join(settings.BASE_DIR, '.appdata')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        return os.path.join(data_dir, 'appdata.json')
    
    def _load_data(self):
        if not self._data:
            datafile = self._get_data_file()
            if os.path.exists(datafile):
                with open(self._get_data_file(), 'r') as f:
                    self._data = json.load(f)
                    
    def __getitem__(self, key):
        self._load_data()
        return self._data[key]
    
    def __setitem__(self, key, value):
        self._data[key] = value
        datafile = self._get_data_file()
        with open(datafile, 'w') as f:
            json.dump(self._data, f)
            
    def get(self, key, default=None):
        self._load_data()
        return self._data.get(key, default)


persist_data = PersistData()
'应用的持久化数据存取'
