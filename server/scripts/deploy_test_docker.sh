#!/bin/bash
# TCA Server部署监测脚本（docker-compose启动方式）
# 检测步骤为：可用磁盘/内存检测 -> 镜像下载源检测 -> docker/docker-compose命令检测 -> docker-compose版本检测

echo "start detect every dependency for tca server..."

# 检验可用磁盘空间
function diskspace_detect() {
    echo "[TCAServerDependencyCheck] *make sure have enough disk space*"
    ret=$(df -hl |grep /$)
    split_result=(${ret// / })
    disk_space="${split_result[3]}"
    if ! [[ $disk_space =~ .*G$ ]]; then
        echo -e "\033[33m⚠️ your disk space $disk_space is less than 10G; please make sure you have enough space to supprt TCA\033[0m"
    fi

    split_space=(${disk_space//G/ })
    number_of_gb="${split_space[0]}"
    if ! [[ $number_of_gb =~ ^[0-9]{2,}.* ]]; then
        echo -e "\033[33m⚠️ your disk space $disk_space is less than 10G; please make sure you have enough space to supprt TCA\033[0m"
    fi
}

# 检验可用内存
function memory_detect() {
    echo "[TCAServerDependencyCheck] *make sure have enough memory*"
    result=$(free)
    split_result=(${result// / })
    memory_avaliable=${split_result[12]}  # 可用内存在切分后的数组中的第13处
    div="1048576"
    memory_avaliable_gb=$(awk '{print $1/$2}' <<<"${memory_avaliable} ${div}")  # 转换为gb
    if ! [[ $memory_avaliable_gb =~ ^([2-9]|([0-9]{2,})).* ]]; then
        echo -e "\033[33m⚠️ your avaliable memory $memory_avaliable_gb G is less than 2G; please make sure you have enough memory to supprt TCA\033[0m"
    fi
}

# 检验docker是否安装
function docker_command_detect() {
    echo "[TCAServerDependencyCheck] *make sure command docker exist*"
    if ! command -v docker &> /dev/null
    then
        echo -e "\e[31m❌ command docker not found, please install docker first then start TCA\e[0m"
        exit -1
    fi
}

# 检验docker-compose是否安装
function dockercompose_command_detect() {
    echo "[TCAServerDependencyCheck] *make sure command docker-compose exist*"
    if ! command -v docker-compose &> /dev/null
    then
        echo -e "\e[31m❌ command docker-compose not found, please install docker-compose first then start TCA\e[0m"
        exit -1
    fi
}

# 检验docker-compose版本
# function dockercompose_version_detect() {
#     echo "[TCAServerDependencyCheck] *make sure docker-compose have right version*"
#     result=$(docker-compose version)
#     split_result=(${result//v/ })
#     version="${split_result[3]}"
#     if ! [[ $version =~ ^[2-9].* ]]; then
#         echo -e "\e[31m❌ version of  docker-compose is $version right now, please install docker-compose 2.0 or above\e[0m"
#         exit -1 
#     fi
# }

diskspace_detect
memory_detect
docker_command_detect
dockercompose_command_detect
# dockercompose_version_detect