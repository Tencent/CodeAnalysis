#!/bin/bash
# 启动 TCA Web 与 Server服务

CURRENT_SCRIPT_PATH=$( cd "$(dirname ${BASH_SOURCE[0]})"; pwd )
export TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$( cd $(dirname $CURRENT_SCRIPT_PATH); pwd )"}

source $TCA_SCRIPT_ROOT/utils.sh
source $TCA_SCRIPT_ROOT/config.sh
source $TCA_SCRIPT_ROOT/base/install_python.sh
source $TCA_SCRIPT_ROOT/base/install_db.sh
source $TCA_SCRIPT_ROOT/base/install_nginx.sh
source $TCA_SCRIPT_ROOT/server/init_config.sh
source $TCA_SCRIPT_ROOT/server/init_data.sh
source $TCA_SCRIPT_ROOT/web/init.sh
source $TCA_SCRIPT_ROOT/server/start.sh
source $TCA_SCRIPT_ROOT/server/stop.sh
source $TCA_SCRIPT_ROOT/server/healthcheck.sh


function tca_local_install() {
    LOG_INFO "1. install base software: Python/Redis/Mariadb(or MySQL)/Nginx"
    interactive_install_python
    interactive_install_redis
    interactive_install_mariadb
    interactive_install_nginx

    LOG_INFO "2. init tca server config"
    init_server_config
    init_server_db_and_data

    LOG_INFO "3. init tca web config"
    init_web_config
}

function tca_local_start() {
    LOG_INFO "start tca server"
    service=$1
    case "$service" in
        main)
            restart_main
        ;;
        analysis)
            restart_analysis
        ;;
        file)
            restart_file
        ;;
        login)
            restart_login
        ;;
        scmproxy)
            restart_scmproxy
        ;;
        nginx)
            start_nginx
        ;;
        *)
            start_tca_server
        ;;
    esac
}

function tca_local_stop() {
    service=$1
    case "$service" in
        main)
            stop_main_server
            stop_main_worker
        ;;
        analysis)
            stop_analysis_server
            stop_analysis_worker
        ;;
        file)
            stop_file_server
        ;;
        login)
            stop_login_server
        ;;
        scmproxy)
            stop_scmproxy_server
        ;;
        nginx)
            stop_nginx
        ;;
        *)
            stop_tca_server
        ;;
    esac
}

function tca_local_help() {
    LOG_INFO "Support command:"
    LOG_INFO "1. deploy : install base sofeware(Python/MySQL/Redis/Nginx), init tca server&web and start all service status"
    LOG_INFO "2. install: install base sofeware(Python/MySQL/Redis/Nginx) and init tca server&web"
    LOG_INFO "3. start  : start service, params: main/analysis/file/login/scmproxy/nginx/all"
    LOG_INFO "4. stop   : stop service, params: main/analysis/file/login/scmproxy/nginx/all"
    LOG_INFO "5. check  : check all serivces status."
    LOG_INFO "6. log    : print all serivces log path."
    LOG_INFO "7. help   : print script document."

}

function tca_local_main() {
    pre_check
    command=$1
    service=$2
    # command: install start stop check log help
    case "$command" in
        deploy)
            tca_local_install
            tca_local_start $service
        ;;
        install)
            tca_local_install
        ;;
        start)
            tca_local_start $service
        ;;
        stop)
            tca_local_stop $service
        ;;
        check)
            check_tca_local_status
        ;;
        log)
            get_tca_local_log
        ;;
        help)
            LOG_INFO "TCA Local Script Help"
            tca_local_help
        ;;
        *)
            LOG_ERROR "Command:'$command' not supported. [Support command: install/start/stop/check/log/help]"
            exit 1
        ;;
    esac
}

