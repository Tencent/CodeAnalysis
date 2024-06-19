#!/bin/bash

CURRENT_SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")";pwd)
TCA_PROJECT_PATH=${TCA_PROJECT_PATH:-"$CURRENT_SCRIPT_PATH"}
TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$TCA_PROJECT_PATH/scripts"}

source $TCA_SCRIPT_ROOT/utils.sh
source $TCA_SCRIPT_ROOT/base/install_git_lfs.sh
source $TCA_SCRIPT_ROOT/base/install_bin.sh
source $TCA_SCRIPT_ROOT/base/install_docker.sh

function tca_help() {
    LOG_INFO "Support command:"
    LOG_INFO "Arg1: Mode, support value: local, docker, docker-compose, help, default:'help'"
    LOG_INFO "Arg2: Operate, details: "
    LOG_INFO "      [local] deploy, install, start, stop, check, log, help. You can run ./quick_install.sh local help to view more details"
    LOG_INFO "      [docker] deploy, start, stop"
    LOG_INFO "      [docker-compose] deploy, start, stop, build"
    LOG_INFO ""
    LOG_INFO "Note:"
    LOG_INFO " * Run with local: will help to you install python, mariadb/mysql, redis, nginx. [Only support linux]"
    LOG_INFO " * Run with docker: will help you to install docker"
    LOG_INFO " * Run with docker-compose: will help you to install docker and docker-compose"
    LOG_INFO ""
    LOG_INFO "example:"
    LOG_INFO "    1. use current machine to deploy tca server, web and client"
    LOG_INFO "        install TCA on local:                      ./quick_install.sh local install"
    LOG_INFO "        install base tools on local:               ./quick_install.sh local install base"
    LOG_INFO "        start TCA on local:                        ./quick_install.sh local start"
    LOG_INFO "        start TCA main services on local:          ./quick_install.sh local start main"
    LOG_INFO "        install and start TCA on local:            ./quick_install.sh local deploy"
    LOG_INFO "        check TCA status on local:                 ./quick_install.sh local check"
    LOG_INFO "        stop tca on local:                         ./quick_install.sh local stop"
    LOG_INFO ""
    LOG_INFO "    2. use docker to deploy tca server, web and client"
    LOG_INFO "        run all services in a container:           ./quick_install.sh docker deploy" 
    LOG_INFO "        start a stopped tca container:             ./quick_install.sh docker start" 
    LOG_INFO "        stop a tca container:                      ./quick_install.sh docker stop" 
    LOG_INFO ""
    LOG_INFO "    3. use docker-compose to deploy tca server, web and client"
    LOG_INFO "        run TCA with docker-compose:               ./quick_install.sh docker-compose deploy"
    LOG_INFO "        restart TCA with docker-compose:           ./quick_install.sh docker-compose start  (equal: docker-compose up -d)"
    LOG_INFO "        rebuild TCA images with docker-compose:    ./quick_install.sh docker-compose build"

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
            LOG_INFO "Start tca directly. [Only support Linux]"
            source $TCA_SCRIPT_ROOT/deploy/tca_local.sh
            tca_local_main "$2" "$3"
        ;;
        docker)
            LOG_INFO "Start tca using docker"
            source $TCA_SCRIPT_ROOT/deploy/tca_docker.sh
            interactive_install_docker
            tca_docker_main "$2"
        ;;
        docker-compose)
            LOG_INFO "Start tca using docker-compose"
            source $TCA_SCRIPT_ROOT/deploy/tca_docker_compose.sh
            interactive_install_docker
            interactive_install_docker_compose
            tca_docker_compose_main "$2"
        ;;
        help)
            tca_help
        ;;
        *)
            LOG_WARN "Mode '$mode' not supported [Support mode: local、docker、docker-compose]"
            tca_help
        ;;
    esac
}

deploy "$1" "$2" "$3"
