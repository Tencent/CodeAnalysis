#!/bin/sh
# TCA Server部署检测脚本
# 检测步骤为：python命令检测 -> python版本检测 -> 依赖完整度检测 -> celery命令检测 -> gunicorn命令检测 -> 配置完整度检测 -> redis/mysql登陆检测 -> 可用磁盘/内存检测 -> pip下载源检测

CURRENT_PATH=$(dirname $(cd "$(dirname "$0")";pwd))
SERVER_REQUIREMENTS_PATH=$CURRENT_PATH/configs/requirements.txt
SERVER_CONFIG_PATH=$CURRENT_PATH/scripts/config.sh

echo "start detect every dependcy for tca server..."

# 校验python命令是否存
function python_command_detect() {
    echo "[TCAServerDependcyCheck] *make sure command python exist*"
    if ! command -v python &> /dev/null
    then
        echo -e "\e[31m❌ command python not found, please install python first then start TCA\e[0m"
        exit -1
    fi
}

# 校验python版本是否为3.7.x及
function python_version_detect() {
    echo "[TCAServerDependcyCheck] *make sure python has right version*"
    result=$(python --version |grep "^Python 3.7.")
    if [[ $result == "" ]];
    then
        echo -e "\e[31m❌ wrong python version, the version must be 3.7.x\e[0m"
        exit -1
    fi
}

# 检验依赖是否完整
function dependcy_detect() {
    echo "[TCAServerDependcyCheck] *make sure every package is installed in right version*"
    while read line
    do
        # 过滤掉不含==的行
        if ! [[ $line =~ "==" ]]; then
            continue
        fi
        # 获得各行依赖包名称及版本  
        array=(${line//==/ })
        package="${array[0]}"
        version="${array[1]}"
        # 校验依赖包是否安装且版本是否正确
        result=$(pip show $package --version |grep "^Version: $version")
        if [[ $result == "" ]]; then
            echo -e "\e[31m❌ package $package not installed or has wrong version; please install [$package: $version]\e[0m"
            exit -1
        fi
    done < $SERVER_REQUIREMENTS_PATH
}

# 校验celery命令是否存
function celery_command_detect() {
    echo "[TCAServerDependcyCheck] *make sure command celery exist*"
    if ! command -v celery &> /dev/null
    then
        echo -e "\e[31m❌ command celery not found, please install celery then soft link to /usr/local/bin/celery\e[0m"
        exit -1
    fi
}

# 校验gunicorn命令是否存
function gunicorn_command_detect() {
    echo "[TCAServerDependcyCheck] *make sure command gunicorn exist*"
    if ! command -v celery &> /dev/null
    then
        echo -e "\e[31m❌ command gunicorn not found, please install gunicorn then soft link to /usr/local/bin/gunicorn\e[0m"
        exit -1
    fi
}

# 检验配置信息是否完整
function config_detect() {
    echo "[TCAServerDependcyCheck] *make sure enter neccessary configuration*"
    while read line
    do
        # 仅监测必填配置项
        if ! [[ $line =~ ^(MYSQL_HOST|MYSQL_USER|MYSQL_PASSWORD|REDIS_HOST|REDIS_PASSWD).* ]]; then
            continue
        fi
        # 获得配置项内容
        array=(${line//==/ })
        config_key="${array[0]}"
        config_value="${array[1]}"
        if [[ $config_value == "" ]]; then
            echo -e "\e[31m❌ please enter configuration [$config_key: ]\e[0m"
            exit -1
        fi
    done < $SERVER_CONFIG_PATH
}

# 检验根据配置信息能否正常访问mysql
function mysql_login_detect() {
    echo "[TCAServerDependcyCheck] *make sure mysql configuration is correct*"
    if [[ $MYSQL_PORT == "" ]]; then
        MYSQL_PORT="3306"
    fi
    ret=$(mysqladmin -u$MYSQL_USER -p$MYSQL_PASSWORD --host=$MYSQL_HOST --port=$MYSQL_PORT status)
    if [[ $ret == "" ]]; then
        echo -e "\e[31m❌ your configuration for mysql is wrong, please check MYSQL_[HOST|PORT|USER|PASSWORD] in config.sh file\e[0m"
        exit -1
    fi      
}

# 检验根据配置信息能否正常访问redis
function redis_login_detect() {
    echo "[TCAServerDependcyCheck] *make sure redis configuration is correct*"
    ret=$(redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWD exists key)
    if [[ $ret == "NOAUTH Authentication required." ]]; then
        echo -e "\e[31m❌ your password configered for redis is wrong, please check REDIS_PASSWD in config.sh file\e[0m"
        exit -1
    elif [[ $ret == "" ]]; then
        echo -e "\e[31m❌ your HOST/PORT configered for redis is wrong, please check REDIS_[HOST|PORT] in config.sh file\e[0m"
        exit -1
    fi
}

# 检验磁盘空间
function diskspace_detect() {
    echo "[TCAServerDependcyCheck] *make sure have enough disk space*"
    result=$(du -sh /)
    split_result=(${result// / })
    disk_space="${split_result[0]}"
    if ! [[ $disk_space =~ .*G$ ]]; then
        echo -e "\e[31m❌ your disk space $disk_space is less than 10G; please make sure you have enough space to supprt TCA\e[0m"
        exit -1
    fi
    split_space=(${disk_space//G/ })
    number_of_gb="${split_space[0]}"
    if ! [[ $number_of_gb =~ ^[0-9]{2,}.* ]]; then
        echo -e "\e[31m❌ your disk space $disk_space is less than 10G; please make sure you have enough space to supprt TCA\e[0m"
        exit -1
    fi
}

# 检验内存
function memory_detect() {
    echo "[TCAServerDependcyCheck] *make sure have enough memory*"
    result=$(free)
    split_result=(${result// / })
    memory_avaliable=${split_result[12]}  # 可用内存在切分后的数组中的第13处
    div="1048576"
    memory_avaliable_gb=$(awk '{print $1/$2}' <<<"${memory_avaliable} ${div}")  # 转换为gb
    if ! [[ $memory_avaliable_gb =~ ^([2-9]|([0-9]{2,})).* ]]; then
        echo -e "\e[31m❌ your avaliable memory $memory_avaliable_gb G is less than 2G; please make sure you have enough memory to supprt TCA\e[0m"
        exit -1
    fi
}

# 检验下载源网络通畅，包括镜像源及pip下载源
function network_detect() {
    echo "[TCAServerDependcyCheck] *make sure have pip download source is avaliable*"
    timeout_time=60
    # 监测pip下载源网络状态
    starttime=`date +'%Y-%m-%d %H:%M:%S'`
    result=`timeout $timeout_time pip install Django`
    endtime=`date +'%Y-%m-%d %H:%M:%S'`
    start_seconds=$(date --date="$starttime" +%s);
    end_seconds=$(date --date="$endtime" +%s);
    running_time=$((end_seconds-start_seconds))
    if [[ $running_time > $timeout_time ]]; then
        echo -e "\e[31m❌ pip install timed out, please check your network or pip download source\e[0m"
        exit -1
    fi
}

python_command_detect
python_version_detect
dependcy_detect
celery_command_detect
gunicorn_command_detect
config_detect
mysql_login_detect
redis_login_detect
diskspace_detect
memory_detect
network_detect