# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""gunicorn配置文件
"""
import os

project_path = os.path.dirname(os.path.abspath(__file__))
host = os.environ.get("MAIN_SERVER_HOST", "0.0.0.0")
port = os.environ.get("MAIN_SERVER_PORT", 8001)
bind = "%s:%s" % (host, port)
backlog = 2048
chdir = project_path
pidfile = os.path.join(project_path, "main-master.pid")
daemon = os.environ.get("DAEMON", "true") == "true"
proc_name = "main"

workers = os.environ.get("MAIN_SERVER_PROCESS_NUM", 8)
threads = 2
max_requests = 5000
loglevel = "info"
access_log_format = "%(t)s %(p)s %(h)s '%(r)s' %(s)s %(L)s %(b)s %(f)s' '%(a)s'"
accesslog = os.environ.get("SERVER_ACCESS_LOG", os.path.join(project_path, "log/gunicorn_access.log"))
errorlog = os.environ.get("SERVER_ERROR_LOG", os.path.join(project_path, "log/gunicorn_error.log"))
