#!/bin/sh
# TCA Server服务运行监测脚本（docker-compose启动方式）

echo "[TCAServerHealthCheck] *start detect status of every service*"

function service_detect_for_dockercompose() {
    array=(codeanalysis_nginx codeanalysis_scmproxy codeanalysis_analysis-worker 
    codeanalysis_main-worker codeanalysis_main-beat codeanalysis_main-server 
    redis:5.0.5 codeanalysis_analysis-server codeanalysis_login-server
    mysql:5.7.24 codeanalysis_file-server)
    result=$(docker ps)
    for service in ${array[@]}
    do
        if ! [[ $result =~ $service.* ]]; then
            echo -e "\e[31m❌ container $service failed, please view logs to locate problems\e[0m"
            exit -1
        fi
    done
}

service_detect_for_dockercompose