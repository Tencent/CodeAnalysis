#!/usr/bin/env bash

CURRENT_SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")";pwd)
TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$(cd $(dirname $CURRENT_SCRIPT_PATH); pwd)"}
export TCA_PROJECT_PATH=${TCA_PROJECT_PATH:-"$( cd $(dirname $TCA_SCRIPT_ROOT); pwd )"}
export TCA_CLIENT_PATH=$TCA_PROJECT_PATH/client

source $TCA_SCRIPT_ROOT/utils.sh

function install_client_requirments() {
    LOG_INFO "[TCAClient] Install client dependency packages..."
    use_right_pip "install -q -r $TCA_CLIENT_PATH/requirements/app_reqs.pip"
    cd $TCA_CLIENT_PATH/requirements
    bash install.sh
}

function init_client_tools() {
    LOG_INFO "[TCAClient] Init client tools..."
    LOG_INFO "可手动执行：cd $TCA_CLIENT_PATH; python3 codepuppy.py updatetool -a -o linux"
    LOG_INFO "注意事项："
    LOG_WARN "如果访问github速度较慢，推荐使用腾讯工蜂拉取，需要修改 $TCA_PROJECT_PATH/client/config.ini 文件"
    LOG_WARN "    1. 前往腾讯工蜂网站 https://git.codeo.tencent.com 注册账号，作为拉取工具使用（已经注册过的可以直接使用）"
    LOG_WARN "    2. 修改 TOOL_CONFIG_URL=https://git.code.tencent.com/TCA/tca-tools/puppy-tools-config.git"
    LOG_WARN "    3. 将腾讯工蜂的账号密码填写到TOOL_LOAD_ACCOUNT中（由于腾讯工蜂的开源仓库也要求使用账号才能拉取，所以此处必须填写账号密码）"
    LOG_WARN "如果是内网环境，建议提前将工具下载到本地使用"
    LOG_WARN "操作指引可以查阅 https://github.com/Tencent/CodeAnalysis/tree/main/client#1-%E9%85%8D%E7%BD%AE%E4%BD%BF%E7%94%A8%E6%9C%AC%E5%9C%B0%E5%B7%A5%E5%85%B7 "
    LOG_WARN ""
}

function init_client_config() {
    install_client_requirments
    init_client_tools
}