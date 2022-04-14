#!/bin/bash
# TCA Server服务运行监测脚本

echo "[TCAServerHealthCheck] *start detect status of every service*"


function service_detect() {
    array=("http://0.0.0.0:8000/main" "http://127.0.0.1:8002" "http://127.0.0.1:8003" "http://127.0.0.1:8004")
    for service in ${array[@]}
    do
        timeout=1
        target="$service/healthcheck/"
        ret_code=$(curl -I -s --connect-timeout ${timeout} ${target} -w %{http_code} | tail -n1)
        if [[ "x$ret_code" == "x200" ]]; then
            echo "service $service health check succeed"
        elif [[ "x$ret_code" == "x503" ]]; then
            echo -e "\e[31m❌ service $service failed, reason might be db connection fail or database/table initialization fail\e[0m"
            exit -1
        elif [[ "x$ret_code" == "x424" ]]; then
            echo -e "\e[31m❌ service $service failed, reason might be celery has not started\e[0m"
            exit -1
        else
            echo -e "\e[31m❌ service $service failed, please view logs to locate the issue\e[0m"
            exit -1
        fi
    done    
}

service_detect