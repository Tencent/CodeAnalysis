#!/bin/sh

CURRENT_PATH=$(dirname $(cd "$(dirname "$0")";pwd))
PROJECT_TMP_PATH=$CURRENT_PATH/tmp
PROJECT_LOG_PATH=$CURRENT_PATH/logs
MAIN_PROJECT_PATH=$CURRENT_PATH/projects/main
ANALYSIS_PROJECT_PATH=$CURRENT_PATH/projects/analysis
LOGIN_PROJECT_PATH=$CURRENT_PATH/projects/login
FILE_PROJECT_PATH=$CURRENT_PATH/projects/file
SCMPROXY_PROJECT_PATH=$CURRENT_PATH/projects/scmproxy

main_celery_worker_pid_file=$PROJECT_TMP_PATH/main_celery_worker.pid
main_celery_beat_pid_file=$PROJECT_TMP_PATH/main_celery_beat.pid
analysis_celery_worker_pid_file=$PROJECT_TMP_PATH/analysis_celery_worker.pid


echo "Stop old server process..."
killall python
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