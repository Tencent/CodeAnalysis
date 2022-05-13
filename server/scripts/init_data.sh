#!/bin/bash

echo "Start to init server data..."


CURRENT_PATH=$(dirname $(cd "$(dirname "$0")";pwd))
MAIN_PROJECT_PATH=$CURRENT_PATH/projects/main
ANALYSIS_PROJECT_PATH=$CURRENT_PATH/projects/analysis
LOGIN_PROJECT_PATH=$CURRENT_PATH/projects/login
FILE_PROJECT_PATH=$CURRENT_PATH/projects/file
PROJECT_TMP_PATH=$CURRENT_PATH/tmp
PROJECT_LOG_PATH=$CURRENT_PATH/logs
CONFIG_PATH=$CURRENT_PATH/configs

source $CURRENT_PATH/scripts/config.sh
bash $CURRENT_PATH/scripts/init_config.sh

function init_main() {
    echo "Init main db"
    cd $MAIN_PROJECT_PATH
    echo "Init checkertool and checkerpackage"
    # 运行数据初始化脚本，导入检测工具和规则包
    python manage.py initializedb_open
    python manage.py initialize_exclude_paths
    python manage.py loadcheckers all --dirname open_source
    python manage.py loadpackages all --dirname open_source_package
}

function init_analysis() {
    echo "Init analysis db"
    cd $ANALYSIS_PROJECT_PATH
    python manage.py createcachetable
    python manage.py initialuser
}

function init_login() {
    echo "Init login db"
    cd $LOGIN_PROJECT_PATH
    python manage.py initializedb
    echo "################################"
    echo "Current dafault admin/password: "$TCA_DEFAULT_ADMIN/$TCA_DEFAULT_PASSWORD
    echo "################################"
}

function init_file() {
    echo "Init file db"
    cd $FILE_PROJECT_PATH
    python manage.py migrate --noinput --traceback
}


init_main
init_analysis
init_file
init_login
