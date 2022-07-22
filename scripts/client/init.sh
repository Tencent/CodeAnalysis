#!/usr/bin/env bash

CURRENT_SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")";pwd)
TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$(cd $(dirname $CURRENT_SCRIPT_PATH); pwd)"}
export TCA_PROJECT_PATH=${TCA_PROJECT_PATH:-"$( cd $(dirname $TCA_SCRIPT_ROOT); pwd )"}
export TCA_CLIENT_PATH=$TCA_PROJECT_PATH/client

source $TCA_SCRIPT_ROOT/utils.sh

function install_client_requirments() {
    LOG_INFO "Install client dependency packages..."
    LOG_WARN "如果访问官方pypi源（files.pythonhosted.org）超时或访问失败，可以配置为腾讯云pypi源进行下载，配置方式可以执行以下命令："
    LOG_WARN "mkdir ~/.pip/ && printf \"[global]\nindex-url = https://mirrors.cloud.tencent.com/pypi/simple\" >> ~/.pip/pip.conf"
    pip install -r $TCA_CLIENT_PATH/requirements/app_reqs.pip
    cd $TCA_CLIENT_PATH/requirements
    bash install.sh
}

function init_client_tools() {
    LOG_WARN "如果访问github速度较慢，推荐使用腾讯工蜂拉取，需要修改 $TCA_PROJECT_PATH/client/config.ini 文件"
    LOG_WARN "1. 前往腾讯工蜂网站 https://git.codeo.tencent.com 注册账号，作为拉取工具使用（已经注册过的可以直接使用）"
    LOG_WARN "2. 修改 TOOL_CONFIG_URL=https://git.code.tencent.com/TCA/tca-tools/puppy-tools-config.git"
    LOG_WARN "3. 将腾讯工蜂的账号密码填写到TOOL_LOAD_ACCOUNT中（由于腾讯工蜂的开源仓库也要求使用账号才能拉取，所以此处必须填写账号密码）"
}

function init_client_config() {
    install_client_requirments
    init_client_tools
}