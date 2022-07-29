#!/bin/bash

CURRENT_SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")";pwd)
TCA_PROJECT_PATH=${TCA_PROJECT_PATH:-"$CURRENT_SCRIPT_PATH"}
TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$CURRENT_SCRIPT_PATH/scripts"}

source $TCA_SCRIPT_ROOT/deploy/tca_docker_compose.sh

function start_deploy_with_docker_compose() {
    bash $TCA_PROJECT_PATH/server/scripts/deploy_test_docker.sh
    tca_docker_compose_main "deploy"
}

start_deploy_with_docker_compose
