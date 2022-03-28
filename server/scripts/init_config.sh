#!/bin/sh

PYVERSION=`python -c 'import sys; print(sys.version_info.major, sys.version_info.minor)'`
if [ "$PYVERSION" != "3 7" ]; then
    echo "wrong python version";
    exit -1
fi

echo "Start to init server config..."


CURRENT_PATH=$(dirname $(cd "$(dirname "$0")";pwd))
MAIN_PROJECT_PATH=$CURRENT_PATH/projects/main
ANALYSIS_PROJECT_PATH=$CURRENT_PATH/projects/analysis
LOGIN_PROJECT_PATH=$CURRENT_PATH/projects/login
FILE_PROJECT_PATH=$CURRENT_PATH/projects/file
PROJECT_TMP_PATH=$CURRENT_PATH/tmp
PROJECT_LOG_PATH=$CURRENT_PATH/logs
CONFIG_PATH=$CURRENT_PATH/configs

source $CURRENT_PATH/scripts/config.sh

if [ -z "$MYSQL_HOST" ]; then
    echo "Wrong msyql config"
    exit -1
fi

echo "Init directory config"
mkdir -p $MAIN_PROJECT_PATH/log
mkdir -p $ANALYSIS_PROJECT_PATH/log
mkdir -p $LOGIN_PROJECT_PATH/log
mkdir -p $FILE_PROJECT_PATH/log
mkdir -p $PROJECT_LOG_PATH
mkdir -p $PROJECT_TMP_PATH
ln -s $MAIN_PROJECT_PATH/log/ $PROJECT_LOG_PATH/main_log
ln -s $ANALYSIS_PROJECT_PATH/log/ $PROJECT_LOG_PATH/analysis_log
ln -s $LOGIN_PROJECT_PATH/log/ $PROJECT_LOG_PATH/login_log
ln -s $FILE_PROJECT_PATH/log/ $PROJECT_LOG_PATH/file_log

echo "Init server config"
rm $MAIN_PROJECT_PATH/codedog/settings/local.py
ln -s $CURRENT_PATH/configs/django/local_main.py $MAIN_PROJECT_PATH/codedog/settings/local.py

rm $ANALYSIS_PROJECT_PATH/codedog/settings/local.py
ln -s $CURRENT_PATH/configs/django/local_analysis.py $ANALYSIS_PROJECT_PATH/codedog/settings/local.py

mkdir -p $FILE_PROJECT_PATH/codedog_file_server/env
rm $FILE_PROJECT_PATH/codedog_file_server/env/local.py
ln -s $CURRENT_PATH/configs/django/local_file.py $FILE_PROJECT_PATH/codedog_file_server/env/local.py

rm $LOGIN_PROJECT_PATH/apps/settings/local.py
ln -s $CURRENT_PATH/configs/django/local_login.py $LOGIN_PROJECT_PATH/apps/settings/local.py

rm /etc/nginx/conf.d/tca_8000.conf /etc/nginx/conf.d/tca_file_local.conf
ln -s $CURRENT_PATH/configs/nginx/tca_8000.conf /etc/nginx/conf.d/tca_8000.conf
ln -s $CURRENT_PATH/configs/nginx/tca_file_local.conf /etc/nginx/conf.d/tca_file_local.conf
# ln -s $CURRENT_PATH/configs/nginx/tca_file_minio.conf /etc/nginx/conf.d/tca_file_local.conf


function init_db() {
    echo "Start to init db, create database..."
    mysql -u$MYSQL_USER -p$MYSQL_PASSWORD -h$MYSQL_HOST -P$MYSQL_PORT < $CURRENT_PATH/sql/init.sql
    echo "Finish to init db"
}

function init_requirments() {
    echo "Start to install requirement..."
    echo -e "\033[33m-*-*-*-*-*-*-注意-*-*-*-*-*-*-*-"
    echo "如果访问官方pypi源（files.pythonhosted.org）超时或访问失败，可以配置为腾讯云pypi源进行下载，配置方式可以执行以下命令："
    echo "mkdir ~/.pip/ && echo "[global]\nindex-url = https://mirrors.cloud.tencent.com/pypi/simple" >> ~/.pip/pip.conf"
    echo -e "-*-*-*-*-*-*-注意-*-*-*-*-*-*-*-\033[0m"
    pip install -r $CONFIG_PATH/requirements.txt
}

function init_main() {
    echo "Init main db"
    cd $MAIN_PROJECT_PATH
    python manage.py createcachetable
    python manage.py migrate --noinput --traceback
}

function init_analysis() {
    echo "Init analysis db"
    cd $ANALYSIS_PROJECT_PATH
    python manage.py createcachetable
    python manage.py migrate --noinput --traceback
}

function init_login() {
    echo "Init login db"
    cd $LOGIN_PROJECT_PATH
    python manage.py createcachetable
    python manage.py migrate --noinput --traceback
}

function init_file() {
    echo "Init file db"
    cd $FILE_PROJECT_PATH
    python manage.py migrate --noinput --traceback
}

init_db
init_requirments
init_main
init_analysis
init_login
init_file
