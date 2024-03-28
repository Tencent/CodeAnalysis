#!/bin/bash
# -*-*-*- 需要关注的配置内容 -*-*-*-
# 数据库配置，默认MySQL端口号为3306
export USE_EXTERNAL_MYSQL=${USE_EXTERNAL_MYSQL:-false}
export MYSQL_HOST=${MYSQL_HOST:-127.0.0.1}
export MYSQL_PORT=${MYSQL_PORT:-3306}
export MYSQL_USER=${MYSQL_USER:-tca}
export MYSQL_PASSWORD=${MYSQL_PASSWORD:-"TCA!@#2021"}

# Redis配置，默认Redis端口号为6379
export USE_EXTERNAL_REDIS=${USE_EXTERNAL_REDIS:-false}
export REDIS_HOST=${REDIS_HOST:-127.0.0.1}
export REDIS_PORT=${REDIS_PORT:-6379}
export REDIS_PASSWD=${REDIS_PASSWD:-"tca2022"}
# -*-*-*- 需要关注的配置内容 -*-*-*-

# -*-*-*- 以下配置均提供默认值，可以根据需要进行调整 -*-*-*-
# Nginx配置
export NGINX_PATH=${NGINX_PATH:-"/etc/nginx"}
export NGINX_CONF_PATH=${NGINX_CONF_PATH:-"/etc/nginx/conf.d"}
export NGINX_LOG_PATH=${NGINX_LOG_PATH:-"/var/log/nginx"}
export TCA_WEB_DEPLOY_PATH=${TCA_WEB_DEPLOY_PATH:-"/usr/share/nginx/www"}

# Web配置
# TCA Web配置服务地址
export TCA_WEB_HOST=${TCA_WEB_HOST:-"0.0.0.0"}
# TCA Web配置服务端口号
export TCA_WEB_PORT=${TCA_WEB_PORT:-"80"}
# TCA Server后端地址
export TCA_SERVER_ADDR=${TCA_SERVER_ADDR:-"127.0.0.1:8000"}

# Client配置
export CODEDOG_SERVER=${CODEDOG_SERVER:-"http://$TCA_WEB_HOST/server/main/"}
export FILE_SERVER_URL=${FILE_SERVER_URL:-"http://$TCA_WEB_HOST/server/files/"}
export TCA_APP_DATA_DIR=${TCA_APP_DATA_DIR}

# Main工程配置
## 框架配置
export MAIN_DEBUG_MODE=true
export HTTPS_CLONE_FLAG=true
export MAIN_SECRET_KEY='lh+6y8pyf16bbor*)p=kp=p(cg615+y+5nnin$l(n%os$8z^v%'

## 服务DB配置
export MAIN_DB_NAME=codedog_main
export MAIN_DB_USER=$MYSQL_USER
export MAIN_DB_PASSWORD=$MYSQL_PASSWORD
export MAIN_DB_HOST=$MYSQL_HOST
export MAIN_DB_PORT=$MYSQL_PORT

## 服务Redis配置
export MAIN_REDIS_HOST=$REDIS_HOST
export MAIN_REDIS_PORT=$REDIS_PORT
export MAIN_REDIS_PASSWD=$REDIS_PASSWD
export MAIN_REDIS_DBID=1

## 日志上报至sentry配置
export MAIN_SENTRY_DSN=

## 服务交互配置
export PASSWORD_KEY='a6x4c7esudcv396w'
export API_TICKET_SALT='a6x4c7esudcv396w'
export API_TICKET_TOKEN='tca@public@2021'
export FILE_SERVER_TOKEN='0712b895f30c5e958ec71a7c22e1b1a2ad1d5c6b'
export CODEDOG_TOKEN='0712b895f30c5e958ec71a7c22e1b1a2ad1d5c6b'


# Analysis工程配置
export ANALYSIS_DEBUG_MODE=true
export ANALYSIS_SECRET_KEY='25n=e*_e=4q!ert$4u#9v&^2n+)_#mi7&7ll@x29@j=w=k^q@^'

