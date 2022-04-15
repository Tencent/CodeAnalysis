#!/bin/bash
# TCA Server服务运行监测脚本

echo "[TCAServerHealthCheck] *start detect status of every service*"

function delete_txt_file() {
    rm -rf $1/healthcheck_*.txt
}

function main_server_detect() {
    current_path=$(dirname $(cd "$(dirname "$0")";pwd))
    file_path="$current_path/projects/main"
    delete_txt_file $file_path
    current_timestamp=`date '+%s'`
    file_path="$file_path/$current_timestamp.txt"
    target="http://0.0.0.0:8000/main/healthcheck/?file_name=$current_timestamp"
    ret_code=$(curl -I -s --connect-timeout 1 ${target} -w %{http_code} | tail -n1)

    if [[ "x$ret_code" == "x200" ]]; then
        echo "[TCAServerHealthCheck] *service main db check pass*"
    elif [[ "x$ret_code" == "x503" ]]; then
        echo -e "\e[31m❌ service main failed, reason might be db connection fail or database/table initialization fail\e[0m"
        exit -1
    else
        echo -e "\e[31m❌ service main failed, please view logs to locate the issue\e[0m"
        exit -1
    fi

    for ((i=0; i<3; i++));
    do
        sleep 1
        if [ -f $file_path ]; then
            echo "[TCAServerHealthCheck] *service main celery check pass*"
            return
        fi
    done

    echo -e "\e[31m❌ service main failed, reason might be celery has not started\e[0m"
    exit -1
}

function analysis_server_detect() {
    current_path=$(dirname $(cd "$(dirname "$0")";pwd))
    file_path="$current_path/projects/analysis"
    delete_txt_file $file_path
    current_timestamp=`date '+%s'`
    file_path="$file_path/$current_timestamp.txt"
    target="http://127.0.0.1:8002/healthcheck/?file_name=$current_timestamp"
    ret_code=$(curl -I -s --connect-timeout 1 ${target} -w %{http_code} | tail -n1)

    if [[ "x$ret_code" == "x200" ]]; then
        echo "[TCAServerHealthCheck] *service analysis db check pass*"
    elif [[ "x$ret_code" == "x503" ]]; then
        echo -e "\e[31m❌ service analysis failed, reason might be db connection fail or database/table initialization fail\e[0m"
        exit -1
    else
        echo -e "\e[31m❌ service analysis failed, please view logs to locate the issue\e[0m"
        exit -1
    fi

    for ((i=0; i<3; i++));
    do
        sleep 1
        if [ -f $file_path ]; then
            echo "[TCAServerHealthCheck] *service analysis celery check pass*"
            return
        fi
    done

    echo -e "\e[31m❌ service analysis failed, reason might be celery has not started\e[0m"
    exit -1
}

function login_server_detect() {
    target="http://127.0.0.1:8003/api/v1/login/healthcheck/"
    ret_code=$(curl -I -s --connect-timeout 1 ${target} -w %{http_code} | tail -n1)

    if [[ "x$ret_code" == "x200" ]]; then
        echo "[TCAServerHealthCheck] *service login db check pass*"
    elif [[ "x$ret_code" == "x503" ]]; then
        echo -e "\e[31m❌ service login failed, reason might be db connection fail or database/table initialization fail\e[0m"
        exit -1
    else
        echo -e "\e[31m❌ service login failed, please view logs to locate the issue\e[0m"
        exit -1
    fi
}

function file_server_detect() {
    target="http://127.0.0.1:8804/healthcheck/"
    ret_code=$(curl -I -s --connect-timeout 1 ${target} -w %{http_code} | tail -n1)

    if [[ "x$ret_code" == "x200" ]]; then
        echo "[TCAServerHealthCheck] *service file db check pass*"
    elif [[ "x$ret_code" == "x503" ]]; then
        echo -e "\e[31m❌ service file failed, reason might be db connection fail or database/table initialization fail\e[0m"
        exit -1
    else
        echo -e "\e[31m❌ service file failed, please view logs to locate the issue\e[0m"
        exit -1
    fi
}


#function service_detect() {
#    array=("http://0.0.0.0:8000/main" "http://127.0.0.1:8002" "http://127.0.0.1:8003" "http://127.0.0.1:8004")
#    for service in ${array[@]}
#    do
#        timeout=1
#        target="$service/healthcheck/"
#        ret_code=$(curl -I -s --connect-timeout ${timeout} ${target} -w %{http_code} | tail -n1)
#        if [[ "x$ret_code" == "x200" ]]; then
#            echo "service $service health check succeed"
#        elif [[ "x$ret_code" == "x503" ]]; then
#            echo -e "\e[31m❌ service $service failed, reason might be db connection fail or database/table initialization fail\e[0m"
#            exit -1
#        elif [[ "x$ret_code" == "x424" ]]; then
#            echo -e "\e[31m❌ service $service failed, reason might be celery has not started\e[0m"
#            exit -1
#        else
#            echo -e "\e[31m❌ service $service failed, please view logs to locate the issue\e[0m"
#            exit -1
#        fi
#    done
#}

main_server_detect
analysis_server_detect
login_server_detect
file_server_detect