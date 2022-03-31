#!/usr/bin/env bash

# 获取本机IP
LOCAL_IP=${LOCAL_IP:-"$(ip addr | awk '/^[0-9]+: / {}; /inet.*global/ {print gensub(/(.*)\/(.*)/, "\\1", "g", $2)}')"}
# 存在多IP时取第一个
array=(${LOCAL_IP//\ / })
LOCAL_IP=${array[0]}

# 校验本机IP
if [ ! -n "${LOCAL_IP}" ]; then
  echo "本机IP获取失败，请先设置本机IP环境变量再执行config.sh脚本，如export LOCAL_IP=xxx"
  exit 1
fi

# 访问后端的地址
export SERVER_ENV=127.0.0.1:8000
# 前端 nginx 配置服务名称
export INGRESS_SERVER_NAME=${LOCAL_IP}
# 前端 nginx 配置服务端口号
export INGRESS_PORT=80
# nginx 配置地址
export NGINX_CONF_PATH="/etc/nginx/conf.d"
# 前端资源部署地址
export WEB_DEPLOY_PATH="/usr/share/nginx/www"
# nginx 日志文件地址
export NGINX_LOG_PATH="/var/log/nginx"
