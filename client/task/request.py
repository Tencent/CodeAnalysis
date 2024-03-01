# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
each task have a request object, which is get from server. request object contains task information, 
and task hooks may put more data into the request object.
"""

from util.attrdict import AttrDict


class TaskRequest(AttrDict):
    """Task request is a dict alike object, which contains task information. task request contains
    at lease below fields.

    ``tid``
        the task id

    ``task_name``
        the task module name in taskapps package

    ``task_params``
        task parameters

    ``files``
        those files will put into the work_dir before calling task procedure.
        this is a iterable object with each item is a file or a directory

    ``task_version``
        task version

    ``task_dir``
        task directory

    ``work_dir``
        task working directory

    """

    pass
