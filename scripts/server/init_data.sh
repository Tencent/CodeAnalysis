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
    LOG_INFO "Init db, create database..."
    mysql -u$MYSQL_USER -p$MYSQL_PASSWORD -h$MYSQL_HOST -P$MYSQL_PORT < $TCA_SERVER_PATH/sql/init.sql
}

function init_main_db() {
    LOG_INFO "Init main db"
    python manage.py createcachetable
    python manage.py migrate --noinput --traceback
}

function init_analysis_db() {
    LOG_INFO "Init analysis db"
    python manage.py createcachetable
    python manage.py migrate --noinput --traceback
}

function init_login_db() {
    LOG_INFO "Init login db"
    python manage.py createcachetable
    python manage.py migrate --noinput --traceback
}

function init_file_db() {
    LOG_INFO "Init file db"
    python manage.py migrate --noinput --traceback
}

function init_main_data() {
    LOG_INFO "Init main data"
    python manage.py initializedb_open
    python manage.py initialize_exclude_paths
    python manage.py loadcheckers all --dirname open_source
    python manage.py loadpackages all --dirname open_source_package
    LOG_INFO "Init checkertool and checkerpackage successfully"
    return 0
}

function init_analysis_data() {
    LOG_INFO "Init analysis data"
    python manage.py initialuser
    return 0
}

function init_login_data() {
    LOG_INFO "Init login data"
    python manage.py initializedb
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
