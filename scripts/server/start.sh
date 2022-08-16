#!/bin/bash

CURRENT_SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")";pwd)
TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$(cd $(dirname $CURRENT_SCRIPT_PATH); pwd)"}

source $TCA_SCRIPT_ROOT/utils.sh
source $TCA_SCRIPT_ROOT/server/_base.sh
source $TCA_SCRIPT_ROOT/server/stop.sh


function start_main() {
    LOG_INFO "start main server, worker and beat"
    cd $TCA_SERVER_MAIN_PATH
    gunicorn codedog.wsgi -c $TCA_MAIN_GUNICORN_CONF_FILE
    nohup celery -A codedog worker -l DEBUG --logfile $TCA_MAIN_CELERY_WORKER_LOG  --pidfile $TCA_MAIN_CELERY_WORKER_PID_FILE 2>worker_error.out &
    nohup celery -A codedog beat -S redbeat.RedBeatScheduler -l DEBUG --logfile $TCA_MAIN_CELERY_BEAT_LOG --pidfile $TCA_MAIN_CELERY_BEAT_PID_FILE 2>beat_error.out &
}

function restart_main() {
    stop_main_server
    stop_main_worker
    stop_main_beat
    start_main
}

function start_analysis() {
    LOG_INFO "start analysis server and worker"
    cd $TCA_SERVER_ANALYSIS_PATH
    gunicorn codedog.wsgi -c $TCA_ANALYSIS_GUNICORN_CONF_FILE
    nohup celery -A codedog worker -l DEBUG --logfile $TCA_ANALYSIS_CELERY_WORKER_LOG  --pidfile $TCA_ANALYSIS_CELERY_WORKER_PID_FILE 2>worker_error.out &
}

function restart_analysis() {
    stop_analysis_server
    stop_analysis_worker
    start_analysis
}

function start_file() {
    LOG_INFO "start file server"
    cd $TCA_SERVER_FILE_PATH
    gunicorn codedog_file_server.wsgi -c $TCA_FILE_GUNICORN_CONF_FILE
}

function restart_file() {
    stop_file_server
    start_file
}

function start_login() {
    LOG_INFO "start login server"
    cd $TCA_SERVER_LOGIN_PATH
    gunicorn apps.wsgi -c $TCA_LOGIN_GUNICORN_CONF_FILE
}

function restart_login() {
    stop_login_server
    start_login
}

function start_scmproxy() {
    LOG_INFO "start scmproxy server"
    cd $TCA_SERVER_SCMPROXY_PATH
    nohup python proxyserver.py 1>proxy_start.out 2>proxy_error.out &
}

function restart_scmproxy() {
    stop_scmproxy_server
    start_scmproxy
}

function start_nginx() {
    LOG_INFO "start nginx"
     nginx_is_start=$(ps -C nginx --no-header | wc -l)
    if [ $nginx_is_start -eq 0 ]; then
        nginx -t || error_exit "nginx test failed"
        nginx
    else
        nginx -s reload
    fi
}

function start_tca_server() {
    stop_tca_server
    start_main
    start_analysis
    start_file
    start_login
    start_scmproxy
    start_nginx
}
