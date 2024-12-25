#!/bin/bash

# url=${LIB_GITHUB_URL}

# filename=$(basename "$url")
# dirname=${filename%.*}

# lib_image_path="${dirname}/tca_lib/doc/images"
# image_path="images"

# if [[ ! -d $image_path ]]; then
#   if [[ ! -d $lib_image_path ]]; then
#     if [[ ! -f $filename ]]; then
#       wget $url
#     fi
#     unzip $filename -d $dirname
#   fi
#   cp -r $lib_image_path $image_path
# fi

# 当前
CURRENT_PATH=$(
  cd "$(dirname "${BASH_SOURCE[0]}")"
  pwd
)

# 根目录
ROOT_PATH=$(dirname "${CURRENT_PATH}")

cd ${ROOT_PATH}

bash "${ROOT_PATH}"/scripts/base/install_bin.sh

cd ${CURRENT_PATH}
