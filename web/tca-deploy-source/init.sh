#!/usr/bin/env sh
# Customizable environment variables:
# +---------+-------------------+----------------------------------------------+
# | Name | Default Value | Intro |
# +---------+-------------------+----------------------------------------------+
# | SERVER_ENV | | 访问的后端地址，必填项 |
# | INGRESS_PORT | 80 | ingress 配置的端口，默认 80 |
# | INGRESS_SERVER_NAME | tca.tencent.com | ingress 配置的服务名称，默认 tca.tencent.com |
# | NGINX_CONF_PATH | /etc/nginx/conf.d | nginx配置地址，默认 /etc/nginx/conf.d |
# | WEB_DEPLOY_PATH | /usr/share/nginx/www | 前端资源部署地址，默认 /usr/share/nginx/www |
# | IS_DOCKER | FALSE | 是否DOCKER启动 |
# +---------+-------------------+----------------------------------------------+

###########################
### 初始化脚本，第一次部署执行
### 执行方式：
### 方式一：直接执行 sh init.sh -d 或 sh init.sh default 即可
### 方式二：查阅上述环境变量，先export对应环境变量，再 sh init.sh
###########################

# 获取当前脚本执行目录，绝对路径
CUR_RUN_PATH=$(cd $(dirname $0) && pwd)
cd $CUR_RUN_PATH

# 默认配置
if [ "$1" = "default" -o "$1" = "-d" ]; then
  source $CUR_RUN_PATH/config.sh
fi

# 微前端静态资源存放位置
WEB_DEPLOY_PATH=${WEB_DEPLOY_PATH:-"/usr/share/nginx/www"}

if [ ! -n "${SERVER_ENV}" ]; then
  echo "请指定访问服务地址"
  exit 1
fi

# nginx 配置地址，默认/etc/nginx/conf.d
NGINX_CONF_PATH=${NGINX_CONF_PATH:-"/etc/nginx/conf.d"}
# nginx 日志文件地址，默认/var/log/nginx
NGINX_LOG_PATH=${NGINX_LOG_PATH:-"/var/log/nginx"}

# 配置host，追加到hosts文件内
function conf_hosts() {
  echo "配置host ..."
  cat >>/etc/hosts <<EOF
127.0.0.1 framework
127.0.0.1 login
127.0.0.1 tca-layout
127.0.0.1 tca-analysis
127.0.0.1 tca-manage
127.0.0.1 tca-document
EOF
}

# 初始化解压编译后文件
function init_unzip_build() {
  echo "初始化解压编译后文件 ..."
  mkdir -p ${WEB_DEPLOY_PATH}
  cd ${CUR_RUN_PATH}/build_zip/
  unzip -o framework.zip -d ${WEB_DEPLOY_PATH}/framework
  unzip -o tca-layout.zip -d ${WEB_DEPLOY_PATH}/tca-layout
  unzip -o login.zip -d ${WEB_DEPLOY_PATH}/login
  unzip -o tca-analysis.zip -d ${WEB_DEPLOY_PATH}/tca-analysis
  unzip -o tca-manage.zip -d ${WEB_DEPLOY_PATH}/tca-manage
  unzip -o tca-document.zip -d ${WEB_DEPLOY_PATH}/tca-document
  cd ${CUR_RUN_PATH}
}

# 初始化配置 framework
function init_framework_web() {
  echo "初始化配置 framework ..."
  RUNTIME="TRUE"
  MICRO_FRONTEND_API=/static/configs.json
  MICRO_FRONTEND_SETTING_API=/static/settings.json
  TITLE=腾讯云代码分析
  DESCRIPTION=腾讯云代码分析，用心关注每行代码迭代、助力传承卓越代码文化！精准跟踪管理代码分析发现的代码质量缺陷、代码规范、代码安全漏洞、无效代码，以及度量代码复杂度、重复代码、代码统计。
  KEYWORDS=代码检查、圈复杂度、重复代码、代码统计
  FAVICON=/static/images/favicon.ico

  if [ $RUNTIME = "TRUE" ]; then
    replace_content="
    s|__TITLE__|${TITLE}|g; \
    s|__KEYWORDS__|${KEYWORDS}|g; \
    s|__DESCRIPTION__|${DESCRIPTION}|g; \
    s|__FAVICON__|${FAVICON}|g; \
    "
    echo "[INFO]:index.html RUNTIME is enabled"
    echo "[INFO]: change 404.html, unsupported-browser.html"
    sed -i "${replace_content}" ${WEB_DEPLOY_PATH}/framework/404.html
    sed -i "${replace_content}" ${WEB_DEPLOY_PATH}/framework/unsupported-browser.html

    echo "[INFO]: change index.html"
    sed \
      "
      ${replace_content} \
      s|__MICRO_FRONTEND_API__|${MICRO_FRONTEND_API}|g; \
      s|__MICRO_FRONTEND_SETTING_API__|${MICRO_FRONTEND_SETTING_API}|g; \
      " \
      ${WEB_DEPLOY_PATH}/framework/index.runtime.html >${WEB_DEPLOY_PATH}/framework/index.html

    if [ "$DEBUG" = "TRUE" ]; then
      cat ${WEB_DEPLOY_PATH}/framework/index.html
      echo ""
      echo "[INFO]:index.html content is above"
    fi
  fi

  # 将conf目录中的配置文件拷贝到 framework static目录下
  cp ${CUR_RUN_PATH}/conf/settings.json ${WEB_DEPLOY_PATH}/framework/static/settings.json
  cp ${CUR_RUN_PATH}/conf/configs.json ${WEB_DEPLOY_PATH}/framework/static/configs.json
}

