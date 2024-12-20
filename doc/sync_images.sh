#!/bin/bash

url=${LIB_GITHUB_URL:-"https://github.com/TCATools/tca_lib/releases/download/v20241015.1/tca_lib-v1.8.zip"}

filename=$(basename "$url")
dirname=${filename%.*}

lib_image_path="${dirname}/tca_lib/doc/images"
image_path="images"

if [[ ! -d $image_path ]]; then
  if [[ ! -d $lib_image_path ]]; then
    if [[ ! -f $filename ]]; then
      wget $url
    fi
    unzip $filename -d $dirname
  fi
  cp -r $lib_image_path $image_path
fi
