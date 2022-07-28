#!/bin/bash

CURRENT_SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")";pwd)
TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$( cd "$(dirname $CURRENT_SCRIPT_PATH)"; pwd )"}

source $TCA_SCRIPT_ROOT/utils.sh

export DOCKER_INSTALL_FILE=${DOCKER_INSTALL_FILE:-/tmp/get-docker.sh}

function check_docker() {
    ret=""
    if command_exists docker; then
        ret="true"
    else
        ret="false"
    fi
    echo "$ret"
}

function check_docker_compose() {
    ret=""
    if command_exists docker-compose; then
        ret="true"
    else
        ret="false"
    fi
    echo "$ret"
}

function check_docker_service() {
    docker ps -q &>/dev/null
    if [ "$?" == "0" ]; then
        ret="true"
    else
        ret="false"
    fi
    echo "$ret"
}

function start_docker_service() {
    LOG_INFO "Start Docker service"
    
    ret=$( check_docker_service )
    if [ "$ret" == "true" ]; then
        LOG_INFO "* Docker had started"
        return 0
    fi

    systemctl restart docker
    start_docker_exit_code=$?

    if [ "$start_docker_exit_code" = "0" ]; then
        LOG_INFO "* Start Docker success"
        return 0
    else
        LOG_ERROR "Start Docker failed. Please check log"
        return 1
    fi
}

function quiet_install_docker() {
    ret=$( check_docker )
    if [ "$ret" == "true" ]; then
        LOG_WARN "This machine had installed docker"
    else
        LOG_INFO "Download docker and install"
        curl -fsSL https://get.docker.com -o $DOCKER_INSTALL_FILE
        sh $DOCKER_INSTALL_FILE
        rm $DOCKER_INSTALL_FILE
    fi

    check_docker_service
    if [ "$?" -ne 0 ] ; then
        start_docker_service
    fi
}

function quiet_install_docker_compose() {
    ret=$( check_docker_compose )
    if [ "$ret" == "true" ]; then
        LOG_WARN "This machine had installed docker_compose"
        return 0
    fi

    LOG_INFO "Download docker-compose and install"
    docker_compose_url="https://github.com/docker/compose/releases/download/1.27.2/docker-compose-$(uname -s)-$(uname -m)"
    curl -L ${docker_compose_url} -o /usr/local/bin/docker-compose
    retval=$?
    chmod +x /usr/local/bin/docker-compose
    if [ "$retval" -ne 0 ]; then
        LOG_WARN "Download docker-compose failed." 
        LOG_WARN "Please download manually, url: ${docker_compose_url}"
        LOG_WARN "  After download, copy to /usr/loca/bin/ and execute command: chmod +x /usr/local/bin/docker-compose"
        LOG_WARN "  docker-compose install Tutorial: https://docs.docker.com/compose/install/#install-compose-on-linux-systems"
        exit 1; 
    fi
}

function interactive_install_docker() {
    ret=$( check_docker )
    status=$( check_docker_service )
    if [ "$ret" == "true" ]; then
        if [ "$status" == "true" ]; then
            return 0
        else
            start_docker_service || error_exit "Start docker service failed"
            sleep 5
            return 0
        fi
    fi
    LOG_WARN "Deploying TCA with docker/docker-compose depends on docker. Current machine has not installed docker."
    LOG_INFO "Do you want to install [Docker] by this script?"
    read -p "Please enter:[Y/N]" result
    case $result in
            [yY])
                sleep 2
                quiet_install_docker
                ;;
            [nN])
                echo -e "Cancel install docker"
                return 1
                ;;
            *)
                LOG_ERROR "Invalid input. Stop."
                exit 1
                ;;
        esac
}

function interactive_install_docker_compose() {
    ret=$( check_docker_compose )
    if [ "$ret" == "true" ]; then
        return 0
    fi

    LOG_WARN "Deploying TCA with docker/docker-compose depends on docker. Current machine has not installed docker-compose."
    LOG_INFO "Do you want to install docker-compose by this script?"
    read -p "Please enter:[Y/N]" result
    case $result in
            [yY])
                sleep 2
                quiet_install_docker_compose
                ;;
            [nN])
                echo -e "Cancel install docker_compose"
                return 1
                ;;
            *)
                LOG_ERROR "Invalid input. Stop."
                exit 1
                ;;
        esac
}
