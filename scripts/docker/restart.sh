#!/bin/bash

CURRENT_SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")";pwd)
TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$( cd "$(dirname $CURRENT_SCRIPT_PATH)"; pwd )"}

# server config environment variables
export DAEMON=False
export SERVER_ACCESS_LOG="-"
export SERVER_ERROR_LOG="-"

source $TCA_SCRIPT_ROOT/config.sh
source $TCA_SCRIPT_ROOT/server/init_config.sh
source $TCA_SCRIPT_ROOT/web/init.sh

function restart_all() {
    init_web_config
    clean_server_pid
    supervisorctl -c /CodeAnalysis/scripts/docker/supervisord.conf restart all
}

restart_all