## 服务DB配置
export ANALYSIS_DB_NAME=codedog_analysis
export ANALYSIS_DB_USER=$MYSQL_USER
export ANALYSIS_DB_PASSWORD=$MYSQL_PASSWORD
export ANALYSIS_DB_HOST=$MYSQL_HOST
export ANALYSIS_DB_PORT=$MYSQL_PORT

## 服务Redis配置
export ANALYSIS_REDIS_HOST=$REDIS_HOST
export ANALYSIS_REDIS_PORT=$REDIS_PORT
export ANALYSIS_REDIS_PASSWD=$REDIS_PASSWD
export ANALYSIS_REDIS_DBID=0

## 日志上报至sentry配置
export ANALYSIS_SENTRY_DSN=

## 服务交互配置
export API_TICKET_SALT='a6x4c7esudcv396w'
export API_TICKET_TOKEN='tca@public@2021'
export FILE_SERVER_TOKEN='0712b895f30c5e958ec71a7c22e1b1a2ad1d5c6b'


# Login工程配置
export LOGIN_DEBUG_MODE=true
export LOGIN_SECRET_KEY='iht%_(ixb)w&sedrh2t-ydxnre)uy+=_hv4v^8m@19p27r6sz_'

export TCA_DEFAULT_ADMIN="CodeDog"
export TCA_DEFAULT_PASSWORD="admin"

## 服务DB配置
export LOGIN_DB_NAME=codedog_login
export LOGIN_DB_USER=$MYSQL_USER
export LOGIN_DB_PASSWORD=$MYSQL_PASSWORD
export LOGIN_DB_HOST=$MYSQL_HOST
export LOGIN_DB_PORT=$MYSQL_PORT


## 服务交互配置
export PASSWORD_KEY='a6x4c7esudcv396w'
export API_TICKET_SALT='a6x4c7esudcv396w'
export API_TICKET_TOKEN='tca@public@2021'


# File工程配置
export FILE_SECRET_KEY='8b_!6t@kb=63c)4#e^0wub=x8%xd9624jm@#eiv3y#%b_%4!n='

## 服务DB配置
export FILE_DB_NAME=codedog_file
export FILE_DB_USER=$MYSQL_USER
export FILE_DB_PASSWORD=$MYSQL_PASSWORD
export FILE_DB_HOST=$MYSQL_HOST
export FILE_DB_PORT=$MYSQL_PORT

## 日志上报至sentry配置
export FILE_SENTRY_DSN=

## 上报文件存储位置
export FILE_STORAGE_DIR=${FILE_STORAGE_DIR:-'data/file/'}

## MinIO服务配置
export FILE_MINIO_ENTRYPOINT=
export FILE_MINIO_ACCESS_KEY=
export FILE_MINIO_SECRET_KEY=

## 服务交互配置
export PASSWORD_KEY='a6x4c7esudcv396w'
export API_TICKET_SALT='a6x4c7esudcv396w'
export API_TICKET_TOKEN='tca@public@2021'

## ScmProxy
export SCMPROXY_HOST="127.0.0.1"
export SCMPROXY_PORT=8009

## LDAP相关配置
## Notice：如果要开启LDAP 认证，请根据实际情况配置以下参数
## LDAP_ENABLE  默认关闭，开启请设置为true
## LDAP_BIND_DN  LDAP管理员账号，如果允许匿名访问则不需要设置
## LDAP_BIND_PASSWORD  LDAP管理员密码 如果允许匿名访问则不需要设置
## LDAP_SERVER  ldap服务器地址
## LDAP_PORT  ldap默认端口号 389 如果需要更改请重新设置
## LDAP_BASE_DN  ldap 基础 DN
## LDAP_USER_SEARCH_FILTER  用户搜索过滤器

export LDAP_ENABLE=${LDAP_ENABLE:-false}
export LDAP_BIND_DN=""
export LDAP_BIND_PASSWORD=""
export LDAP_SERVER=""
export LDAP_PORT=389
export LDAP_BASE_DN=""
export LDAP_USER_SEARCH_FILTER=""