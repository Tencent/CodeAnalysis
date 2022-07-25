#!/bin/bash

CURRENT_SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")";pwd)
TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$( cd "$(dirname $CURRENT_SCRIPT_PATH)"; pwd )"}
TCA_PROJECT_PATH=${TCA_PROJECT_PATH:-"$( cd "$(dirname $TCA_SCRIPT_ROOT)"; pwd )"}

source $TCA_SCRIPT_ROOT/utils.sh

export REDIS_PASSWD=${REDIS_PASSWD:-"tca2022"}
export MYSQL_USERNAME=${MYSQL_USERNAME:-"tca"}
export MYSQL_PASSWORD=${MYSQL_PASSWORD:-"TCA!@#2021"}
export MARIADB_SETUP_FILE=${MARIADB_SETUP_FILE:-/tmp/mariadb_repo_setup}
export MARIADB_SETUP_CACHE_FILE=${MARIADB_SETUP_CACHE_FILE}


function check_redis() {
    ret=""
    if command_exists redis-server; then
        ret="true"
    else
        ret="false"
    fi
    echo "$ret"
}

function check_mysql() {
    ret=""
    if command_exists mysqld; then
        ret="true"
    else
        ret="false"
    fi
    echo "$ret"
}

function install_and_conf_redis_on_centos() {
    LOG_INFO "    Start to run: yum install epel-release redis. [Please wait for moment.]"
	yum install -q -y epel-release redis --nogpgcheck || error_exit "yum install redis failed"
}

function install_and_conf_redis_on_ubuntu() {
    LOG_INFO "    Start to run: apt-get update and apt-get install redis. [Please wait for moment.]"
    apt-get update -qq -y >/dev/null || error_exit "apt-get update"
    apt-get install -qq -y redis >/dev/null || error_exit "apt-get install redis failed"
    
}

function config_redis() {
    LOG_INFO "[RedisInstall] Config redis auth: "$REDIS_PASSWD
    if [ -f /etc/redis.conf ]; then
        LOG_INFO "    redis.conf path: /etc/redis.conf"
        cp /etc/redis.conf /etc/redis.conf.bak
        echo "requirepass $REDIS_PASSWD" >> /etc/redis.conf
    fi

    if [ -f /etc/redis/redis.conf ]; then
        LOG_INFO "    redis.conf path: /etc/redis/redis.conf"
        cp /etc/redis/redis.conf /etc/redis/redis.conf.bak
        echo "requirepass $REDIS_PASSWD" >> /etc/redis/redis.conf
    fi
}

function start_redis() {
    redis_ret=$( check_target_process_exist "redis-server" )
    if [ $redis_ret == "true" ]; then
        return 0
    fi

	LOG_INFO "[RedisInstall] Start redis service"
    if command_normal systemctl; then
        systemctl start redis
        LOG_INFO "Set redis auto start during machine start"
        systemctl enable redis
    else
        LOG_WARN "Using nohup start redis-server"
        nohup /usr/bin/redis-server --requirepass $REDIS_PASSWD 2>redis_start.error &
    fi
}

function restart_redis() {
	LOG_INFO "Start redis service"
    if command_normal systemctl; then
        systemctl restart redis
    else
        normal_kill "redis-server"
        LOG_WARN "Using nohup start redis-server"
        nohup /usr/bin/redis-server --requirepass $REDIS_PASSWD 2>redis_start.error &
    fi
}

function quiet_install_redis() {
    ret=$( check_redis )
    if [ "$ret" == "true" ]; then
        LOG_WARN "This machine had installed redis-server"
        return 0
    fi

    LINUX_OS=$( get_linux_os )
	LOG_INFO "[RedisInstall] Start to install redis"

    case "$LINUX_OS" in
        centos|rhel|sles|tlinux|tencentos)
            install_and_conf_redis_on_centos
        ;;
        ubuntu|debian|raspbian)
            install_and_conf_redis_on_ubuntu
        ;;
        *)
            LOG_ERROR "$LINUX_OS not supported."
            exit 1
        ;;
    esac
    LOG_INFO "[RedisInstall] Install redis successfully."
    
    config_redis
    start_redis
}

function check_mariadb_cache_file() {
    if [ -n "$MARIADB_SETUP_CACHE_FILE" ]; then
        ret="true"
    else
        ret="false"
    fi
    echo "$ret"
}

function download_and_conf_mariadb_setup_file() {
    cache=$( check_mariadb_cache_file )
    if [ "$cache" == "false" ]; then
        wget -O $MARIADB_SETUP_FILE http://downloads.mariadb.com/MariaDB/mariadb_repo_setup || error_exit "download mariadb_repo_setup failed"
    else
        LOG_INFO "Use Mariadb PKG Cache: "$MARIADB_SETUP_FILE
        MARIADB_SETUP_FILE=$MARIADB_SETUP_CACHE_FILE
    fi
    chmod +x $MARIADB_SETUP_FILE
    $MARIADB_SETUP_FILE --mariadb-server-version="mariadb-10.6" || error_exit "config mariadb_repo_setup failed，请手动执行：$MARIADB_SETUP_FILE --mariadb-server-version='mariadb-10.6'"
}

