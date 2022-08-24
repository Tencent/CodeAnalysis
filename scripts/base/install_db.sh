#!/bin/bash

CURRENT_SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")";pwd)
TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$( cd "$(dirname $CURRENT_SCRIPT_PATH)"; pwd )"}
TCA_PROJECT_PATH=${TCA_PROJECT_PATH:-"$( cd "$(dirname $TCA_SCRIPT_ROOT)"; pwd )"}
REDIS_SRC_URL=${REDIS_SRC_URL:-"http://download.redis.io/releases/redis-5.0.4.tar.gz"}
REDIS_SRC_PKG_PATH=${REDIS_SRC_PKG_PATH:-"/tmp/redis-5.0.4.tar.gz"}
REDIS_SRC_PATH=${REDIS_SRC_PATH:-"/usr/local/src/redis-5.0.4"}
REDIS_SRC_DIR=$(dirname  $REDIS_SRC_PATH)
REDIS_LOG_PATH=${REDIS_LOG_PATH:-"/var/log/redis/redis-server.log"}
REDIS_LOG_DIR=$(dirname $REDIS_LOG_PATH)

source $TCA_SCRIPT_ROOT/utils.sh

export REDIS_PASSWD=${REDIS_PASSWD:-"tca2022"}
export MYSQL_USERNAME=${MYSQL_USERNAME:-"tca"}
export MYSQL_PASSWORD=${MYSQL_PASSWORD:-"TCA!@#2021"}
export MARIADB_SETUP_FILE=${MARIADB_SETUP_FILE:-/tmp/mariadb_repo_setup}
export MARIADB_SETUP_CACHE_FILE=${MARIADB_SETUP_CACHE_FILE}

####################################
#       mysql&redis命令检查         #
####################################
function check_redis() {
    ret=""
    if command_exists redis-server; then
        ret="true"
    else
        ret="false"
    fi
    echo "$ret"
}

function check_mysqld() {
    ret=""
    if command_exists mysqld; then
        ret="true"
    else
        ret="false"
    fi
    echo "$ret"
}

function check_mysql_client() {
    ret=""
    if command_exists mysql; then
        ret="true"
    else
        ret="false"
    fi
    echo "$ret"
}

####################################
#          源码安装Redis            #
####################################
function install_redis_using_src() {
    LOG_INFO "    Start to run: download redis src pkg and compile. [Please wait for moment.]"
    download_redis_src
    pre_install_for_redis
    compile_and_link_redis
    create_redis_systemctl_service
}

function download_redis_src() {
    LOG_INFO "[RedisInstall] Download redis src from $REDIS_SRC_URL, save to $REDIS_SRC_PKG_PATH"
    wget -O $REDIS_SRC_PKG_PATH $REDIS_SRC_URL || error_exit "Download redis src failed"
}

function pre_install_for_redis() {
    tools="gcc make tcl"
    LOG_INFO "[RedisInstall] Pre install tools"
    case "$LINUX_OS" in
        ubuntu|debian|raspbian)
            LOG_INFO "    Start run: apt-get update and apt-get install $tools"
            apt-get update -qq >/dev/null || error_exit "[RedisInstall] pre install tools failed"
            DEBIAN_FRONTEND=noninteractive apt-get -y install -qq $tools >/dev/null || error_exit "[PythonInstall] pre install tools failed"
        ;;
        *)
            LOG_INFO "    Start run: yum install tools: $tools"
	        yum -q -y install $tools || error_exit "[RedisInstall] pre install tools failed"
        ;;
    esac
    LOG_INFO "[RedisInstall] Pre install tools successfully."
}

function compile_and_link_redis() {
    LOG_INFO "[RedisInstall] Extract into $REDIS_SRC_PATH"
    tar zxf $REDIS_SRC_PKG_PATH -C $REDIS_SRC_DIR && cd $REDIS_SRC_PATH
    LOG_INFO "[RedisInstall] Config and install redis"
    cd $REDIS_SRC_PATH/deps && make -j4 hiredis jemalloc linenoise lua >/dev/null
    cd $REDIS_SRC_PATH && make -j4 >/dev/null && make install >/dev/null && make clean >/dev/null
    cp $REDIS_SRC_PATH/redis.conf  /etc/redis.conf
}

function create_redis_systemctl_service() {
    LOG_INFO "[RedisInstall] Create redis systemctl service file"
    if [ -d "/etc/systemd/system" ]; then
        echo "[Unit]
Description=redis-server
After=network.target

[Service]
Type=forking
ExecStart=/usr/local/bin/redis-server /etc/redis.conf
ExecStop=/usr/local/bin/redis-cli shutdown
Restart=always

PrivateTmp=true

[Install]
WantedBy=multi-user.target" > /etc/systemd/system/redis.service
    fi

}

