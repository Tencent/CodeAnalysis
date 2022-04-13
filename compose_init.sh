#!/bin/sh

CURRENT_PATH=$(dirname $(cd "$(dirname "$0")";pwd))
CODEDOG_DBUSER=${CODEDOG_DBUSER:-root}
CODEDOG_DBPASSWD=${CODEDOG_DBPASSWD:-'TCA!@#2021'}

function start_db() {
    docker-compose up --force-recreate -d mysql redis
}

function init_db() {
    db_container=$(docker-compose ps | grep mysql | awk '{print $1}')

   docker-compose exec mysql /bin/bash -c \
        "printf 'wait db [DB default password: TCA!@#2021]\n'; \
         until \$(MYSQL_PWD=${CODEDOG_DBPASSWD} mysql -u${CODEDOG_DBUSER} -e '\s' > /dev/null 2>&1); do \
            printf '.' && sleep 1; \
         done; echo
        "
}

# 文件服务器初始化
function init_file() {
    mkdir -p $CURRENT_PATH/server/projects/file
    docker-compose up -d file-server 
    docker-compose exec file-server bash -c \
        "python manage.py migrate --noinput --traceback"
}

# 登陆服务器初始化
function init_login() {
    mkdir -p $CURRENT_PATH/server/projects/login
    docker-compose up -d login-server
    docker-compose exec login-server bash -c \
        "python manage.py migrate --noinput --traceback; \
         python manage.py createcachetable; \
         python manage.py initializedb;
        "
}

# Main服务器初始化
function init_main() {
    mkdir -p $CURRENT_PATH/server/projects/main/log
    docker-compose up -d main-server
    docker-compose exec main-server /bin/bash -c \
        "python manage.py migrate --noinput --traceback; \
         python manage.py createcachetable; \
         python manage.py initializedb_open; \
         python manage.py initialize_exclude_paths; \
         python manage.py loadcheckers all --dirname open_source; \
         python manage.py loadpackages all --dirname open_source_package;
        "
}

# Analysis服务器初始化
function init_analysis() {
    mkdir -p $CURRENT_PATH/server/projects/analysis/log
    docker-compose up -d analysis-server
    docker-compose exec analysis-server /bin/bash -c \
        "python manage.py migrate --noinput --traceback; \
         python manage.py createcachetable; \
         python manage.py initialuser; \
        "
}

function start_all_services() {
    docker-compose up -d
}

sh $CURRENT_PATH/server/scripts/deploy_test_docker.sh
start_db
init_db
init_file
init_login
init_analysis
init_main
start_all_services
sh $CURRENT_PATH/server/scripts/service_test_docker.sh