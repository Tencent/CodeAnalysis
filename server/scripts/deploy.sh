#!/bin/bash

CURRENT_PATH=$(dirname $(cd "$(dirname "$0")";pwd))

if [ $1 == "initconf" ]; then
    sh $CURRENT_PATH/scripts/init_config.sh
elif [ $1 == "init" ]; then
    sh $CURRENT_PATH/scripts/init_data.sh
elif [ $1 == "start" ]; then
    sh $CURRENT_PATH/scripts/start_service.sh
elif [ $1 == "stop" ]; then
    sh $CURRENT_PATH/scripts/stop_service.sh
fi