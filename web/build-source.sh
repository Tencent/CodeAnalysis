#!/bin/bash

# 用于管道命令 只要一个子命令失败，整个管道命令就失败，脚本就会终止执行
set -eo pipefail

# 打印带颜色的状态，蓝色
function status() {
  echo -e "\033[34m >>> $*\033[0;39m"
}

# 打印带颜色的状态，黄色
function warning() {
  echo -e "\033[33m >>> $*\033[0;39m"
}

# 当前脚本执行目录
CURRENT_PATH=$(
  cd "$(dirname "${BASH_SOURCE[0]}")"
  pwd
)

# web目录
ROOT_PATH=$CURRENT_PATH

cd "$ROOT_PATH"

# git 版本
GIT_REVISION=$(git rev-parse HEAD)
CONF_PATH="${ROOT_PATH}/tca-deploy-source/conf/"
BUILD_ZIP_PATH="${ROOT_PATH}/tca-deploy-source/build_zip/"

# 默认的前端构建资源打包
function default_frontend() {
  dist=${2:-dist}
  status "开始构建 $1 ..."
  GIT_REVISION=$GIT_REVISION yarn build --scope "${1}"
  status "构建完成，开始打包到 tca-deploy-source"
  cd "${ROOT_PATH}"/packages/"${1}"/"${dist}"
  zip -r "${1}".zip ./* --exclude '*.map' --exclude 'stats.json' --exclude '*.txt'
  mv "${1}".zip "${BUILD_ZIP_PATH}" && cd "${ROOT_PATH}"
  status "打包完成 $1"
}

# 文档构建资源打包
function document_frontend() {
  cd "${ROOT_PATH}"
  cd "../doc"
  status "开始构建 $1 ..."
  yarn install && BASE=document yarn build
  dist=${2:-dist}
  status "构建完成，开始打包到 tca-deploy-source"
  cd "${dist}"
  zip -r "${1}".zip ./* --exclude '*.map' --exclude 'stats.json' --exclude '*.txt'
  mv "${1}".zip "${BUILD_ZIP_PATH}" && cd "${ROOT_PATH}"
  status "打包完成 $1"
}

# 子微前端的构建资源打包
function sub_microfrontend() {
  status "开始构建 $1 ..."
  PLATFORM_ENV=open GIT_REVISION=$GIT_REVISION PUBLIC_PATH=/static/$1/ ENABLE_EXTERNALS=TRUE yarn build --scope "$1"
  status "构建完成，开始打包到 tca-deploy-source"
  cd "${ROOT_PATH}"/packages/"${1}"/dist
  zip -r "${1}".zip ./* --exclude '*.map' --exclude 'stats.json' --exclude '*.txt' --exclude '*.html'
  mv "${1}".zip "${BUILD_ZIP_PATH}" && cd "${ROOT_PATH}"
  status "打包完成 $1"
}

function run() {
  BUILD_PKGS=("tca-document" "framework" "login" "tca-layout" "tca-analysis" "tca-manage")
  for pkg_name in "${BUILD_PKGS[@]}"; do
    if [ "$pkg_name" = "framework" ]; then
      default_frontend "$pkg_name"
    elif [ "$pkg_name" = "tca-document" ]; then
      document_frontend "$pkg_name"
    else
      sub_microfrontend "$pkg_name"
    fi
  done
}

function run_config() {
  cd "${ROOT_PATH}"
  SUB_MICRO_FRONTEND_PKGS=("tca-layout" "login" "tca-analysis" "tca-manage")
  configs=''
  for i in "${!SUB_MICRO_FRONTEND_PKGS[@]}"; do
    pkg_name=${SUB_MICRO_FRONTEND_PKGS[$i]}
    configs+=', '$(cat "${ROOT_PATH}"/packages/"${pkg_name}"/dist/"$pkg_name".json)
  done
  # 存在 jq 命令则格式化 json 文件
  if command -v jq &>/dev/null; then
    echo '['"${configs:2}"']' | jq . >"${CONF_PATH}"/configs.json
  else
    echo '['"${configs:2}"']' >"${CONF_PATH}"/configs.json
  fi
}

yarn
run
run_config
