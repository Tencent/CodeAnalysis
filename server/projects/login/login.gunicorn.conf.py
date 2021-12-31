# -*- coding: utf-8 -*-
"""gunicorn配置文件
"""
import logging
import logging.handlers
from logging.handlers import WatchedFileHandler
import os
import multiprocessing

project_path = os.path.dirname(os.path.abspath(__file__))
bind = "0.0.0.0:8003"
backlog = 2048
chdir = project_path
pidfile = os.path.join(project_path, "login-master.pid")
daemon = os.environ.get("DAEMON", "true") == "true"  # 默认后台运行
proc_name = "login"

workers = 8
threads = 2
max_requests = 5000
loglevel = "info"
access_log_format = "%(t)s %(p)s %(h)s '%(r)s' %(s)s %(L)s %(b)s %(f)s' '%(a)s'"
accesslog = os.environ.get("SERVER_ACCESS_LOG", os.path.join(project_path, "log/gunicorn_access.log"))
errorlog = os.environ.get("SERVER_ERROR_LOG", os.path.join(project_path, "log/gunicorn_error.log"))
