#!/bin/bash

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

function ping_celery() {
    celery -A codedog inspect ping -d celery@$HOSTNAME 2>&1 >/dev/null
    echo $?
}

function check_celery_healthy() {
    result=0
    for((i=1;i<=3;i++)); do
        result=`ping_celery`
	echo "check celery result: $result"
        if [ "$result" == "0" ]; then
            break
        fi
        sleep 10
    done

    if [ "$result" != "0" ]; then
        pids=`get_target_process 'celery -A codedog'`
        kill -HUP $pids
    fi
}

check_celery_healthy