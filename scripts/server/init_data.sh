#!/bin/bash

CURRENT_SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")";pwd)
TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$(cd $(dirname $CURRENT_SCRIPT_PATH); pwd)"}

source $TCA_SCRIPT_ROOT/utils.sh
source $TCA_SCRIPT_ROOT/server/_base.sh


function check_mysql_config() {
    if [ -z "$MYSQL_HOST" ]; then
        LOG_ERROR "Wrong MySQL config"
        exit -1
    fi
}

function check_redis_config() {
    if [ -z "$REDIS_HOST" ]; then
        LOG_ERROR "Wrong Redis config"
        exit -1
    fi
}

function create_database() {
    LOG_INFO "[TCAServer] Init db, create database...[DB: MYSQL_HOST=$MYSQL_HOST, MYSQL_PORT=$MYSQL_PORT, MYSQL_USER=$MYSQL_USER]"
    mysql -u$MYSQL_USER -p$MYSQL_PASSWORD -h$MYSQL_HOST -P$MYSQL_PORT < $TCA_SERVER_PATH/sql/init.sql
    if [ "$?" != "0" ]; then
        LOG_ERROR "Create TCA database failed."
        LOG_ERROR "请检查连接数据库的HOST、PORT、USER、PORT是否准确，或配置的USER是否有权限创建DB"
        LOG_ERROR "可在执行脚本之前设置 MYSQL_HOST、MYSQL_PORT、MYSQL_USER、MYSQL_PASSWORD 环境变量或直接调整 scripts/config.sh 脚本中相关变量"
        exit 1
    fi
}

function init_main_db() {
    LOG_INFO "[TCAServer] Init main db..."
    python manage.py createcachetable >/dev/null
    python manage.py migrate --noinput --traceback >/dev/null
}

function init_analysis_db() {
    LOG_INFO "[TCAServer] Init analysis db..."
    python manage.py createcachetable >/dev/null
    python manage.py migrate --noinput --traceback >/dev/null
}

function init_login_db() {
    LOG_INFO "[TCAServer] Init login db..."
    python manage.py createcachetable >/dev/null
    python manage.py migrate --noinput --traceback >/dev/null
}

function init_file_db() {
    LOG_INFO "[TCAServer] Init file db..."
    python manage.py migrate --noinput --traceback >/dev/null
}

function init_main_data() {
    LOG_INFO "[TCAServer] Init main data..."
    python manage.py initializedb_open
    python manage.py initialize_exclude_paths
    LOG_INFO "[TCAServer] Init checker config..."
    python manage.py loadlibs all --dirname open_source_toollib --ignore-auth  >/dev/null
    python manage.py loadcheckers all --dirname open_source >/dev/null
    python manage.py loadpackages all --dirname open_source_package >/dev/null
    LOG_INFO "Init checkertool and checkerpackage successfully"
    return 0
}

function init_analysis_data() {
    LOG_INFO "[TCAServer] Init analysis data..."
    python manage.py initialuser >/dev/null
    return 0
}

function init_login_data() {
    LOG_INFO "[TCAServer] Init login data..."
    python manage.py initializedb >/dev/null
    LOG_INFO "################################"
    LOG_INFO "Current dafault admin/password: "$TCA_DEFAULT_ADMIN/$TCA_DEFAULT_PASSWORD
    LOG_INFO "################################"
    return 0
}

function init_server_db() {
    create_database || error_exit "create database failed"
    cd $TCA_SERVER_MAIN_PATH
    init_main_db || error_exit "Init main server database failed"
    cd $TCA_SERVER_ANALYSIS_PATH
    init_analysis_db || error_exit "Init analysis server database failed"
    cd $TCA_SERVER_LOGIN_PATH
    init_login_db || error_exit "Init login server database failed"
    cd $TCA_SERVER_FILE_PATH
    init_file_db || error_exit "Init file server database failed"
}

function init_server_data() {
    cd $TCA_SERVER_MAIN_PATH
    init_main_data || error_exit "Init main server data failed"
    cd $TCA_SERVER_ANALYSIS_PATH
    init_analysis_data || error_exit "Init analysis server data failed"
    cd $TCA_SERVER_LOGIN_PATH
    init_login_data || error_exit "Init login server data failed"
}


function init_server_db_and_data() {
    check_mysql_config
    check_redis_config
    init_server_db
    init_server_data
}
