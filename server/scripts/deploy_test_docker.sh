#!/bin/sh
# TCA Server部署监测脚本（docker-compose启动方式）
# 检测步骤为：可用磁盘/内存检测 -> 镜像下载源检测 -> docker/docker-compose命令检测 -> docker-compose版本检测

echo "start detect every dependcy for tca server..."

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

# 镜像下载源检测
function network_detect() {
    echo "[TCAServerDependcyCheck] *make sure docker download source is avaliable*"
    timeout_time=60
    # 监测镜像源网络状态
    starttime=`date +'%Y-%m-%d %H:%M:%S'`
    result=`timeout $timeout_time docker pull mysql`
    endtime=`date +'%Y-%m-%d %H:%M:%S'`
    start_seconds=$(date --date="$starttime" +%s);
    end_seconds=$(date --date="$endtime" +%s);
    running_time=$((end_seconds-start_seconds))
    if [[ $running_time > $timeout_time ]]; then
        echo -e "\e[31m❌ docker pull mysql timed out, please check your network or docker image download source\e[0m"
        exit -1
    fi
}

# 检验docker是否安装
function docker_command_detect() {
    echo "[TCAServerDependcyCheck] *make sure command docker exist*"
    if ! command -v docker &> /dev/null
    then
        echo -e "\e[31m❌ command docker not found, please install docker first then start TCA\e[0m"
        exit -1
    fi
}

# 检验docker-compose是否安装
function dockercompose_command_detect() {
    echo "[TCAServerDependcyCheck] *make sure command docker-compose exist*"
    if ! command -v docker-compose &> /dev/null
    then
        echo -e "\e[31m❌ command docker-compose not found, please install docker-compose first then start TCA\e[0m"
        exit -1
    fi
}

# 检验docker-compose版本
function dockercompose_version_detect() {
    echo "[TCAServerDependcyCheck] *make sure docker-compose have right version*"
    result=$(docker-compose version)
    split_result=(${result//v/ })
    version="${split_result[3]}"
    if ! [[ $version =~ ^[2-9].* ]]; then
        echo -e "\e[31m❌ version of  docker-compose is $version right now, please install docker-compose 2.0 or above\e[0m"
        exit -1 
    fi
}

diskspace_detect
memory_detect
network_detect
docker_command_detect
dockercompose_command_detect
dockercompose_version_detect