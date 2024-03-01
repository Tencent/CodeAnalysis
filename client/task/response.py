# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

'''
each task has a response object, which is used to send back task result to server.
'''
from util.attrdict import AttrDict
from util import errcode
from task.toolmodel import IToolModel


class TaskResponse(AttrDict):
    '''Task response contains below fields.
    
    ``task_version``
        task version
    
    ``status``
        task status code
        
    ``result``
        task result data
        
    ``message``
        task error message, default is None if no error
        
    ``files``
        file list with each item be a file or a directory path relative to work_dir. 
        those file will upload to file server
    '''

    def __init__(self, task_version=IToolModel.version, status=errcode.OK, message=None, result=None, files=None):
        self.task_version = task_version
        self.status = status
        self.message = message
        self.result = result
        self.files = files
