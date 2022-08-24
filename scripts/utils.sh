#!/bin/bash

function LOG_INFO() {
	echo -e "\033[32m[$(date "+%Y/%m/%d %H:%M:%S")] [INFO]: $@\033[0m"
}

function LOG_WARN() {
	echo -e "\033[33m[$(date "+%Y/%m/%d %H:%M:%S")] [WARN]: $@\033[0m"
}

function LOG_ERROR() {
    echo ""
	echo -e "\033[31m[$(date "+%Y/%m/%d %H:%M:%S")] [ERROR]: $@\033[0m"
	echo -e "\033[31m__________________________________________________________________________________________\033[0m"
}

# 获取操作系统
function get_linux_os() {
	linux_os=""
	if [ -r /etc/os-release ]; then
		linux_os="$(. /etc/os-release && echo "$ID")"
	fi
	echo "$linux_os"
}

function error_exit() {
    LOG_ERROR "$1" 1>&2
    exit 1
}

function command_exists() {
	command -v "$@" > /dev/null 2>&1
}

function command_normal() {
	"$@" > /dev/null 2>&1
}

# 安装基础软件：wget、curl、unzip git subversion
function install_base() {
	LINUX_OS=$( get_linux_os )

	case "$LINUX_OS" in
        centos|rhel|sles|tlinux|tencentos)
            yum install -q -y wget curl unzip git subversion >/dev/null
        ;;
        ubuntu|debian|raspbian)
            apt-get install -qq -y wget curl unzip git subversion >/dev/null
        ;;
        *)
            LOG_WARN "$LINUX_OS default using yum"
            yum install -q -y wget curl unzip git subversion >/dev/null || error_exit "$LINUX_OS install base failed"
        ;;
    esac
}

function get_target_process(){
	proc_name=$1
	pids=`ps -ef | grep "$proc_name" | grep -v grep | awk '{print $2}'`
	echo $pids
}

function check_target_process_exist() {
	proc_name=$1
	pids=$( get_target_process "$proc_name" )
	ret=""
	if [ ! -n "$pids" ]; then  
        ret="false"
	else
		ret="true"
    fi
	echo "$ret"
}

function kill_by_pid_file() {
    pid_file=$1
    if [ -f "$pid_file" ]; then
        kill -15 `cat $pid_file` &>/dev/null
    fi
}

function normal_kill() {
    proc_name=$1
    pids=$( get_target_process "$proc_name" )
    if [ ! -n "$pids" ]; then  
        return 0  
    fi
    kill $pids &>/dev/null
}

function force_kill() {
    proc_name=$1
    pids=$( get_target_process "$proc_name" )
    if [ ! -n "$pids" ]; then  
        return 0  
    fi
    kill -9 $pids &>/dev/null
}

### 检验软链文件是否存在，存在则询问是否删除 ###
function check_ln_file() {
    file=$1
    new_soft_link=$2
    if [ -f $file ]; then
        LOG_INFO "$file need to be removed, TCA will replaced it with new soft link file: $new_soft_link"
        read -p "please enter: [Y/N]" result
        case $result in
            [Yy])
                rm -f $file
            ;;
            [Nn])
                LOG_WARN "soft link create failed."
            ;;
            *)
                LOG_ERROR "Invalid input. Stop."
                exit 1
            ;;
        esac
    fi
    
}

### 核验pip版本 ###
### 保证使用python3.7对应的pip安装依赖 ###
function use_right_pip() {
    params=$1
    neccessary_pip_py_verson="3.7"
    if command_exists pip; then
        pip_py_version=$(pip -V |awk '{print $6}' |cut -f 1 -d ')')
        if [ $pip_py_version == $neccessary_pip_py_verson ]; then
            pip install $params
        fi
    elif command_exists pip3; then
        pip3_py_version=$(pip3 -V |awk '{print $6}' |cut -f 1 -d ')')
        if [ $pip3_py_version == $neccessary_pip_py_verson ]; then
            pip3 install $params
        fi
    else
        error_exit "Please make sure pip's python version is 3.7! otherwise TCA CAN'T be used"
    fi
}

#--------------------------------------------
# 前置校验通用方法
#--------------------------------------------

### 前置校验 ###
function pre_check() {
    root_check
    os_digits_check
    os_version_check
    http_proxy_check
}

### 校验是否为root权限 ### 
function root_check() {
    if [ "$(whoami)" != "root" ]; then
        error_exit "Please use TCA init script under root privilege."
    fi
}

### 校验系统位数 ### 
function os_digits_check() {
    is64bit=$(getconf LONG_BIT)
    if [ $is64bit != "64" ]; then
        error_exit "non 64 digits os CAN'T use TCA."
    fi
}

### 校验系统及版本 ###
### centos版本需为7及以上，ubuntu需为18.04及以上 ###
### 若其他系统版本不可用，可至https://github.com/Tencent/CodeAnalysis发出issue ###
function os_version_check() {
    if [ -s "/etc/redhat-release" ]; then
        centos_version=$(cat /etc/redhat-release | grep -iE 'release [1-7]\.' | grep -iE 'centos|Red Hat')
        if [ "$centos_version" ]; then
            LOG_WARN "current centOS version is $centos_version, we recommend you use 7 or above."
        fi
    elif [ -s "/etc/issue" ]; then
        ubuntu_version=$(cat /etc/issue |grep Ubuntu |awk '{print $2}')
        min_version="18.03"
        if [ "$ubuntu_version" ]; then
            if [[ $ubuntu_version < $min_version ]]; then
                LOG_WARN "current Ubuntu version is $ubuntu_version, we recommend you use 18.04 or above."
            fi
        fi
    fi
}

### 监测是否设置网络代理 ###
function http_proxy_check() {
    http_proxy=$HTTP_PROXY
    https_proxy=$HTTPS_PROXY
    no_proxy=$no_proxy
    if [ $http_proxy ] || [ $https_proxy ]; then
        if [[ $no_proxy != *"127.0.0.1"* ]]; then
            LOG_INFO "TCA script will unset HTTP_PROXY/HTTPS_PROXY or set NO_PROXY，otherwise TCA will be unavaliable."
            LOG_INFO "1. unset HTTP_PROXY/HTTPS_PROXY. <please note after unset, your node may lose access to Extranet> "
            LOG_INFO "2. set NO_PROXY=127.0.0.1, cause TCA server is deployed on http:/127.0.0.1:8000/"
            LOG_INFO "3. do nothing"
            read -p "please enter: [1/2/3]" result
            case $result in
                [1])
                    if [ $http_proxy ]; then
                        unset HTTP_PROXY
                    fi
                    if [ $https_proxy ]; then
                        unset HTTPS_PROXY
                    fi
                    ;;
                [2])
                    export no_proxy="$no_proxy,127.0.0.1"
                    ;;
                [3])
                    LOG_INFO "do nothing about PROXY setting"
                    return 1
                    ;;
                *)
                    LOG_ERROR "Invalid input. Stop."
                    exit 1
                    ;;
            esac
        fi
    fi
}