####################################
#        包管理工具安装Redis         #
####################################
function install_redis_on_centos() {
    LOG_INFO "    Start to run: yum install epel-release redis. [Please wait for moment.]"
    yum install -q -y epel-release redis --nogpgcheck || error_exit "yum install redis failed"
}

function install_redis_on_ubuntu() {
    LOG_INFO "    Start to run: apt-get update and apt-get install redis. [Please wait for moment.]"
    apt-get update -qq -y >/dev/null || error_exit "apt-get update"
    apt-get install -qq -y redis >/dev/null || error_exit "apt-get install redis failed"
}

####################################
#          配置Redis                #
####################################
function config_redis() {
    mkdir -p $REDIS_LOG_DIR
    LOG_INFO "[RedisInstall] Config redis auth: "$REDIS_PASSWD
    redis_conf_path=""
    if [ -f "/etc/redis.conf" ]; then
        redis_conf_path="/etc/redis.conf"
    elif [ -f "/etc/redis/redis.conf" ]; then
        redis_conf_path="/etc/redis/redis.conf"
    fi
    LOG_INFO "    redis.conf path: $redis_conf_path"
    cp "$redis_conf_path" "$redis_conf_path".bak
    echo "requirepass $REDIS_PASSWD" >> $redis_conf_path
    echo "logfile $REDIS_LOG_PATH" >> $redis_conf_path
    echo "daemonize no" >> $redis_conf_path
}

####################################
#          启动Redis                #
####################################
function start_redis() {
    redis_ret=$( check_target_process_exist "redis-server" )
    if [ $redis_ret == "true" ]; then
        return 0
    fi

	LOG_INFO "[RedisInstall] Start redis service"
    if command_normal systemctl; then
        systemctl start redis
        LOG_INFO "    Set redis auto start during machine start"
        systemctl enable redis
    else
        LOG_WARN "    Using nohup start redis-server"
        nohup /usr/bin/redis-server --requirepass $REDIS_PASSWD 2>redis_start.error &
    fi
}

function restart_redis() {
	LOG_INFO "[RedisInstall] Start redis service"
    if command_normal systemctl; then
        systemctl restart redis
    else
        normal_kill "redis-server"
        LOG_WARN "    Using nohup start redis-server"
        nohup /usr/bin/redis-server --requirepass $REDIS_PASSWD 2>redis_start.error &
    fi
}

####################################
#          安装Redis入口            #
####################################
function quiet_install_redis() {
    ret=$( check_redis )
    if [ "$ret" == "true" ]; then
        LOG_WARN "[RedisInstall] This machine had installed redis-server"
        return 0
    fi

    if [ "$SOURCE" == "true" ]; then
        LINUX_OS=""
    else
        LINUX_OS=$( get_linux_os )
    fi

	LOG_INFO "[RedisInstall] Start to install redis"

    case "$LINUX_OS" in
        centos|rhel|sles|tlinux|tencentos)
            install_redis_on_centos
        ;;
        ubuntu|debian|raspbian)
            install_redis_on_ubuntu
        ;;
        *)
            LOG_WARN "$LINUX_OS install by source"
            install_base
            install_redis_using_src
        ;;
    esac
    LOG_INFO "[RedisInstall] Install redis successfully."
    
    config_redis
    restart_redis
}

####################################
#        下载Mariadb安装文件         #
####################################
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
    $MARIADB_SETUP_FILE --mariadb-server-version="mariadb-10.6" >/dev/null || error_exit "config mariadb_repo_setup failed，请手动执行：$MARIADB_SETUP_FILE --mariadb-server-version='mariadb-10.6'"
}

####################################
#             启动Mariadb          #
####################################
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
            LOG_ERROR "Execute 'systemctl status mysqld' to view error log."
        else
            LOG_ERROR "Execute 'cat $TCA_PROJECT_PATH/mysql_start.error' to view error log."
        fi
    fi
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

function restart_mariadb() {
    LOG_INFO "[MariadbInstall] Restart mysqld service"
    if command_normal systemctl; then
        LOG_INFO "    Using systemctl restart mysqld"
        systemctl restart mysqld
    else
        normal_kill "mariadbd\|mysqld"
        LOG_WARN "    Using nohup restart mysqld"
        nohup /usr/bin/mysqld_safe 2>$TCA_PROJECT_PATH/mysql_start.error &
    fi
    sleep 10
    mariadb_ret=$( check_target_process_exist "mariadbd\|mysqld" )
    if [ $mariadb_ret == "true" ]; then
        return 0
    else
        LOG_ERROR "[MariadbInstall] Restart mysqld failed"
        if command_normal systemctl; then
            LOG_ERROR "Execute 'systemctl status mysqld' to view error log."
        else
            LOG_ERROR "Execute 'cat $TCA_PROJECT_PATH/mysql_start.error' to view error log."
        fi
    fi
}