function start_mariadb() {
    mariadb_ret=$( check_target_process_exist "mariadbd\|mysqld" )
    if [ $mariadb_ret == "true" ]; then
        return 0
    fi
    
    LOG_INFO "[MariadbInstall] Start mysqld service"
    if command_normal systemctl; then
        LOG_INFO "Using systemctl start mysqld"
        systemctl start mysqld
        LOG_INFO "Set mysqld auto start during machine start"
        systemctl enable mysqld
    else
        LOG_WARN "Using nohup start mysqld"
        nohup /usr/bin/mysqld_safe 2>$TCA_PROJECT_PATH/mysql_start.error &
        # nohup /usr/sbin/mariadbd --basedir=/usr --datadir=/var/lib/mysql --plugin-dir=/usr/lib/mysql/plugin --user=mysql --skip-log-error --pid-file=/run/mysqld/mysqld.pid --socket=/run/mysqld/mysqld.sock 2>mysql_start.error &
    fi
    sleep 10
    mariadb_ret=$( check_target_process_exist "mariadbd\|mysqld" )
    if [ $mariadb_ret == "true" ]; then
        return 0
    else
        LOG_ERROR "[MariadbInstall] Start mysqld failed"
        if command_normal systemctl; then
            LOG_ERROR "execute 'systemctl status mysqld' to view error log."
        else
            LOG_ERROR "execute 'cat $TCA_PROJECT_PATH/mysql_start.error' to view error log."
        fi
    fi
}


function restart_mariadb() {
    if command_normal systemctl; then
        LOG_INFO "Using systemctl start mysqld"
        systemctl start mysqld
    else
        normal_kill "mariadbd\|mysqld"
        LOG_WARN "Using nohup start mysqld"
        nohup /usr/bin/mysqld_safe 2>$TCA_PROJECT_PATH/mysql_start.error &
    fi
}

function config_mariadb() {
    LOG_INFO "[MariadbInstall] Config mysql auth, user: '$MYSQL_USERNAME', password: '$MYSQL_PASSWORD'"
    mysql -uroot -hlocalhost -e "DELETE FROM mysql.user WHERE USER='$MYSQL_USERNAME' AND HOST='localhost';FLUSH PRIVILEGES;"
    mysql -uroot -hlocalhost -e "CREATE USER '$MYSQL_USERNAME'@'localhost' IDENTIFIED BY \"$MYSQL_PASSWORD\";GRANT ALL ON *.* TO '$MYSQL_USERNAME'@'localhost' WITH GRANT OPTION;FLUSH PRIVILEGES;"
}

function start_mariadb_with_docker() {
    mariadb_ret=$( check_target_process_exist "mariadbd\|mysqld" )
    if [ $mariadb_ret == "true" ]; then
        return 0
    fi
    
    LOG_WARN "[MariadbInstall] Start mysqld in docker..."
    LOG_WARN "[MariadbInstall] Config mysql auth, user: '$MYSQL_USERNAME', password: '$MYSQL_PASSWORD'"
    sed -i "s/TCA_MYSQL_PASSWORD/${MYSQL_PASSWORD}/g ; s/TCA_MYSQL_USERNAME/${MYSQL_USERNAME}/g" "$TCA_PROJECT_PATH/server/sql/reset_root_password.sql"
    nohup mysqld --user=mysql --datadir=/var/opt/tca/mariadb --log_error=/var/log/tca/mariadb/mariadb.err --init-file="$TCA_PROJECT_PATH/server/sql/reset_root_password.sql" 2>/var/log/tca/mariadb/mysql_error.out &
    sleep 10
    mariadb_ret=$( check_target_process_exist "mariadbd\|mysqld" )
    if [ $mariadb_ret == "true" ]; then
        LOG_INFO "[MariadbInstall] Start mysqld success"
    else
        LOG_ERROR "[MariadbInstall] Start mysqld failed"
    fi
}

function quiet_install_mariadb() {
    ret=$( check_mysql )
    if [ "$ret" == "true" ]; then
        LOG_WARN "[MariadbInstall] This machine had installed mysql-server"
        start_mariadb
        return 0
    fi
    
    LINUX_OS=$( get_linux_os )
    install_base || error_exit "Install base software failed"
    LOG_INFO "[MariadbInstall] Start to install mysqld"
    
    case "$LINUX_OS" in
        centos|rhel|sles|tlinux)
            download_and_conf_mariadb_setup_file
            LOG_INFO "    Start to run: yum install MariaDB-server MariaDB-backup [Please wait for moment.]"
            yum install -q -y MariaDB-server MariaDB-backup || error_exit "Install mariadb failed"
        ;;
        ubuntu|debian|raspbian)
            download_and_conf_mariadb_setup_file
            LOG_INFO "    Start to run: apt-get install mariadb-server mariadb-backup [Please wait for moment.]"
            apt-get install -qq -y mariadb-server mariadb-backup >/dev/null || error_exit "Install mariadb failed"
        ;;
        tencentos)
            LOG_INFO "    Start to run: yum install mysql-server"
            yum install -q -y mysql-server
        ;;
        *)
            LOG_ERROR "$LINUX_OS not supported."
            exit 1
        ;;
    esac

    start_mariadb
    config_mariadb
}


function interactive_install_redis() {
    ret=$( check_redis )
    if [ "$ret" == "true" ]; then
        start_redis
        return 0
    fi
    LOG_INFO "Do you want to install [Redis] by this script?"
    read -p "Please enter:[Y/N]" result
    case $result in
            [yY])
                quiet_install_redis
                ;;
            [nN])
                LOG_WARN "Cancel install Redis"
                return 1
                ;;
            *)
                LOG_ERROR "Invalid input. Stop."
                exit 1
                ;;
        esac
}


function interactive_install_mariadb() {
    ret=$( check_mysql )
    if [ "$ret" == "true" ]; then
        start_mariadb
        return 0
    fi
    LOG_INFO "Do you want to install [Mariadb] by this script?"
    read -p "Please enter:[Y/N]" result
    case $result in
        [yY])
            quiet_install_mariadb
            ;;
        [nN])
            LOG_WARN "Cancel install mariadb"
            return 1
            ;;
        *)
            LOG_ERROR "Invalid input. Stop."
            exit 1
            ;;
    esac
}

