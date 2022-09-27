#!/bin/bash

CURRENT_SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")";pwd)
TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$( cd "$(dirname $CURRENT_SCRIPT_PATH)"; pwd )"}
TCA_INIT_DATA=${TCA_INIT_DATA:-"false"}

# server config environment variables
export DAEMON=False
export SERVER_ACCESS_LOG="-"
export SERVER_ERROR_LOG="-"
export FILE_STORAGE_DIR="/var/opt/tca/files/"
export REDIS_LOG_PATH="/var/log/tca/redis/redis.log"
export TCA_APP_DATA_DIR="/var/opt/tca/client"

source $TCA_SCRIPT_ROOT/utils.sh
source $TCA_SCRIPT_ROOT/config.sh
source $TCA_SCRIPT_ROOT/base/install_db.sh
source $TCA_SCRIPT_ROOT/base/install_nginx.sh
source $TCA_SCRIPT_ROOT/server/init_config.sh
source $TCA_SCRIPT_ROOT/server/init_data.sh
source $TCA_SCRIPT_ROOT/web/init.sh

function init_directory() {
    mkdir -p /var/log/tca/supervisord
    mkdir -p /var/log/tca/servers/main
    mkdir -p /var/log/tca/servers/analysis
    mkdir -p /var/log/tca/servers/login
    mkdir -p /var/log/tca/servers/file
    mkdir -p /var/log/tca/servers/scmproxy
    mkdir -p /var/log/tca/nginx
    mkdir -p /var/log/tca/mariadb
    mkdir -p /var/opt/tca/mariadb
    mkdir -p /var/opt/tca/redis
    mkdir -p /var/log/tca/redis
    mkdir -p /var/log/tca/client
    mkdir -p /var/opt/tca/files
    mkdir -p /var/opt/tca/tools
    mkdir -p /var/opt/tca/client
    mkdir -p /run/mysqld/
    mkdir -p /etc/tca/client
    chown -R mysql:mysql /var/log/tca/mariadb /var/opt/tca/mariadb /run/mysqld

    if [ -d "/CodeAnalysis/tools" ]; then
        rsync -a /CodeAnalysis/tools/ /var/opt/tca/tools/
        rm -rf /CodeAnalysis/tools
        # mv -f /CodeAnalysis/tools /var/opt/tca/tools/
        ln -s /var/opt/tca/tools /CodeAnalysis/tools
    else
        ln -s /var/opt/tca/tools /CodeAnalysis/tools
    fi

    if [ ! -f "/etc/tca/config.sh" ]; then
        cp /CodeAnalysis/scripts/config.sh /etc/tca/config.sh
    else
        mv /CodeAnalysis/scripts/config.sh /CodeAnalysis/scripts/config.sh.bak
        ln -s /etc/tca/config.sh /CodeAnalysis/scripts/config.sh
        source /etc/tca/config.sh
    fi

    if [ ! -f "/etc/tca/client/config.ini" ]; then
        cp /CodeAnalysis/client/config.ini /etc/tca/client/config.ini
    else
        mv /CodeAnalysis/client/config.ini /CodeAnalysis/client/config.ini.bak
        ln -s /etc/tca/client/config.ini /CodeAnalysis/client/config.ini
    fi
}

function start_db_and_init_data() {
    init_directory
    config_redis
    if [ $TCA_INIT_DATA == "true" ]; then
        if [ ! -d "/var/opt/tca/mariadb/mysql" ]; then
            mysql_install_db --user=mysql --datadir=/var/opt/tca/mariadb
        fi
        start_mariadb_with_docker
        init_server_db_and_data
    fi
    init_web_config
    config_nginx
    clean_server_pid
}

function stop_db() {
    force_kill "mariadbd\|mysqld"
    sleep 1
}

start_db_and_init_data
stop_db
LOG_INFO "===================================TCA启动说明==================================="
LOG_INFO "TCA服务已经基于Docker启动，可以观察下方日志，每个服务都进入 'RUNNING state'，说明服务都启动成功"
LOG_INFO "TCA访问入口：http://127.0.0.1"
LOG_INFO "TCA服务状态监控平台：http://127.0.0.1:9001"
LOG_INFO "TCA容器名称: tca-services"
LOG_INFO ""
LOG_INFO "注意："
LOG_INFO " - TCA首次启动默认使用前台进程模式运行"
LOG_INFO " - 如果需要后台模式运行，可以关闭当前进程，然后再执行 ./quick_install.sh docker start，则会以后台模式运行"
LOG_INFO "===================================TCA启动说明==================================="
supervisord -n -c /CodeAnalysis/scripts/docker/supervisord.conf
