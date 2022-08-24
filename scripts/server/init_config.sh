#!/bin/bash

CURRENT_SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")";pwd)
TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$(cd $(dirname $CURRENT_SCRIPT_PATH); pwd)"}

source $TCA_SCRIPT_ROOT/utils.sh
source $TCA_SCRIPT_ROOT/config.sh
source $TCA_SCRIPT_ROOT/server/_base.sh

function create_server_dir() {
    LOG_INFO "[TCAServer] Create server directory"
    mkdir -p $TCA_SERVER_MAIN_PATH/log
    mkdir -p $TCA_SERVER_ANALYSIS_PATH/log
    mkdir -p $TCA_SERVER_LOGIN_PATH/log
    mkdir -p $TCA_SERVER_FILE_PATH/log
    mkdir -p $TCA_SERVER_FILE_PATH/data
    mkdir -p $TCA_SERVER_LOG_PATH
    mkdir -p $TCA_SERVER_TMP_PATH

    if [ ! -h "$TCA_SERVER_LOG_PATH/main_log" ]; then
        ln -s $TCA_SERVER_MAIN_PATH/log $TCA_SERVER_LOG_PATH/main_log
    fi
    
    if [ ! -h "$TCA_SERVER_LOG_PATH/analysis_log" ]; then
        ln -s $TCA_SERVER_ANALYSIS_PATH/log $TCA_SERVER_LOG_PATH/analysis_log
    fi

    if [ ! -h "$TCA_SERVER_LOG_PATH/login_log" ]; then
        ln -s $TCA_SERVER_LOGIN_PATH/log $TCA_SERVER_LOG_PATH/login_log
    fi

    if [ ! -h "$TCA_SERVER_LOG_PATH/file_log" ]; then
        ln -s $TCA_SERVER_FILE_PATH/log $TCA_SERVER_LOG_PATH/file_log
    fi

    if [ ! -h "$TCA_SERVER_LOG_PATH/scmproxy_log" ]; then
        mkdir -p $TCA_SERVER_SCMPROXY_PATH/logs
        ln -s $TCA_SERVER_SCMPROXY_PATH/logs $TCA_SERVER_LOG_PATH/scmproxy_log
    fi

    if [ ! -h "$TCA_SERVER_LOG_PATH/nginx_log" ]; then
        ln -s $NGINX_LOG_PATH $TCA_SERVER_LOG_PATH/nginx_log
    fi
}

function copy_server_config() {
    LOG_INFO "[TCAServer] Copy server config"
    rm -f $TCA_SERVER_MAIN_PATH/codedog/settings/local.py
    ln -s $TCA_SERVER_PATH/configs/django/local_main.py $TCA_SERVER_MAIN_PATH/codedog/settings/local.py

    rm -f $TCA_SERVER_ANALYSIS_PATH/codedog/settings/local.py
    ln -s $TCA_SERVER_PATH/configs/django/local_analysis.py $TCA_SERVER_ANALYSIS_PATH/codedog/settings/local.py

    mkdir -p $TCA_SERVER_FILE_PATH/codedog_file_server/env
    rm -f $TCA_SERVER_FILE_PATH/codedog_file_server/env/local.py
    ln -s $TCA_SERVER_PATH/configs/django/local_file.py $TCA_SERVER_FILE_PATH/codedog_file_server/env/local.py

    rm -f $TCA_SERVER_LOGIN_PATH/apps/settings/local.py
    ln -s $TCA_SERVER_PATH/configs/django/local_login.py $TCA_SERVER_LOGIN_PATH/apps/settings/local.py

    if [ ! -d $NGINX_CONF_PATH ]; then
        LOG_ERROR "[TCAServer] $NGINX_CONF_PATH not exist."
        LOG_WARN "If you installed nginx into other path, you can set change '$TCA_SCRIPT_ROOT/config.sh' "
        LOG_WARN "or set environment variable 'NGINX_CONF_PATH' with actual conf path"
        return 1
    fi

    if [ -f $NGINX_CONF_PATH/tca_8000.conf ]; then
        rm -f $NGINX_CONF_PATH/tca_8000.conf
    fi
    if [ -f $NGINX_CONF_PATH/tca_file_local.conf ]; then
        rm -f $NGINX_CONF_PATH/tca_file_local.conf
    fi
    cp $TCA_SERVER_PATH/configs/nginx/tca_8000.conf $NGINX_CONF_PATH/tca_8000.conf
    cp $TCA_SERVER_PATH/configs/nginx/tca_file_local.conf $NGINX_CONF_PATH/tca_file_local.conf
    # cp $CURRENT_PATH/configs/nginx/tca_file_minio.conf $NGINX_CONF_PATH/tca_file_local.conf
}

function install_server_requirments() {
    LOG_INFO "[TCAServer] Install server dependency packages... [Please wait for a moment.]"
    LOG_INFO "    * TCA Server requirements detail: $TCA_SERVER_CONFIG_PATH/requirements.txt"
    LOG_WARN "    * TCA已配置腾讯云pypi源（https://mirrors.cloud.tencent.com/pypi/simple）进行下载"
    LOG_WARN "    * 若仍无法正常下载或需更新为其他pypi源，请至/root/.pip/pip.conf文件进行调整, 使用目标镜像源地址进行替换"
    use_right_pip " -r $TCA_SERVER_CONFIG_PATH/requirements.txt"
}

function create_tool_link() {
    LOG_INFO "[TCAServer] Create link with gunicorn、celery"
    if [ -f "/usr/local/bin/gunicorn" ]; then
        LOG_INFO "/usr/local/bin/gunicorn exist"
        return 0
    else
        ln -s $PYTHON_PATH/gunicorn /usr/local/bin/gunicorn
    fi
    if [ -f "/usr/local/bin/celery" ]; then
        LOG_INFO "/usr/local/bin/celery exist"
        return 0
    else
        ln -s $PYTHON_PATH/celery /usr/local/bin/celery
    fi   
}

function clean_server_pid() {
    rm -f $TCA_MAIN_GUNICORN_PID_FILE $TCA_ANALYSIS_GUNICORN_PID_FILE $TCA_LOGIN_GUNICORN_PID_FILE $TCA_FILE_GUNICORN_PID_FILE
}

function init_server_config() {
    create_server_dir || error_exit "Create server directory failed"
    copy_server_config || error_exit "Copy server config failed"
    install_server_requirments || error_exit "Install server dependency packages failed"
    create_tool_link || error_exit "Create link failed"
    clean_server_pid
}
