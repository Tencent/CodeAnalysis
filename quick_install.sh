#!/bin/bash

CURRENT_SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")";pwd)
TCA_PROJECT_PATH=${TCA_PROJECT_PATH:-"$CURRENT_SCRIPT_PATH"}
TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$TCA_PROJECT_PATH/scripts"}

source $TCA_SCRIPT_ROOT/utils.sh
source $TCA_SCRIPT_ROOT/base/install_docker.sh
source $TCA_PROJECT_PATH/server/scripts/config.sh
source $TCA_SCRIPT_ROOT/config.sh
source $TCA_SCRIPT_ROOT/deploy/tca_local.sh
source $TCA_SCRIPT_ROOT/deploy/tca_docker.sh
source $TCA_SCRIPT_ROOT/deploy/tca_docker_compose.sh

function tca_help() {
    LOG_INFO "Support command:"
    LOG_INFO "Arg1. local/docker/docker-compose/help, default:'docker-compose'"
    LOG_INFO "Arg2. deploy/install/start/stop/check/log/help: Only for 'local' mode. You can run ./quick_install local help to view more details"
    LOG_INFO ""
    LOG_INFO "Run with docker: will help you install docker"
    LOG_INFO "Run with docker-compose: will help you install docker and docker-compose"
    LOG_INFO "Run with local: only support linux, will help you install python, mariadb, redis, nginx"
}

deploy() {
    mode=$1
    command=$2
    options=$3

    LOG_INFO "===========================================================" 
    LOG_INFO "                  _______    _____                         "
    LOG_INFO "                 |__   __|  / ____|     /\                 "   
    LOG_INFO "                    | |    | |         /  \                "  
    LOG_INFO "                    | |    | |        / /\ \               "  
    LOG_INFO "                    | |    | |____   / ____ \              "
    LOG_INFO "                    |_|     \_____| /_/    \_\             "
    LOG_INFO "                                                           "         
    LOG_INFO "==========================================================="
    case "$mode" in
        local)
            LOG_INFO "Start tca directly.[Only support Linux]"
            tca_local_main "$2" "$3"
        ;;
        docker)
            LOG_INFO "Start tca using docker"
            interactive_install_docker
            tca_docker_main
        ;;
        docker-compose)
            LOG_INFO "Start tca using docker-compose"
            interactive_install_docker
            interactive_install_docker_compose
            tca_docker_compose_main
        ;;
        help)
            tca_help
        ;;
        *)
            LOG_WARN "Default using 'compose' mode [Support mode: local、docker、docker-compose]"
            interactive_install_docker
            interactive_install_docker_compose
            tca_docker_compose_main
        ;;
    esac
}

deploy "$1" "$2" "$3"
