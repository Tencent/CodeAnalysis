#!/bin/bash

CURRENT_SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")";pwd)
TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$( cd "$(dirname $CURRENT_SCRIPT_PATH)"; pwd )"}
TCA_INIT_FLAG=${TCA_INIT_FLAG:-"true"}

source $TCA_SCRIPT_ROOT/utils.sh
source $TCA_SCRIPT_ROOT/config.sh
source $TCA_SCRIPT_ROOT/server/init_config.sh
source $TCA_SCRIPT_ROOT/client/init.sh

# 配置DB初始化密码
sed "s/TCA_MYSQL_PASSWORD/${MYSQL_PASSWORD}/g" /CodeAnalysis/server/sql/_temp.sql > /CodeAnalysis/server/sql/reset_root_password.sql
# 调整redis rdb位置
sed -i "s/^dir\s.*/dir \/var\/opt\/tca\/redis/g" /etc/redis/redis.conf

init_server_config
init_client_config