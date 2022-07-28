#!/usr/bin/env bash

CURRENT_SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")";pwd)
TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$(cd $(dirname $CURRENT_SCRIPT_PATH); pwd)"}

source $TCA_SCRIPT_ROOT/utils.sh

function stop_client() {
    cd $TCA_CLIENT_PATH
    LOG_INFO "stop tca client"
    force_kill "codepuppy.py"
}