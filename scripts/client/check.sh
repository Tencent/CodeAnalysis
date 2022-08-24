#!/bin/bash

CURRENT_SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")";pwd)
TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$(cd $(dirname $CURRENT_SCRIPT_PATH); pwd)"}
TCA_PROJECT_PATH=${TCA_PROJECT_PATH:-"$(cd "$(dirname $TCA_SCRIPT_ROOT)"; pwd)"}


source $TCA_SCRIPT_ROOT/utils.sh

function check_result() {
    name=$1
    ret=$2
    if [ "$ret" = "true" ]; then
        LOG_INFO "$name start: OK."
        return 0
    else
        LOG_ERROR "$name start: Failed."
        return 1
    fi
}

function check_client_running() {
    client_result=$( check_target_process_exist "codepuppy")
    if [ "$client_result" = "true" ]; then
        return 0
    else
        return 1
    fi
}

function check_tca_client_status() {
    client_result=""
    LOG_INFO "Check client start status..."
    check_client_running
    check_result "tca_client" "$client_result"
}
