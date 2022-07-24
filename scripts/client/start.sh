#!/usr/bin/env bash

CURRENT_SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")";pwd)
TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$(cd $(dirname $CURRENT_SCRIPT_PATH); pwd)"}
export TCA_PROJECT_PATH=${TCA_PROJECT_PATH:-"$( cd $(dirname $TCA_SCRIPT_ROOT); pwd )"}
export TCA_CLIENT_PATH=$TCA_PROJECT_PATH/client

source $TCA_SCRIPT_ROOT/utils.sh
source $TCA_SCRIPT_ROOT/config.sh
source $TCA_SCRIPT_ROOT/client/stop.sh

function start_client() {
    cd $TCA_CLIENT_PATH
    stop_client
    LOG_INFO "start tca client"
    nohup python3 codepuppy.py start -t ${CODEDOG_TOKEN} >start.out 2>&1 &
}