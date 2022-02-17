#!/bin/sh
# -*-*-*- 需要关注的配置内容 -*-*-*-
# 数据库配置，默认MySQL端口号为3306
export MYSQL_HOST=
export MYSQL_PORT=
export MYSQL_USER=
export MYSQL_PASSWORD=

# Redis配置，默认Redis端口号为6379
export REDIS_HOST=
export REDIS_PORT=
export REDIS_PASSWD=
# -*-*-*- 需要关注的配置内容 -*-*-*-

# -*-*-*- 以下配置均提供默认值，可以根据需要进行调整 -*-*-*-
# Main工程配置
## 框架配置
export MAIN_DEBUG_MODE=true
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
export FILE_STORAGE_DIR='data/file/'

## 服务交互配置
export PASSWORD_KEY='a6x4c7esudcv396w'
export API_TICKET_SALT='a6x4c7esudcv396w'
export API_TICKET_TOKEN='tca@public@2021'

## ScmProxy
export SCMPROXY_HOST="127.0.0.1"
export SCMPROXY_PORT=8009
