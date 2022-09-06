#!/bin/bash

CURRENT_SCRIPT_PATH=$( cd "$(dirname ${BASH_SOURCE[0]})"; pwd )
export TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$( cd $(dirname $CURRENT_SCRIPT_PATH); pwd )"}
export TCA_PROJECT_PATH=${TCA_PROJECT_PATH:-"$( cd $(dirname $TCA_SCRIPT_ROOT); pwd )"}

source $TCA_SCRIPT_ROOT/utils.sh
source $TCA_SCRIPT_ROOT/server/_base.sh

CODEDOG_DBUSER=${CODEDOG_DBUSER:-root}
CODEDOG_DBPASSWD=${CODEDOG_DBPASSWD:-'TCA!@#2021'}

function tca_introduction() {
    LOG_INFO "===========================================================" 
    LOG_INFO "                  _______    _____                         "
    LOG_INFO "                 |__   __|  / ____|     /\                 "   
    LOG_INFO "                    | |    | |         /  \                "  
    LOG_INFO "                    | |    | |        / /\ \               "  
    LOG_INFO "                    | |    | |____   / ____ \              "
    LOG_INFO "                    |_|     \_____| /_/    \_\             "
    LOG_INFO "                                                           "         
    LOG_INFO "==========================================================="
    LOG_INFO "| docker-compose 部署说明                                  |"
    LOG_INFO "| 默认部署以下服务                                           |"
    LOG_INFO "| - mysql, redis, nginx                                   |"
    LOG_INFO "| - main-server, main-worker, main-beat                   |"
    LOG_INFO "| - analysis-server, analysis-worker                      |"
    LOG_INFO "| - scmproxy                                              |"
    LOG_INFO "| - login-server                                          |"
    LOG_INFO "| - file-server, file-nginx                               |"
    LOG_INFO "|                                                         |"
    LOG_INFO "| 数据缓存路径                                              |"
    LOG_INFO "| - mysql数据：./.docker_data/mysql                        |"
    LOG_INFO "| - redis数据：./.docker_data/redis                        |"
    LOG_INFO "| - 本地文件数据：./.docker_data/filedata                   |"
    LOG_INFO "|                                                         |"
    LOG_INFO "| 日志缓存路径                                              |"
    LOG_INFO "| - main-server：./.docker_data/logs/main_server/         |"
    LOG_INFO "| - main-worker：./.docker_data/logs/main_worker/         |"
    LOG_INFO "| - main-beat：/.docker_data/logs/main_beat/              |"
    LOG_INFO "| - analysis-server：./.docker_data/logs/analysis_server/ |"
    LOG_INFO "| - analysis-worker：./.docker_data/logs/analysis_worker/ |"
    LOG_INFO "| - scmproxy: ./.docker_data/logs/scmproxy/               |"
    LOG_INFO "| - file-server: ./.docker_data/logs/file-server/         |"
    LOG_INFO "| - file-nginx: ./.docker_data/logs/file-nginx/           |"
    LOG_INFO "| - login-server: ./.docker_data/logs/login-server/       |"
    LOG_INFO "|                                                         |"
    LOG_INFO "==========================================================="
    LOG_INFO "部署文档：https://tencent.github.io/CodeAnalysis/zh/quickStarted/deploySever.html"
    LOG_INFO "Q&A文档：https://tencent.github.io/CodeAnalysis/zh/quickStarted/FAQ.html"
    LOG_INFO ""
}

# 根据架构决定当前选择的镜像
function set_image_with_arch() {
    system_os=$( uname )
    if [ $system_os == "Darwin" ]; then
        sed_command="sed -i.bak -E"
    else
        sed_command="sed -ir -E"
    fi
    current_arch=$( uname -m )
    if [ $current_arch == "aarch64" ] || [ $current_arch == "arm64" ]; then
        $sed_command 's/^([[:space:]]*)(image: mysql)/\1\# \2/' $TCA_PROJECT_PATH/docker-compose.yml
        $sed_command 's/^([[:space:]]*)\#[[:space:]]*(image: mariadb:10)/\1\2/' $TCA_PROJECT_PATH/docker-compose.yml
    else
        $sed_command 's/^([[:space:]]*)\#[[:space:]]*(image: mysql:5)/\1\2/' $TCA_PROJECT_PATH/docker-compose.yml
        $sed_command 's/^([[:space:]]*)[[:space:]]*(image: mariadb:10)/\1\# \2/' $TCA_PROJECT_PATH/docker-compose.yml
    fi
}

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
         python manage.py loadlibs all --dirname open_source_toollib --ignore-auth; \
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

function stop_all_services() {
    docker-compose stop
}

function deploy_all_services() {
    cd $TCA_PROJECT_PATH
    set_image_with_arch
    start_db || error_exit "start db failed"
    init_db || error_exit "init db failed"
    init_file || error_exit "init file server failed"
    init_login || error_exit "init login server failed"
    init_analysis || error_exit "init analysis server failed"
    init_main || error_exit "init main server failed"
    start_all_services
    tca_introduction
}


function tca_docker_compose_main() {
    command=$1
    case $command in
        deploy)
            LOG_INFO "Deploy tca docker-compose"
            deploy_all_services
        ;;
        start)
            LOG_INFO "Start tca docker-compose"
            start_all_services
        ;;
        stop)
            LOG_INFO "Stop tca docker-compose"
            stop_all_services
        ;;
        build)
            LOG_INFO "Build tca image"
            docker-compose build main-server analysis-server file-server login-server scmproxy client
        ;;
        *)
            LOG_ERROR "'$command' not support."
            exit 1
    esac
}

