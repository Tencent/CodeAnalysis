#!/bin/bash

# 当前脚本执行目录
CURRENT_SCRIPT_PATH=$(
  cd "$(dirname "${BASH_SOURCE[0]}")" || exit
  pwd
)

TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$(dirname "${CURRENT_SCRIPT_PATH}")"}

export TCA_PROJECT_PATH=${TCA_PROJECT_PATH:-"$(dirname "${TCA_SCRIPT_ROOT}")"}
export TCA_WEB_PATH=$TCA_PROJECT_PATH/web
export TCA_WEB_DEPLOY_SOURCE_PATH=$TCA_WEB_PATH/tca-deploy-source

# shellcheck disable=SC1091
source "$TCA_SCRIPT_ROOT"/utils.sh
# shellcheck disable=SC1091
source "$TCA_SCRIPT_ROOT"/config.sh

# 微前端基座
MICRO_FRONTEND_FRAMEWORK="framework"
# 微前端帮助文档
MICRO_FRONTEND_DOCUMENT="tca-document"
# 子微前端
MICRO_FRONTEND_APPS="login tca-layout tca-analysis tca-manage"

# 清理资源文件
function clear_assets() {
  LOG_WARN "将路径下的资源文件和前端nginx配置备份到 ${TCA_WEB_DEPLOY_PATH}_bak 下..."
  if [ -d "$TCA_WEB_DEPLOY_PATH" ]; then
    cp -r "$TCA_WEB_DEPLOY_PATH"/ "${TCA_WEB_DEPLOY_PATH}"_bak/
  fi

  if [ -d "$NGINX_CONF_PATH/tca_ingress.conf" ]; then
    cp -r "$NGINX_CONF_PATH"/tca_ingress.conf "${TCA_WEB_DEPLOY_PATH}"_bak/
  fi

  LOG_INFO "开始清理路径下的资源文件 $TCA_WEB_DEPLOY_PATH ..."
  rm -rf "${TCA_WEB_DEPLOY_PATH:?}"/
  LOG_INFO "开始清理前端nginx配置 ..."
  rm -f "$NGINX_CONF_PATH"/tca_ingress.conf
}

# 解压编译后文件
function init_unzip_build() {
  LOG_INFO "解压编译后文件到 $TCA_WEB_DEPLOY_PATH ..."
  rm -rf "${TCA_WEB_DEPLOY_PATH:?}"/
  mkdir -p "$TCA_WEB_DEPLOY_PATH"
  cd "$TCA_WEB_DEPLOY_SOURCE_PATH"/build_zip/ || exit
  # 遍历并解压
  MICRO_FRONTEND="$MICRO_FRONTEND_FRAMEWORK $MICRO_FRONTEND_APPS $MICRO_FRONTEND_DOCUMENT"
  for app in $MICRO_FRONTEND; do
    unzip -q -o "$app".zip -d "$TCA_WEB_DEPLOY_PATH"/"$app"
  done
  cd "$TCA_WEB_DEPLOY_SOURCE_PATH" || exit
}

