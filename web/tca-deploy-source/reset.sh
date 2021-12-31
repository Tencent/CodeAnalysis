#!/usr/bin/env sh
# Customizable environment variables:
# +---------+-------------------+----------------------------------------------+
# | Name | Default Value | Intro |
# +---------+-------------------+----------------------------------------------+
# | SERVER_ENV | | 访问的后端地址，必填项 |
# | INGRESS_PORT | 80 | ingress 配置的端口，默认 80 |
# | INGRESS_SERVER_NAME | tca.tencent.com | ingress 配置的服务名称，默认 tca.tencent.com |
# +---------+-------------------+----------------------------------------------+

###########################
### 重新部署脚本
### 执行方式：
### 方式一：直接执行 sh reset.sh -d 或 sh reset.sh default 即可
### 方式二：查阅上述环境变量，先export对应环境变量，再 sh reset.sh
###########################

# 获取当前脚本执行目录，绝对路径
CUR_RUN_PATH=$(cd $(dirname $0) && pwd)
cd $CUR_RUN_PATH

# 默认配置
if [ "$1" = "default" -o "$1" = "-d" ]; then
  source $CUR_RUN_PATH/config.sh
fi

# 微前端静态资源存放位置
WWW_DIR_PATH="/usr/share/nginx/www"

if [ ! -n "${SERVER_ENV}" ]; then
  echo "请指定访问服务地址"
  exit 1
fi

function rm_all() {
  mkdir -p ${WWW_DIR_PATH}
  echo "移除全部静态资源文件 ..."
  rm -rf ${WWW_DIR_PATH}/
  CONFD_PATH="/etc/nginx/conf.d"
  echo "移除nginx conf.d web相关conf"
  rm -f ${CONFD_PATH}/framework.conf
  rm -f ${CONFD_PATH}/tca-layout.conf
  rm -f ${CONFD_PATH}/login.conf
  rm -f ${CONFD_PATH}/tca-analysis.conf
  rm -f ${CONFD_PATH}/tca-document.conf
  echo "移除nginx conf.d ingress相关conf"
  rm -f ${CONFD_PATH}/tca_ingress.conf
}

function reset_run() {
  echo "关闭 nginx ..."
  # 存在nginx 进程时，先stop nginx，再执行初始化
  nginx_is_start=$(ps -C nginx --no-header | wc -l)
  if [ ${nginx_is_start} -ne 0 ]; then
    nginx -s stop
  fi
  echo "重新执行init脚本"
  cd ${CUR_RUN_PATH}
  sh init.sh
}

rm_all
reset_run
