#!/bin/sh

echo "Check python version..."
PYVERSION=`python -c 'import sys; print(sys.version_info.major, sys.version_info.minor)'`
if [ "$PYVERSION" != "3 7" ]; then
    echo "❌ Wrong python version";
    exit -1
fi

echo "Check celery command..."
if ! command -v celery &> /dev/null
then
    echo "❌ celery could not be found"
    exit -1
fi

echo "Check gunicorn command..."
if ! command -v gunicorn &> /dev/null
then
    echo "❌ gunicorn could not be found"
    exit -1
fi

export CURRENT_PATH=$(dirname $(cd "$(dirname "$0")";pwd))
export PROJECT_TMP_PATH=$CURRENT_PATH/tmp
export PROJECT_LOG_PATH=$CURRENT_PATH/logs
export MAIN_PROJECT_PATH=$CURRENT_PATH/projects/main
export ANALYSIS_PROJECT_PATH=$CURRENT_PATH/projects/analysis
export LOGIN_PROJECT_PATH=$CURRENT_PATH/projects/login
export FILE_PROJECT_PATH=$CURRENT_PATH/projects/file
export SCMPROXY_PROJECT_PATH=$CURRENT_PATH/projects/scmproxy

main_gunicorn_pid_file=$MAIN_PROJECT_PATH/main-master.pid
main_gunicorn_conf_file=$MAIN_PROJECT_PATH/main.gunicorn.conf.py
analysis_gunicorn_pid_file=$ANALYSIS_PROJECT_PATH/analysis-master.pid
analysis_gunicorn_conf_file=$ANALYSIS_PROJECT_PATH/analysis.gunicorn.conf.py
login_gunicorn_pid_file=$LOGIN_PROJECT_PATH/login-master.pid
login_gunicorn_conf_file=$LOGIN_PROJECT_PATH/login.gunicorn.conf.py
file_gunicorn_pid_file=$FILE_PROJECT_PATH/file-master.pid
file_gunicorn_conf_file=$FILE_PROJECT_PATH/file.gunicorn.conf.py
main_celery_worker_pid_file=$PROJECT_TMP_PATH/main_celery_worker.pid
main_celery_beat_pid_file=$PROJECT_TMP_PATH/main_celery_beat.pid
analysis_celery_worker_pid_file=$PROJECT_TMP_PATH/analysis_celery_worker.pid
main_celery_worker_log=$MAIN_PROJECT_PATH/log/main_celery.log
main_celery_beat_log=$MAIN_PROJECT_PATH/log/main_beat.log
analysis_celery_worker_log=$ANALYSIS_PROJECT_PATH/log/analysis_celery.log


echo "Start configs..."
source $CURRENT_PATH/scripts/config.sh

sh $CURRENT_PATH/scripts/deploy_test.sh

echo "Stop old server process..."
killall python

if [ -f "$main_gunicorn_pid_file" ]; then
    main_gunicorn_pid=`cat $main_gunicorn_pid_file`
    echo "Kill main server: "$main_gunicorn_pid
    kill $main_gunicorn_pid
fi

if [ -f "$analysis_gunicorn_pid_file" ]; then
    analysis_gunicorn_pid=`cat $analysis_gunicorn_pid_file`
    echo "Kill analysis server: "$analysis_gunicorn_pid
    kill $analysis_gunicorn_pid
fi

if [ -f "$login_gunicorn_pid_file" ]; then
    login_gunicorn_pid=`cat $login_gunicorn_pid_file`
    echo "Kill login server: "$login_gunicorn_pid
    kill $login_gunicorn_pid
fi

if [ -f "$file_gunicorn_pid_file" ]; then
    file_gunicorn_pid=`cat $file_gunicorn_pid_file`
    echo "Kill file server: "$file_gunicorn_pid
    kill $file_gunicorn_pid
fi

killall gunicorn

echo "Stop old worker process"
if [ -f "$main_celery_worker_pid_file" ]; then
    main_celery_worker_pid=`cat $main_celery_worker_pid_file`
    echo "Kill main celery worker: "$main_celery_worker_pid
    kill $main_celery_worker_pid
fi

if [ -f "$main_celery_beat_pid_file" ]; then
    main_celery_beat_pid=`cat $main_celery_beat_pid_file`
    echo "Kill main celery beat: "$main_celery_beat_pid
    kill $main_celery_beat_pid
fi
if [ -f "$analysis_celery_worker_pid_file" ]; then
    analysis_celery_worker_pid=`cat $analysis_celery_worker_pid_file`
    echo "Kill analysis celery worker: "$analysis_celery_worker_pid
    kill $analysis_celery_worker_pid
fi
sleep 5

echo "Start main server"
cd $MAIN_PROJECT_PATH && gunicorn codedog.wsgi -c $main_gunicorn_conf_file

echo "Start analysis server"
cd $ANALYSIS_PROJECT_PATH && gunicorn codedog.wsgi -c $analysis_gunicorn_conf_file

echo "Start file server"
cd $FILE_PROJECT_PATH && gunicorn codedog_file_server.wsgi -c $file_gunicorn_conf_file

echo "Start login server"
cd $LOGIN_PROJECT_PATH && gunicorn apps.wsgi -c $login_gunicorn_conf_file

echo "Start scmproxy"
cd $SCMPROXY_PROJECT_PATH && nohup python proxyserver.py 2>&1 > nohup.out &

echo "Start worker"
echo "Start main celery worker"
echo "Main celery worker log: "$main_celery_worker_log
cd $MAIN_PROJECT_PATH && nohup celery -A codedog worker -l DEBUG --logfile $main_celery_worker_log  --pidfile $main_celery_worker_pid_file 2>&1 > nohup_worker.out &

echo "Start main celery beat"
echo "Main celery beat log: "$main_celery_beat_log
cd $MAIN_PROJECT_PATH && nohup celery -A codedog beat -S redbeat.RedBeatScheduler -l DEBUG --logfile $main_celery_beat_log --pidfile $main_celery_beat_pid_file 2>&1 > nohup_beat.out &

echo "Start analysis celery worker"
echo "Analysis celery worker log: "$analysis_celery_worker_log
cd $ANALYSIS_PROJECT_PATH && nohup celery -A codedog worker -l DEBUG --logfile $analysis_celery_worker_log  --pidfile $analysis_celery_worker_pid_file 2>&1 > nohup.out &

echo "Server Log:" $PROJECT_LOG_PATH

sh $CURRENT_PATH/scripts/service_test.sh