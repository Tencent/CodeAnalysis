#!/bin/bash

CURRENT_SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")";pwd)
TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$(cd $(dirname $CURRENT_SCRIPT_PATH); pwd)"}

source $TCA_SCRIPT_ROOT/utils.sh
source $TCA_SCRIPT_ROOT/server/_base.sh

function check_result() {
    name=$1
    ret=$2
    if [ "$ret" = "true" ]; then
        LOG_INFO "$name: OK."
        return 0
    else
        LOG_ERROR "$name run failed."
        return 1
    fi
}

function check_main_server() {
    main_server_result=$( check_target_process_exist "main.gunicorn.conf.py")
    if [ "$main_server_result" = "true" ]; then
        return 0
    else
        return 1
    fi
}

function check_main_worker() {
    main_worker_result=$( check_target_process_exist "main_celery_worker.pid")
    if [ "$main_worker_result" = "true" ]; then
        return 0
    else
        return 1
    fi
}

function get_main_worker_log() {
    LOG_INFO "Check main worker log"
    worker_log=$( tail -n 100 $TCA_SERVER_MAIN_PATH/log/celery.log )
    LOG_INFO "$worker_log"
}

function get_main_worker_error_log() {
    LOG_WARN "Check main worker error log"
    error_log=$( tail -n 100 $TCA_SERVER_MAIN_PATH/worker_error.out )
    LOG_WARN "$error_log"
}

function check_main_beat() {
    main_beat_result=$( check_target_process_exist "main_celery_beat.pid")
    if [ "$main_beat_result" = "true" ]; then
        return 0
    else
        return 1
    fi
}

function get_main_beat_log() {
    LOG_INFO "Check main beat log"
    beat_log=$( tail -n 100 $TCA_SERVER_MAIN_PATH/log/celery.log )
    LOG_INFO "$beat_log"
}

function get_main_beat_error_log() {
    LOG_WARN "Check main beat error log"
    error_log=$( tail -n 100 $TCA_SERVER_MAIN_PATH/beat_error.out )
    LOG_WARN "$error_log"
}

function check_analysis_server() {
    analysis_server_result=$( check_target_process_exist "analysis.gunicorn.conf.py")
    if [ "$analysis_server_result" = "true" ]; then
        return 0
    else
        return 1
    fi
}

function check_analysis_worker() {
    analysis_worker_result=$( check_target_process_exist "analysis_celery_worker.pid")
    if [ "$analysis_worker_result" = "true" ]; then
        return 0
    else
        return 1
    fi
}

function get_analysis_worker_error_log() {
    LOG_WARN "Check analysis beat error log"
    error_log=$( tail -n 100 $TCA_SERVER_ANALYSIS_PATH/worker_error.out )
    LOG_WARN "$error_log"
}

function check_login_server() {
    login_server_result=$( check_target_process_exist "login.gunicorn.conf.py")
    if [ "$login_server_result" = "true" ]; then
        return 0
    else
        return 1
    fi
}

function check_file_server() {
    file_server_result=$( check_target_process_exist "file.gunicorn.conf.py")
    if [ "$file_server_result" = "true" ]; then
        return 0
    else
        return 1
    fi
}

function check_scmproxy_server() {
    scmproxy_result=$( check_target_process_exist "proxyserver.py")
    if [ "$scmproxy_result" = "true" ]; then
        return 0
    else
        return 1
    fi
}

function check_nginx() {
    nginx_result=$( check_target_process_exist "nginx")
    if [ "$nginx_result" = "true" ]; then
        return 0
    else
        return 1
    fi
}

function check_tca_local_status() {
    main_server_result=""
    main_worker_result=""
    main_beat_result=""
    analysis_server_result=""
    analysis_worker_result=""
    login_server_result=""
    file_server_result=""
    scmproxy_result=""
    nginx_result=""

    check_main_server
    check_result "tca_main_server" "$main_server_result"
    check_analysis_server
    check_result "tca_analysis_server" "$analysis_server_result"
    check_login_server
    check_result "tca_login_server" "$login_server_result"
    check_file_server
    check_result "tca_file_server" "$file_server_result"

    check_main_worker
    check_result "tca_main_worker" "$main_worker_result" || get_main_worker_error_log
    check_main_beat
    check_result "tca_main_beat" "$main_beat_result" || get_main_beat_error_log
    check_analysis_worker
    check_result "tca_analysis_worker" "$analysis_worker_result" || get_analysis_worker_error_log
    check_nginx
    check_result "tca_nginx" "$nginx_result"
}

function get_tca_local_log() {
    LOG_INFO "tca main server log      : "$TCA_MAIN_SERVER_LOG
    LOG_INFO "tca main worker log      : "$TCA_MAIN_CELERY_WORKER_LOG
    LOG_INFO "tca main beat log        : "$TCA_MAIN_CELERY_BEAT_LOG
    LOG_INFO "tca analysis server log  : "$TCA_ANALYSIS_SERVER_LOG
    LOG_INFO "tca analysis worker log  : "$TCA_ANALYSIS_CELERY_WORKER_LOG
    LOG_INFO "tca file server log      : "$TCA_FILE_SERVER_LOG
    LOG_INFO "tca login server log     : "$TCA_LOGIN_SERVER_LOG
    LOG_INFO "tca scmproxy server log  : "$TCA_SCMPROXY_SERVER_LOG
}