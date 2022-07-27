#!/bin/bash

CURRENT_SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")";pwd)
TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$(dirname $CURRENT_SCRIPT_PATH; pwd)"}
NGINX_SRC_URL=${NGINX_SRC_URL:-"http://nginx.org/download/nginx-1.20.2.tar.gz"}
NGINX_SRC_PKG_PATH=${NGINX_SRC_PKG_PATH:-"/tmp/nginx-1.20.2.tar.gz"}
NGINX_SRC_PATH=${NGINX_SRC_PATH:-"/usr/local/src/nginx-1.20.2"}
NGINX_SRC_DIR=$(dirname  $NGINX_SRC_PATH)
NGINX_LOG_DIR=${NGINX_LOG_PATH:-"/var/log/nginx"}

source $TCA_SCRIPT_ROOT/utils.sh

function check_nginx() {
    ret=""
    if command_exists nginx; then
        ret="true"
    else
        ret="false"
    fi
    echo "$ret"
}

function config_nginx() {
    LOG_INFO "[NginxInstall] Comment nginx default listen"
    sed -ri 's/^([[:space:]]*)(server_name|listen)/\1#\2/' /etc/nginx/nginx.conf
    if [ -f "/etc/nginx/sites-enabled/default" ]; then
        sed -ri 's/^([[:space:]]*)(server_name|listen)/\1#\2/' /etc/nginx/sites-enabled/default
    fi
}

####################################
#          源码安装Nginx            #
####################################
function install_nginx_using_src() {
    LOG_INFO "    Start to run: download nginx src pkg and compile. [Please wait for moment.]"
    download_nginx_src
    pre_install_for_nginx
    compile_and_link_nginx
    config_nginx_from_src_install
}

function download_nginx_src() {
    LOG_INFO "[NginxInstall] Download nginx src from $NGINX_SRC_URL, save to $NGINX_SRC_PKG_PATH"
    wget -O $NGINX_SRC_PKG_PATH $NGINX_SRC_URL || error_exit "Download nginx src failed"
}

function pre_install_for_nginx() {
    LOG_INFO "[NginxInstall] Pre install tools"
    case "$LINUX_OS" in
        ubuntu|debian|raspbian)
            tools="gcc libssl-dev zlib1g-dev libpcre3-dev libbz2-dev libreadline-dev"
            LOG_INFO "    Start run: apt-get update and apt-get install $tools"
            apt-get update -qq >/dev/null || error_exit "[NginxInstall] pre install tools failed"
            DEBIAN_FRONTEND=noninteractive apt-get -y install -qq $tools >/dev/null || error_exit "[PythonInstall] pre install tools failed"
        ;;
        *) 
            tools="gcc zlib-devel pcre-devel bzip2-devel openssl-devel readline-devel"
            LOG_INFO "    Start run: yum install tools: $tools"
	        yum -q -y install $tools || error_exit "[NginxInstall] pre install tools failed"
        ;;
    esac
    LOG_INFO "[NginxInstall] Pre install tools successfully."
}

function compile_and_link_nginx() {
    LOG_INFO "[NginxInstall] Extract into $NGINX_SRC_PATH"
    tar zxf $NGINX_SRC_PKG_PATH -C $NGINX_SRC_DIR && cd $NGINX_SRC_PATH
    LOG_INFO "[NginxInstall] Config and install nginx"
    ./configure \
        --sbin-path=/usr/local/nginx/nginx \
        --conf-path=/etc/nginx/nginx.conf \
        --pid-path=/run/nginx.pid \
        --with-stream \
        --with-http_ssl_module \
        --with-http_v2_module \
        --with-http_auth_request_module >/dev/null || error_exit "Nginx src configure failed"
    make -j4 >/dev/null && make install >/dev/null && make clean >/dev/null
    ln -sf /usr/local/nginx/nginx /usr/local/bin/nginx
    mkdir /etc/nginx/conf.d/ $NGINX_LOG_DIR
}

function config_nginx_from_src_install() {
    LOG_INFO "[NginxInstall] Config nginx from src"
    cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak
    echo "
worker_processes auto;
pid /run/nginx.pid;

events {
	worker_connections 1024;
}

http {
	sendfile on;
	tcp_nopush on;
	tcp_nodelay on;
	keepalive_timeout 65;
	types_hash_max_size 2048;
	include /etc/nginx/mime.types;
	default_type application/octet-stream;
	access_log /var/log/nginx/access.log;
	error_log /var/log/nginx/error.log;

	include /etc/nginx/conf.d/*.conf;
}" > /etc/nginx/nginx.conf
}

function quiet_install_nginx() {
    ret=$( check_nginx )
    if [ "$ret" == "true" ]; then
        LOG_WARN "This machine had installed nginx"
        return 0
    fi
    if [ "$SOURCE" == "true" ]; then
        LINUX_OS=""
    else
        LINUX_OS=$( get_linux_os )
    fi
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
            LOG_WARN "$LINUX_OS install by source"
            install_base
            install_nginx_using_src
        ;;
    esac
    LOG_INFO "[NginxInstall] Install nginx successfully."
    config_nginx
}

function interactive_install_nginx() {
    ret=$( check_nginx )
    if [ "$ret" == "true" ]; then
        return 0
    fi
    LOG_WARN "Deploying TCA with docker/docker-compose depends on Nginx. Current machine has not installed nginx."
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
