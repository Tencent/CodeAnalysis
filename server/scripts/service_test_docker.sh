#!/bin/bash
# TCA Server服务运行监测脚本（docker-compose启动方式）

echo "[TCAServerHealthCheck] *start detect status of every service*"

function service_detect_for_dockercompose() {
    array=(codeanalysis_scmproxy tca-analysis nginx tca-main
           redis codeanalysis_login-server
           codeanalysis_file-server mysql
    )
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