#!/usr/bin/env sh
# Customizable environment variables:
# +---------+-------------------+----------------------------------------------+
# | Name | Default Value | Intro |
# +---------+-------------------+----------------------------------------------+
# | UPDATE_ALL | <none> | 全部更新 |
# | UPDATE_FRAMEWORK | <none> | 更新framework微前端 |
# | UPDATE_LAYOUT | <none> | 更新tca-layout微前端 |
# | UPDATE_LOGIN | <none> | 更新login微前端 |
# | UPDATE_ANALYSIS | <none> | 更新tca-analysis微前端 |
# | UPDATE_DOCUMENT | <none> | 更新document |
# +---------+-------------------+----------------------------------------------+

###########################
### 更新脚本，用于更新前端镜像资源
### 执行方式：
### 方式一：直接执行 sh update.sh $param 即可，
###        其中$param可以是 all framework layout login analysis document，多个用,分隔
###        如：sh update.sh all, sh update.sh layout,analysis,document
### 方式二：查阅上述环境变量，先export对应环境变量，再 sh update.sh
###########################

# 获取当前脚本执行目录，绝对路径
CUR_RUN_PATH=$(cd $(dirname $0) && pwd)
cd $CUR_RUN_PATH

# 提供参数执行，eg sh update.sh login,layout
array=(${1//\,/ })
for var in ${array[@]}; do
  case "$var" in
  "all")
    UPDATE_ALL=TRUE
    ;;
  "framework")
    UPDATE_FRAMEWORK=TRUE
    ;;
  "layout")
    UPDATE_LAYOUT=TRUE
    ;;
  "login")
    UPDATE_LOGIN=TRUE
    ;;
  "analysis")
    UPDATE_ANALYSIS=TRUE
    ;;
  "document")
    UPDATE_DOCUMENT=TRUE
    ;;
  *)
    echo "未匹配到正确的参数"
    ;;
  esac
done

# 微前端静态资源存放位置
WWW_DIR_PATH="/usr/share/nginx/www"

# 根据更新参数判断更新内容
function update_unzip_build() {

  mkdir -p ${WWW_DIR_PATH}
  cd ${CUR_RUN_PATH}/build_zip/

  if [ -n "${UPDATE_ALL}" ] || [ -n "${UPDATE_FRAMEWORK}" ]; then
    echo "移除 framework 内容 ..."
    rm -rf ${WWW_DIR_PATH}/framework/
    echo "解压并更新 framework ..."
    unzip -d ${WWW_DIR_PATH}/framework framework.zip
  fi

  if [ -n "${UPDATE_ALL}" ] || [ -n "${UPDATE_LAYOUT}" ]; then
    echo "移除 tca-layout 内容 ..."
    rm -rf ${WWW_DIR_PATH}/tca-layout/
    echo "解压并更新 tca-layout ..."
    unzip -d ${WWW_DIR_PATH}/tca-layout tca-layout.zip
  fi

  if [ -n "${UPDATE_ALL}" ] || [ -n "${UPDATE_LOGIN}" ]; then
    echo "移除 login_web 内容 ..."
    rm -rf ${WWW_DIR_PATH}/login/
    echo "解压并更新 login_web ..."
    unzip -d ${WWW_DIR_PATH}/login login.zip
  fi

  if [ -n "${UPDATE_ALL}" ] || [ -n "${UPDATE_ANALYSIS}" ]; then
    echo "移除 tca-analysis 内容 ..."
    rm -rf ${WWW_DIR_PATH}/tca-analysis/
    echo "解压并更新 tca-analysis ..."
    unzip -d ${WWW_DIR_PATH}/tca-analysis tca-analysis.zip
  fi

  if [ -n "${UPDATE_ALL}" ] || [ -n "${UPDATE_DOCUMENT}" ]; then
    echo "移除 tca-document 内容 ..."
    rm -rf ${WWW_DIR_PATH}/tca-document/
    echo "解压并更新 tca-document ..."
    unzip -d ${WWW_DIR_PATH}/tca-document tca-document.zip
  fi

  cd ${CUR_RUN_PATH}
}

# 初始化配置 framework
function init_framework_web() {
  echo "初始化配置 framework ..."
  RUNTIME="TRUE"
  MICRO_FRONTEND_API=/static/configs.json
  MICRO_FRONTEND_SETTING_API=/static/settings.json
  TITLE=腾讯云代码分析
  DESCRIPTION=腾讯云代码分析，用心关注每行代码迭代、助您传承卓越代码文化！精准跟踪管理代码分析发现的代码质量缺陷、代码规范、代码安全漏洞、无效代码，以及度量代码复杂度、重复代码、代码统计。
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
    sed -i "${replace_content}" ${WWW_DIR_PATH}/framework/404.html
    sed -i "${replace_content}" ${WWW_DIR_PATH}/framework/unsupported-browser.html

    echo "[INFO]: change index.html"
    sed \
      "
      ${replace_content} \
      s|__MICRO_FRONTEND_API__|${MICRO_FRONTEND_API}|g; \
      s|__MICRO_FRONTEND_SETTING_API__|${MICRO_FRONTEND_SETTING_API}|g; \
      " \
      ${WWW_DIR_PATH}/framework/index.runtime.html >${WWW_DIR_PATH}/framework/index.html
  fi
}

# 将conf目录中的配置文件拷贝到 framework_web static目录下
function init_conf() {
  echo "将配置项拷贝至 framework static目录下"
  # \cp强制覆盖
  \cp ${CUR_RUN_PATH}/conf/settings.json ${WWW_DIR_PATH}/framework/static/settings.json
  \cp ${CUR_RUN_PATH}/conf/configs.json ${WWW_DIR_PATH}/framework/static/configs.json
}

# 重启nginx
function reload() {
  echo "重启nginx ..."
  nginx_is_start=$(ps -C nginx --no-header | wc -l)
  if [ ${nginx_is_start} -eq 0 ]; then
    nginx -t
    nginx
  else
    nginx -s reload
  fi
}

update_unzip_build

if [ -n "${UPDATE_ALL}" ] || [ -n "${UPDATE_FRAMEWORK}" ]; then
  echo "更新 framework 后，重新配置"
  init_framework_web
fi

init_conf
reload
