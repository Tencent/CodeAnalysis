#!/bin/bash

CURRENT_SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")";pwd)
TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$(dirname $CURRENT_SCRIPT_PATH; pwd)"}

source $TCA_SCRIPT_ROOT/utils.sh

check_nginx() {
    ret=""
    if command_exists nginx; then
        ret="true"
    else
        ret="false"
    fi
    echo "$ret"
}

config_nginx() {
    LOG_INFO "[NginxInstall] Comment nginx default listen"
    sed -ri 's/^([[:space:]]*)(server_name|listen)/\1#\2/' /etc/nginx/nginx.conf
    if [ -f "/etc/nginx/sites-enabled/default" ]; then
        sed -ri 's/^([[:space:]]*)(server_name|listen)/\1#\2/' /etc/nginx/sites-enabled/default
    fi
}

quiet_install_nginx() {
    ret=$( check_nginx )
    if [ "$ret" == "true" ]; then
        LOG_WARN "This machine had installed nginx"
        return 0
    fi

    LINUX_OS=$( get_linux_os )
	LOG_INFO "[NginxInstall] Start to install nginx"

    case "$LINUX_OS" in
        centos|rhel|sles|tlinux|tencentos)
            LOG_INFO "    Start to run: yum install epel-release nginx [Please wait for a moment.]"
            yum install -q -y epel-release nginx >/dev/null || error_exit "yum install nginx failed"
        ;;
        ubuntu|debian|raspbian)
            LOG_INFO "    Start to run: apt-get update and apt-get install nginx [Please wait for a moment.]"
            apt-get update -qq >/dev/null || error_exit "apt-get update failed"
            apt-get install -qq -y nginx >/dev/null || error_exit "apt-get install nginx failed"
        ;;
        *)
            LOG_ERROR "$LINUX_OS not supported."
            exit 1
        ;;
    esac
    LOG_INFO "[NginxInstall] Install nginx successfully."
    config_nginx
}

interactive_install_nginx() {
    ret=$( check_nginx )
    if [ "$ret" == "true" ]; then
        return 0
    fi
    LOG_INFO "Do you want to install [Nginx] by this script?"
    read -p "Please enter:[Y/N]" result
    case $result in
        [yY])
            quiet_install_nginx
            ;;
        [nN])
            LOG_WARN "Cancel install nginx"
            return 1
            ;;
        *)
            LOG_ERROR "Invalid input. Stop."
            exit 1
            ;;
    esac
}
