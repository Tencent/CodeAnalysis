#!/bin/bash


CURRENT_SCRIPT_PATH=$( cd "$(dirname ${BASH_SOURCE[0]})"; pwd )
export TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$( cd $(dirname $CURRENT_SCRIPT_PATH); pwd )"}
export TCA_PROJECT_PATH=${TCA_PROJECT_PATH:-"$( cd $(dirname $TCA_SCRIPT_ROOT); pwd )"}

source $TCA_SCRIPT_ROOT/utils.sh

TCA_IMAGE_NAME=${TCA_IMAGE_NAME:-"tencenttca/tca-server"}
TCA_IMAGE_TAG=${TCA_IMAGE_TAG:-"latest"}
TCA_IMAGE_BUILD=${TCA_IMAGE_BUILD:-"false"}
TCA_INIT_DATA=${TCA_INIT_DATA:-"true"}

TCA_DOCKER_LOG_PATH=${TCA_LOG_PATH:-"$TCA_PROJECT_PATH/.docker_temp/logs/"}
TCA_DOCKER_DATA_PATH=${TCA_DATA_PATH:-"$TCA_PROJECT_PATH/.docker_temp/data/"}
TCA_DOCKER_CONFIG_PATH=${TCA_CONFIG_PATH:-"$TCA_PROJECT_PATH/.docker_temp/configs/"}

function build_image() {
    if [ "$(docker image inspect $TCA_IMAGE_NAME:$TCA_IMAGE_TAG 2> /dev/null)" == "[]" ]; then
        cd $TCA_PROJECT_PATH
        docker build -t $TCA_IMAGE_NAME:$TCA_IMAGE_TAG .
    fi
}

function get_image() {
    if [ "$TCA_IMAGE_BUILD" == "true" ]; then
        LOG_INFO "Build TCA Image: $TCA_IMAGE_NAME:$TCA_IMAGE_TAG"
        cd $TCA_PROJECT_PATH
        docker build -t $TCA_IMAGE_NAME:$TCA_IMAGE_TAG .
        return $?
    fi
    LOG_INFO "Pull TCA Image: $TCA_IMAGE_NAME:$TCA_IMAGE_TAG"
    docker pull $TCA_IMAGE_NAME:$TCA_IMAGE_TAG 2> /dev/null
    ret=$?
    if [ "$ret" != "0" ]; then
        build_image
    fi
}

function start_container() {
    LOG_INFO "Start tca container command:"
    set -x
    docker run -it --env TCA_INIT_DATA=$TCA_INIT_DATA \
        --name tca_server --publish 80:80 --publish 8000:8000 --publish 9001:9001 \
        -v $TCA_DOCKER_LOG_PATH:/var/log/tca/ \
        -v $TCA_DOCKER_DATA_PATH:/var/opt/tca/ \
        -v $TCA_DOCKER_CONFIG_PATH:/etc/tca/ \
        $TCA_IMAGE_NAME:$TCA_IMAGE_TAG
    set +x
    
    LOG_INFO "TCA Docker Log Path:     $TCA_DOCKER_LOG_PATH"
    LOG_INFO "TCA Docker Data Path:    $TCA_DOCKER_DATA_PATH"
    LOG_INFO "TCA Docker Config Path:  $TCA_DOCKER_CONFIG_PATH"
}

function tca_docker_main() {
    get_image
    start_container
}

