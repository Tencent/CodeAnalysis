# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

'''
节点异常类定义
'''


from util.errcode import E_NODE_TASK_BUILD, E_NODE_TASK_ANALYZE, \
    E_NODE_TASK_DATAHANDLE, E_NODE_TASK_FORMAT, E_NODE_TASK_BLAME, E_NODE_TASK_FILTER, E_NODE_TASK_SOURCE, \
    E_NODE_TASK_TRANSFER, E_NODE_REQUESTS_API, E_NODE_TASK_RESFULAPI, E_NODE_FILE_SERVER, E_NODE_ZIP, \
    E_NODE_Input_Retry, E_NODE_TASK_CONFIG, E_NODE_CONFIG


class NodeError(Exception):
    """
    节点异常错误类型。节点遇到异常时，需要抛出NodeError，指定code, msg和data::
    
        raise NodeError(200, u"node error msg", u"其他补充详细信息")    
    """
    def __init__(self, code, msg, data = None):
        """
        :param code: 异常代码
        :param msg: 异常消息
        :param data: 详细信息
        """
        self.code = code
        self.msg = msg
        self.data = data
    
    def __str__(self):
        return "Error[%d]: %s" % (self.code, self.msg) # python3 中不需要unicode

class TaskError(NodeError):
    """
        try:
    
    任务的异常错误类型。任务遇到异常时，需要抛出TaskError，指定code， msg和data::
    
        raise TaskError(201, u"task error msg", u"其他补充详细信息")
        
    """
    
    pass
	
class ScmClientError(NodeError):
    """
        try:
    
    任务的异常错误类型。任务遇到异常时，需要抛出TaskError，指定code， msg和data::
    
        raise TaskError(201, u"task error msg", u"其他补充详细信息")
        
    """
    pass

# 实现具体的错误类型，用于调用时不用引用两处代码：错误类型+错误码
class CompileTaskError(NodeError):
    def __init__(self, msg):
        NodeError.__init__(self, E_NODE_TASK_BUILD, msg)

class AnalyzeTaskError(NodeError):
    def __init__(self, msg):
        NodeError.__init__(self, E_NODE_TASK_ANALYZE, msg)

class DataHandleTaskError(NodeError):
    def __init__(self, msg):
        NodeError.__init__(self, E_NODE_TASK_DATAHANDLE, msg)

class TaskFormatError(NodeError):
    def __init__(self, msg):
        NodeError.__init__(self, E_NODE_TASK_FORMAT, msg)

class TaskBlameError(NodeError):
    def __init__(self, msg):
        NodeError.__init__(self, E_NODE_TASK_BLAME, msg)

class TaskFilterError(NodeError):
    def __init__(self, msg):
        NodeError.__init__(self, E_NODE_TASK_FILTER, msg)

class SourceMgrError(NodeError):
    def __init__(self, msg):
        NodeError.__init__(self, E_NODE_TASK_SOURCE, msg)

class TransferModuleError(NodeError):
    def __init__(self, msg):
        NodeError.__init__(self, E_NODE_TASK_TRANSFER, msg)

class RequestsApiError(NodeError):
    def __init__(self, msg):
        NodeError.__init__(self, E_NODE_REQUESTS_API, msg)

class ResfulApiError(NodeError):
    def __init__(self, msg):
        NodeError.__init__(self, E_NODE_TASK_RESFULAPI, msg)

class FileServerError(NodeError):
    def __init__(self, msg):
        NodeError.__init__(self, E_NODE_FILE_SERVER, msg)

class ZIPError(NodeError):
    def __init__(self, msg):
        NodeError.__init__(self, E_NODE_ZIP, msg)

class InputRetryError(NodeError):
    def __init__(self, msg):
        NodeError.__init__(self, E_NODE_Input_Retry, msg)

class ConfigError(NodeError):
    def __init__(self, msg):
        NodeError.__init__(self, E_NODE_TASK_CONFIG, msg)

class NodeConfigError(NodeError):
    def __init__(self, msg):
        NodeError.__init__(self, E_NODE_CONFIG, msg)


