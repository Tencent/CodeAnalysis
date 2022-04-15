#!/bin/bash
# TCA Server服务运行监测脚本

echo "[TCAServerHealthCheck] *start detect status of every service*"

function delete_txt_file() {
    rm -rf $1/*.txt
}

function main_server_detect() {
    current_path=$(dirname $(cd "$(dirname "$0")";pwd))
    file_path="$current_path/projects/main/apps/base"
    delete_txt_file $file_path
    current_timestamp=`date '+%s'`
    file_path="$file_path/$current_timestamp.txt"
    target="http://0.0.0.0:8000/main/healthcheck/?file_name=$current_timestamp"

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