#!/bin/bash
# TCA Server服务运行监测脚本

echo "[TCAServerHealthCheck] *start detect status of every service*"

MAIN_CELERY_STATUS=0
ANALYSIS_CELERY_STATUS=0

function delete_txt_file() {
    rm -rf $1/healthcheck_*.txt
}

function main_server_detect() {
    current_path=$(dirname $(cd "$(dirname "$0")";pwd))
    file_path="$current_path/projects/main"
    delete_txt_file $file_path
    current_timestamp=`date '+%s'`
    file_path="$file_path/healthcheck_$current_timestamp.txt"
    target="http://0.0.0.0:8000/main/healthcheck/?file_name=$current_timestamp"
    ret_code=$(curl -I -s --connect-timeout 1 ${target} -w %{http_code} | tail -n1)

    if [[ "x$ret_code" == "x200" ]]; then
        echo "[TCAServerHealthCheck] *service main db check pass*"
    elif [[ "x$ret_code" == "x503" ]]; then
        echo -e "\e[31m❌ service main failed, reason might be db connection fail or database/table initialization fail\e[0m"
        exit -1
    else
        echo -e "\e[31m❌ nginx or service main failed, please reload nginx or view logs to locate the issue\e[0m"
        exit -1
    fi

    for ((i=0; i<3; i++));
    do
        sleep 1
        if [ -f $file_path ]; then
            MAIN_CELERY_STATUS=1
            echo "[TCAServerHealthCheck] *service main celery check pass*"
            return
        fi
    done
}

function analysis_server_detect() {
    current_path=$(dirname $(cd "$(dirname "$0")";pwd))
    file_path="$current_path/projects/analysis"
    delete_txt_file $file_path
    current_timestamp=`date '+%s'`
    file_path="$file_path/healthcheck_$current_timestamp.txt"
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
            ANALYSIS_CELERY_STATUS=1
            echo "[TCAServerHealthCheck] *service analysis celery check pass*"
            return
        fi
    done
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

function celery_status_detect() {
    if [[ $MAIN_CELERY_STATUS == 1 ]] && [[ $ANALYSIS_CELERY_STATUS == 1 ]]; then
        return
    fi
    echo "Start to detect celery status, this process may take 10 seconds, please wait patiently...\n"
    b=""
    i=0
    while [[ $i -le 100 ]]
    do
      printf "[%-50s] %d%% \r" "$b" "$i";
      sleep 0.2
      ((i=i+2))
      b+="#"
      main_ret=$(ps -aux |grep -c main_celery_worker)
      analysis_ret=$(ps -aux |grep -c analysis_celery_worker)
      if [[ $main_ret -gt 1 ]] && [[ $main_ret -gt 1 ]]; then
        echo ""
        echo "[TCAServerHealthCheck] *celery has started*"
        return
      fi
    done

    echo ""
    echo -e "\e[31m❌ celery启动异常，为确保TCA能够正常进行扫描，请查阅server/projects/main/log/main_celery.log、server/projects/analysis/log/analysis_celery.log等日志文件定位问题并处理e[0m"
    echo -e "\e[31m❌ 若无法解决，请前往github提出issue并附带日志截图\e[0m"
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