# 初始化配置 framework
function init_framework_web() {
  LOG_INFO "初始化配置 $MICRO_FRONTEND_FRAMEWORK ..."
  # index meta 配置项
  MICRO_FRONTEND_API=/static/configs.json
  MICRO_FRONTEND_SETTING_API=/static/settings.json
  TITLE=腾讯云代码分析
  DESCRIPTION=腾讯云代码分析，用心关注每行代码迭代、助力传承卓越代码文化！精准跟踪管理代码分析发现的代码质量缺陷、代码规范、代码安全漏洞、无效代码，以及度量代码复杂度、重复代码、代码统计。
  KEYWORDS=代码检查、圈复杂度、重复代码、代码统计
  FAVICON=/static/images/favicon.ico
  FRAMEWORK_DEPLOY_PATH=$TCA_WEB_DEPLOY_PATH/$MICRO_FRONTEND_FRAMEWORK

  LOG_INFO "index meta 配置 ..."
  replace_content="
  s|__TITLE__|$TITLE|g; \
  s|__KEYWORDS__|$KEYWORDS|g; \
  s|__DESCRIPTION__|$DESCRIPTION|g; \
  s|__FAVICON__|$FAVICON|g; \
  "
  LOG_INFO "[INFO]:index.html RUNTIME is enabled"
  LOG_INFO "[INFO]: change 404.html, unsupported-browser.html"
  sed -i "$replace_content" "$FRAMEWORK_DEPLOY_PATH"/404.html
  sed -i "$replace_content" "$FRAMEWORK_DEPLOY_PATH"/unsupported-browser.html

  LOG_INFO "[INFO]: change index.html"
  sed \
    "
    $replace_content \
    s|__MICRO_FRONTEND_API__|$MICRO_FRONTEND_API|g; \
    s|__MICRO_FRONTEND_SETTING_API__|$MICRO_FRONTEND_SETTING_API|g; \
    " \
    "$FRAMEWORK_DEPLOY_PATH"/index.runtime.html >"$FRAMEWORK_DEPLOY_PATH"/index.html

  LOG_INFO "conf 配置迁移 ..."
  # 将conf目录中的配置文件拷贝到 $MICRO_FRONTEND_FRAMEWORK static目录下
  cp "$TCA_WEB_DEPLOY_SOURCE_PATH"/conf/settings.json "$FRAMEWORK_DEPLOY_PATH"/static/settings.json
  cp "$TCA_WEB_DEPLOY_SOURCE_PATH"/conf/configs.json "$FRAMEWORK_DEPLOY_PATH"/static/configs.json
  LOG_INFO "$MICRO_FRONTEND_FRAMEWORK 配置完毕"
}

# 初始化配置web的nginx配置
function init_web_nginx() {
  LOG_INFO "初始化配置web的nginx配置 ..."
  SET_DEFAULT_SERVER=""
  if [ "$IS_DOCKER" == "TRUE" ]; then
    SET_DEFAULT_SERVER="default_server"
  fi
  apps=$(echo "$MICRO_FRONTEND_APPS" | sed 's/[ ]/\\|/g')
  sed \
    "
    s|SERVER_NAME|$TCA_WEB_HOST|g; \
    s|SET_DEFAULT_SERVER|$SET_DEFAULT_SERVER|g; \
    s|PORT|$TCA_WEB_PORT|g; \
    s|NGINX_LOG_PATH|$NGINX_LOG_PATH|g; \
    s|WEB_DEPLOY_PATH|$TCA_WEB_DEPLOY_PATH|g; \
    s|SERVER_ENV|$TCA_SERVER_ADDR|g; \
    s|MICRO_FRONTEND_FRAMEWORK|$MICRO_FRONTEND_FRAMEWORK|g; \
    s|MICRO_FRONTEND_DOCUMENT|$MICRO_FRONTEND_DOCUMENT|g; \
    s|MICRO_FRONTEND_APPS|$apps|g; \
    " \
    "$TCA_WEB_DEPLOY_SOURCE_PATH"/nginx/ingress.conf >"$NGINX_CONF_PATH"/tca_ingress.conf
}

# 打印环境变量配置
function log_env() {
  LOG_INFO "============================前端配置说明============================"
  LOG_INFO "| 前端服务端口: TCA_WEB_PORT --- $TCA_WEB_PORT"
  LOG_INFO "| 前端服务SERVER_NAME: TCA_WEB_HOST --- $TCA_WEB_HOST"
  LOG_INFO "| 前端服务访问的后端地址: SERVER_ENV --- $TCA_SERVER_ADDR"
  LOG_INFO "| 前端服务NGINX配置地址: NGINX_CONF_PATH --- $NGINX_CONF_PATH"
  LOG_INFO "| 前端服务资源部署地址: WEB_DEPLOY_PATH --- $TCA_WEB_DEPLOY_PATH"
  LOG_INFO "| 前端服务日志地址: NGINX_LOG_PATH --- $NGINX_LOG_PATH"
  LOG_INFO "========================end 前端配置说明 end========================"
}

function init_web_config() {
  # 校验是否存在unzip命令
  command_exists unzip || error_exit "unzip command not installed"
  clear_assets
  init_unzip_build
  init_framework_web
  init_web_nginx
  log_env
}
