#!/bin/bash

CURRENT_SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")";pwd)
TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$(cd $(dirname $CURRENT_SCRIPT_PATH); pwd)"}

source $TCA_SCRIPT_ROOT/utils.sh
source $TCA_SCRIPT_ROOT/server/_base.sh

function stop_main_server() {
    LOG_INFO "stop tca main server"
    kill_by_pid_file "$TCA_MAIN_GUNICORN_PID_FILE"
    force_kill "main.gunicorn.conf.py"
}

function stop_analysis_server() {
    LOG_INFO "stop tca analysis server"
    kill_by_pid_file "$TCA_ANALYSIS_GUNICORN_PID_FILE"
    force_kill "analysis.gunicorn.conf.py"
}

function stop_login_server() {
    LOG_INFO "stop tca login server"
    kill_by_pid_file "$TCA_LOGIN_GUNICORN_PID_FILE"
    force_kill "login.gunicorn.conf.py"
}

function stop_file_server() {
    LOG_INFO "stop tca file server"
    kill_by_pid_file "$TCA_FILE_GUNICORN_PID_FILE"
    force_kill "file.gunicorn.conf.py"
}

function stop_scmproxy_server() {
    LOG_INFO "stop tca scmproxy server"
    force_kill "proxyserver.py"
}

function stop_main_worker() {
    LOG_INFO "stop tca main worker and beat"
    kill_by_pid_file "$TCA_MAIN_CELERY_WORKER_PID_FILE"
    kill_by_pid_file "$TCA_MAIN_CELERY_BEAT_PID_FILE"
    force_kill "main_celery_worker.pid"
    force_kill "main_celery_beat.pid"
}

function stop_analysis_worker() {
    LOG_INFO "stop tca analysis worker"
    kill_by_pid_file "$TCA_ANALYSIS_CELERY_WORKER_PID_FILE"
    force_kill "analysis_celery_worker.pid"
}

function stop_nginx() {
    LOG_INFO "stop tca nginx"
    nginx -s stop >/dev/null 2>&1
    force_kill "nginx"
}

function stop_tca_server() {
    LOG_INFO "stop all tca services"
    stop_main_server
    stop_analysis_server
    stop_login_server
    stop_file_server
    stop_scmproxy_server
    stop_main_worker
    stop_analysis_worker
    stop_nginx
}
