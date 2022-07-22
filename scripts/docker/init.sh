#!/bin/bash

CURRENT_SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")";pwd)
TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$( cd "$(dirname $CURRENT_SCRIPT_PATH)"; pwd )"}
TCA_INIT_FLAG=${TCA_INIT_FLAG:-"true"}

source $TCA_SCRIPT_ROOT/utils.sh
source $TCA_SCRIPT_ROOT/config.sh
source $TCA_SCRIPT_ROOT/server/init_config.sh
source $TCA_SCRIPT_ROOT/server/int_db.sh

mkdir -p /var/log/tca/supervisord/
mkdir -p /var/log/tca/mariadb
mkdir -p /var/opt/tca/mariadb
mkdir -p /var/opt/tca/redis
mkdir -p /var/log/tca/redis
mkdir -p /var/log/tca/servers/
mkdir -p /etc/tca/
chown -R mysql:mysql /var/log/tca/mariadb /var/opt/tca/mariadb

# 配置DB初始化密码
sed "s/TCA_MYSQL_PASSWORD/${MYSQL_PASSWORD}/g" /CodeAnalysis/server/sql/_temp.sql > /CodeAnalysis/server/sql/reset_root_password.sql
# 指定mariadb安装位置
mysql_install_db --user=mysql --datadir=/var/opt/tca/mariadb
# 调整redis rdb位置
sed -i "s/^dir\s.*/dir \/var\/opt\/tca\/redis/g" /etc/redis.conf

init_server_config
