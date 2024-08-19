# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""gunicorn配置文件
"""
import os


def on_starting(server):
    if os.environ.get('MY_PROMETHEUS_MULTIPROC_DIR', None):
        os.environ['PROMETHEUS_MULTIPROC_DIR'] = os.environ.get('MY_PROMETHEUS_MULTIPROC_DIR')
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        multiproc_dir = os.environ.get('PROMETHEUS_MULTIPROC_DIR')

        try:
            if not os.path.exists(multiproc_dir):
                os.makedirs(multiproc_dir)
        except Exception:
            os.environ['PROMETHEUS_MULTIPROC_DIR'] = BASE_DIR


def post_fork(server, worker):
    if os.environ.get('MY_PROMETHEUS_MULTIPROC_DIR', None):
        try:
            from prometheus_client import values
            values.ValueClass = values.MultiProcessValue(os.getpid)
        except ImportError:
            pass


def child_exit(server, worker):
    if os.environ.get('MY_PROMETHEUS_MULTIPROC_DIR', None):
        mark_all_process_dead(worker.pid)


def mark_all_process_dead(pid, path=None):
    if path is None:
        path = os.environ.get('PROMETHEUS_MULTIPROC_DIR')

    try:
        from prometheus_client import Gauge
        import glob
        for mode in Gauge._MULTIPROC_MODES:
            for f in glob.glob(os.path.join(path, f'gauge_{mode}_{pid}.db')):
                os.remove(f)
    except ImportError:
        pass

    try:
        os.remove(os.path.join(path, f'counter_{pid}.db'))
        os.remove(os.path.join(path, f'histogram_{pid}.db'))
    except Exception:
        pass


project_path = os.path.dirname(os.path.abspath(__file__))
host = os.environ.get("LOGIN_SERVER_HOST", "0.0.0.0")
port = os.environ.get("LOGIN_SERVER_PORT", 8003)
bind = "%s:%s" % (host, port)
backlog = 2048
chdir = project_path
pidfile = os.path.join(project_path, "login-master.pid")
daemon = os.environ.get("DAEMON", "true") == "true"  # 默认后台运行
proc_name = "login"

workers = os.environ.get("LOGIN_SERVER_PROCESS_NUM", 8)
threads = 2
max_requests = 5000
loglevel = "info"
access_log_format = "%(t)s %(p)s %(h)s '%(r)s' %(s)s %(L)s %(b)s %(f)s' '%(a)s'"
accesslog = os.environ.get("SERVER_ACCESS_LOG", os.path.join(project_path, "log/gunicorn_access.log"))
errorlog = os.environ.get("SERVER_ERROR_LOG", os.path.join(project_path, "log/gunicorn_error.log"))