####################################
#             配置Mariadb          #
####################################
function config_mariadb() {
    LOG_INFO "[MariadbInstall] Config mysql auth, user: '$MYSQL_USERNAME', password: '$MYSQL_PASSWORD'"
    mysql -uroot -hlocalhost -e "DELETE FROM mysql.user WHERE USER='$MYSQL_USERNAME' AND HOST='localhost';FLUSH PRIVILEGES;"
    mysql -uroot -hlocalhost -e "CREATE USER '$MYSQL_USERNAME'@'localhost' IDENTIFIED BY \"$MYSQL_PASSWORD\";GRANT ALL ON *.* TO '$MYSQL_USERNAME'@'localhost' WITH GRANT OPTION;FLUSH PRIVILEGES;"
}

####################################
#          安装Mariadb入口          #
####################################
function quiet_install_mysql_client() {
    ret=$( check_mysql_client )
    if [ "$ret" == "true" ]; then
        LOG_WARN "[MySQLClientInstall] This machine had installed mysql-client"
        return 0
    fi
    
    LINUX_OS=$( get_linux_os )
    install_base || error_exit "Install base software failed"
    LOG_INFO "[MySQLClientInstall] Start to install mysql-client"
    
    case "$LINUX_OS" in
        centos|rhel|sles|tlinux)
            LOG_INFO "    Start to run: yum install MariaDB-client [Please wait for moment.]"
            download_and_conf_mariadb_setup_file
            yum install -q -y MariaDB-client || error_exit "Install MariaDB-client failed"
        ;;
        ubuntu|debian|raspbian)
            LOG_INFO "    Start to run: apt-get install MariaDB-client [Please wait for moment.]"
            download_and_conf_mariadb_setup_file
            apt-get install -qq -y mariadb-client >/dev/null || error_exit "Install mariadb-client failed. You can run 'apt-get install mysql-client' manually."
        ;;
        tencentos)
            LOG_INFO "    Start to run: yum install mysql-community-client [Please wait for moment.]"
            yum install -q -y mysql-community-client || error_exit "Install mysql-client failed"
        ;;
        *)
            LOG_ERROR "$LINUX_OS not supported."
            exit 1
        ;;
    esac
    LOG_INFO "[MySQLClientInstall] install mysql-client successfully"
}

function quiet_install_mariadb() {
    ret=$( check_mysqld )
    if [ "$ret" == "true" ]; then
        LOG_WARN "[MariadbInstall] This machine had installed mysql-server"
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

    restart_mariadb
    config_mariadb
}

####################################
#          交互式安装Redis          #
####################################
function interactive_install_redis() {
    if [ "$USE_EXTERNAL_REDIS" == "true" ]; then
        LOG_INFO "Use external redis, host: $REDIS_HOST, port: $REDIS_PORT"
        return 0
    fi
    ret=$( check_redis )
    if [ "$ret" == "true" ]; then
        return 0
    fi
    LOG_INFO "Do you want to install [Redis] by this script?"
    LOG_WARN "Deploying TCA depends on Redis. If you using remote redis service, you can enter N"
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

####################################
#    交互式安装Mariadb客户端与服务端   #
####################################
function interactive_install_mariadb() {
    ret=$( check_mysql_client )
    if [ "$ret" != "true" ]; then
        LOG_INFO "Do you want to install [mysql-client] by this script?"
        LOG_WARN "For initializing tca database"
        read -p "Please enter:[Y/N]" result
        case $result in
            [yY])
                quiet_install_mysql_client
                ;;
            [nN])
                LOG_WARN "Cancel install mysql-client"
                return 1
                ;;
            *)
                LOG_ERROR "Invalid input. Stop."
                exit 1
                ;;
        esac
    fi

    if [ "$USE_EXTERNAL_MYSQL" == "true" ]; then
        LOG_INFO "Use external mysql, host: $MYSQL_HOST, port: $MYSQL_PORT"
        return 0
    fi
    ret=$( check_mysqld )
    if [ "$ret" == "true" ]; then
        return 0
    fi
    LOG_INFO "Do you want to install [Mariadb] by this script?"
    LOG_WARN "Deploying TCA depends on MySQL/Mariadb. If you using remote mysql service, you can enter N"
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
