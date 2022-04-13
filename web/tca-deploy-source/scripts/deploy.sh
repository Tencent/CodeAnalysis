#!/usr/bin/env bash

echo "###################################### 脚本说明 ######################################"
echo "# 前端部署脚本"
echo "# \$1 action，为必传项，\$2 其他参数，非必传项"
echo "# 部署web服务：bash $0 init -d"
echo "###################################### 脚本说明 ######################################"

# 获取工作目录路径，绝对路径
WORK_PATH=$(cd $(dirname $0) && pwd)

source $WORK_PATH/_log.sh

# 第一个参数为执行行动
ACTION=${1:-'$1'}
# 第二个参数其他参数配置
PARAMS=${2:-'$1'}

if [ "$ACTION" == "init" ]; then
  bash $WORK_PATH/init.sh $PARAMS
else
  LOG_WARN "$ACTION 参数无效"
  exit 1
fi