# 初始化各个微前端的nginx配置
function init_web_nginx() {
  echo "初始化各个微前端的nginx配置 ..."
  sed "s|WEB_DEPLOY_PATH|${WEB_DEPLOY_PATH}|g; s|NGINX_LOG_PATH|${NGINX_LOG_PATH}|g; s|APP_NAME|framework|g; s|SERVER_ENV|${SERVER_ENV}|g;" ${CUR_RUN_PATH}/nginx/framework_template.conf >${NGINX_CONF_PATH}/framework.conf
  sed "s|WEB_DEPLOY_PATH|${WEB_DEPLOY_PATH}|g; s|NGINX_LOG_PATH|${NGINX_LOG_PATH}|g; s|APP_NAME|tca-layout|g;" ${CUR_RUN_PATH}/nginx/template.conf >${NGINX_CONF_PATH}/tca-layout.conf
  sed "s|WEB_DEPLOY_PATH|${WEB_DEPLOY_PATH}|g; s|NGINX_LOG_PATH|${NGINX_LOG_PATH}|g; s|APP_NAME|login|g;" ${CUR_RUN_PATH}/nginx/template.conf >${NGINX_CONF_PATH}/login.conf
  sed "s|WEB_DEPLOY_PATH|${WEB_DEPLOY_PATH}|g; s|NGINX_LOG_PATH|${NGINX_LOG_PATH}|g; s|APP_NAME|tca-analysis|g;" ${CUR_RUN_PATH}/nginx/template.conf >${NGINX_CONF_PATH}/tca-analysis.conf
  sed "s|WEB_DEPLOY_PATH|${WEB_DEPLOY_PATH}|g; s|NGINX_LOG_PATH|${NGINX_LOG_PATH}|g; s|APP_NAME|tca-document|g;" ${CUR_RUN_PATH}/nginx/document.conf >${NGINX_CONF_PATH}/tca-document.conf
}

# 初始化配置ingress的nginx配置
function init_ingress_nginx() {
  echo "初始化配置ingress的nginx配置 ..."
  INGRESS_PORT="${INGRESS_PORT:-80}"
  INGRESS_SERVER_NAME="${INGRESS_SERVER_NAME:-tca.tencent.com}"
  SET_DEFAULT_SERVER=""
  if [ "$IS_DOCKER" = "TRUE" ]; then
    SET_DEFAULT_SERVER="default_server"
  fi
  sed \
    "
    s|PORT|${INGRESS_PORT}|g; \
    s|SERVER_NAME|${INGRESS_SERVER_NAME}|g; \
    s|SET_DEFAULT_SERVER|${SET_DEFAULT_SERVER}|g; \
    s|NGINX_LOG_PATH|${NGINX_LOG_PATH}|g; \
    " \
    ${CUR_RUN_PATH}/nginx/ingress.conf >${NGINX_CONF_PATH}/tca_ingress.conf
}

# 启动nginx
function start() {
  echo "启动 nginx ..."
  # wc -l 行数计算。当nginx无进程时，启动nginx，否则reload nginx
  nginx_is_start=$(ps -C nginx --no-header | wc -l)
  if [ ${nginx_is_start} -eq 0 ]; then
    nginx -t
    if [ "$IS_DOCKER" = "TRUE" ]; then
      nginx -g "daemon off;"
    else
      nginx
    fi
  else
    nginx -s reload
  fi
}

conf_hosts
init_unzip_build
init_framework_web
init_web_nginx
init_ingress_nginx
start
