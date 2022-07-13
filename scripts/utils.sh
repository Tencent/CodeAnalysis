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

# 安装基础软件：wget、curl、unzip
function install_base() {
	LINUX_OS=$( get_linux_os )

	case "$LINUX_OS" in
        centos|rhel|sles|tlinux)
            yum install -y wget curl unzip
        ;;
        ubuntu|debian|raspbian)
            apt install -y wget curl unzip
        ;;
        *)
            LOG_ERROR "$LINUX_OS not supported."
            exit 1
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
        kill -15 `cat $pid_file` >/dev/null 2>&1 
    fi
}

function force_kill() {
    proc_name=$1
    pids=$( get_target_process "$proc_name" )
    if [ ! -n "$pids" ]; then  
        return 0  
    fi
    kill -9 $pids
}
