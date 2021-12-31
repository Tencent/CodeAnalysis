#!/bin/sh

# 获取本机IP
LOCAL_IP=${LOCAL_IP:-"$(ip addr | awk '/^[0-9]+: / {}; /inet.*global/ {print gensub(/(.*)\/(.*)/, "\\1", "g", $2)}')"}
# 存在多IP时取第一个
array=(${LOCAL_IP//\ / })
LOCAL_IP=${array[0]}

if [ ! -n "${LOCAL_IP}" ]; then
  echo "本机IP获取失败，请先设置本机IP环境变量再执行config.sh脚本，如export LOCAL_IP=xxx"
  exit 1
fi

export SERVER_ENV=127.0.0.1:8000

export INGRESS_SERVER_NAME=${LOCAL_IP}
export INGRESS_PORT=80
