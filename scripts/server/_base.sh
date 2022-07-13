#!/bin/bash

# system base
export PYTHON_PATH=${PYTHON_PATH:-"/usr/local/python3/bin"}

# server path
CURRENT_SCRIPT_PATH=$( cd "$(dirname ${BASH_SOURCE[0]})"; pwd )
export TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$( cd $(dirname $CURRENT_SCRIPT_PATH); pwd )"}
export TCA_PROJECT_PATH=${TCA_PROJECT_PATH:-"$( cd $(dirname $TCA_SCRIPT_ROOT); pwd )"}
export TCA_SERVER_PATH=$TCA_PROJECT_PATH/server
export TCA_SERVER_TMP_PATH=$TCA_SERVER_PATH/tmp
export TCA_SERVER_LOG_PATH=$TCA_SERVER_PATH/logs
export TCA_SERVER_CONFIG_PATH=$TCA_SERVER_PATH/configs
export TCA_SERVER_MAIN_PATH=$TCA_SERVER_PATH/projects/main
export TCA_SERVER_ANALYSIS_PATH=$TCA_SERVER_PATH/projects/analysis
export TCA_SERVER_LOGIN_PATH=$TCA_SERVER_PATH/projects/login
export TCA_SERVER_FILE_PATH=$TCA_SERVER_PATH/projects/file
export TCA_SERVER_SCMPROXY_PATH=$TCA_SERVER_PATH/projects/scmproxy

# pid and conf file
export TCA_MAIN_GUNICORN_PID_FILE=$TCA_SERVER_MAIN_PATH/main-master.pid
export TCA_MAIN_GUNICORN_CONF_FILE=$TCA_SERVER_MAIN_PATH/main.gunicorn.conf.py
export TCA_ANALYSIS_GUNICORN_PID_FILE=$TCA_SERVER_ANALYSIS_PATH/analysis-master.pid
export TCA_ANALYSIS_GUNICORN_CONF_FILE=$TCA_SERVER_ANALYSIS_PATH/analysis.gunicorn.conf.py
export TCA_LOGIN_GUNICORN_PID_FILE=$TCA_SERVER_LOGIN_PATH/login-master.pid
export TCA_LOGIN_GUNICORN_CONF_FILE=$TCA_SERVER_LOGIN_PATH/login.gunicorn.conf.py
export TCA_FILE_GUNICORN_PID_FILE=$TCA_SERVER_FILE_PATH/file-master.pid
export TCA_FILE_GUNICORN_CONF_FILE=$TCA_SERVER_FILE_PATH/file.gunicorn.conf.py
export TCA_MAIN_CELERY_WORKER_PID_FILE=$TCA_SERVER_TMP_PATH/main_celery_worker.pid
export TCA_MAIN_CELERY_BEAT_PID_FILE=$TCA_SERVER_TMP_PATH/main_celery_beat.pid
export TCA_ANALYSIS_CELERY_WORKER_PID_FILE=$TCA_SERVER_TMP_PATH/analysis_celery_worker.pid

# log file
export TCA_MAIN_SERVER_LOG=$TCA_SERVER_MAIN_PATH/log/codedog.log
export TCA_MAIN_SERVER_ERROR_LOG=$TCA_SERVER_MAIN_PATH/log/codedog_error.log
export TCA_MAIN_CELERY_WORKER_LOG=$TCA_SERVER_MAIN_PATH/log/main_celery.log
export TCA_MAIN_CELERY_BEAT_LOG=$TCA_SERVER_MAIN_PATH/log/main_beat.log
export TCA_ANALYSIS_SERVER_LOG=$TCA_SERVER_ANALYSIS_PATH/log/codedog.log
export TCA_ANALYSIS_SERVER_ERROR_LOG=$TCA_SERVER_ANALYSIS_PATH/log/codedog_error.log
export TCA_ANALYSIS_CELERY_WORKER_LOG=$TCA_SERVER_ANALYSIS_PATH/log/analysis_celery.log
export TCA_LOGIN_SERVER_LOG=$TCA_SERVER_LOGIN_PATH/log/codedog.log
export TCA_FILE_SERVER_LOG=$TCA_SERVER_FILE_PATH/log/codedog_file.log
export TCA_FILE_SERVER_ERROR_LOG=$TCA_SERVER_FILE_PATH/log/codedog_error_file.log
export TCA_SCMPROXY_SERVER_LOG=$TCA_SERVER_SCMPROXY_PATH/logs/scmproxy.log
