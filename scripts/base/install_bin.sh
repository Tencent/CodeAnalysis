#!/bin/bash
# 下载 TCA 自研的依赖库二进制文件，避免代码库急速变大

CURRENT_SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")";pwd)
TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$( cd "$(dirname $CURRENT_SCRIPT_PATH)"; pwd )"}

source $TCA_SCRIPT_ROOT/utils.sh

# 代码库根目录
TCA_ROOT=$( cd "$(dirname $TCA_SCRIPT_ROOT)"; pwd )
LIB_GITHUB_URL=${LIB_GITHUB_URL:-"https://github.com/TCATools/tca_lib/releases/download/v20241015.1/tca_lib-v1.8.zip"}
LIB_GONGFENG_URL=${LIB_GONGFENG_URL:-"https://git.code.tencent.com/TCA/tca-tools/tca_lib.git#v20241015.1"}
LIB_CNB_URL=${LIB_CNB_URL:-"https://cnb.cool/tca/tools/tca_lib.git#v20241015.1"}
LIB_DIR_NAME="tca_lib"


# 下载依赖库包
function downloader() {
    # 只有一个参数
    url=${1}

    ret=1
    # 判断 url 是不是以“.zip”结尾
    # 下载github
    if [[ $url == *\.zip ]]; then
        # 在根目录下下载
        LOG_INFO "start download lib ..."
        wget $url
        cmd_ret=$?
        if [[ ${cmd_ret} == 0 ]] ; then
            filename=$(basename "$url")
            # 解压
            unzip $filename
            rm $filename
            ret=0
        fi
    else
        LOG_INFO "start git clone lib ..."
        # 使用工蜂默认密码
        user=$2
        password=$3
        auth=""
        if [[ "${user}" != "" ]] ; then
            auth=${user}:${password}@
        fi

        # ${url: -11} 中间要有空格，才能是截取后几位
        # 2024/8/2 适配低版本的shell写法
        length=${#url}
        git clone -b ${url: -11} ${url:0:8}${auth}${url:8:length-20}
        cmd_ret=$?
        if [[ ${cmd_ret} == 0 ]] ; then
            # 清理lib中无关文件
            rm -rf "${TCA_ROOT}/${LIB_DIR_NAME}/.git"
            rm "${TCA_ROOT}/${LIB_DIR_NAME}/.gitattributes"
            ret=0
        fi
    fi
    return $ret
}

function readIni()
{ 
    FILENAME=$1; SECTION=$2; KEY=$3
    RESULT=`awk '/\['$SECTION'\]/{a=1}a==1&&$1~/'$KEY'/{print $1}' $FILENAME | grep $KEY= | awk -F '=' '{print $2;exit}'`
    echo $RESULT
}

# 根据client中的配置来决定是下载github的还是工蜂的
function download_lib() {
    config_url=$(readIni ${TCA_ROOT}/client/config.ini "COMMON" "TOOL_CONFIG_URL")
    if [[ $config_url == *"github.com"* ]]; then
        downloader $LIB_GITHUB_URL
    else
        if [[ $config_url == *"cnb.cool"* ]]; then
            downloader $LIB_CNB_URL
        else
            # 工蜂
            user=$(readIni ${TCA_ROOT}/client/config.ini "TOOL_LOAD_ACCOUNT" "USERNAME")
            downloader $LIB_GONGFENG_URL $user $(readIni ${TCA_ROOT}/client/config.ini "TOOL_LOAD_ACCOUNT" "PASSWORD")
        fi
    fi
    ret=$?
    if [[ $ret == 0 ]]; then
        LOG_INFO "Download lib success."
        return 0
    fi
    error_exit "Download lib failed."
}

# 复制到对应位置
function deepmove() {
    src_dir=${1}
    dst_dir=${2}
    # 遍历
    for target in $(find $src_dir -type f); do
        relpath=$(realpath "$target" --relative-to=$src_dir)
        if [ ! -e "$dst_dir/$relpath" ]; then
            # 目标位置不存在
            ret=1
        else
            # 先判断md5值，有变化才复制覆盖
            isSame $target $dst_dir/$relpath
            ret=$?
        fi
        if [[ $ret == 1 ]]; then
            LOG_INFO "update lib: $relpath"
            # 判断目标位置的目录是否存在
            parent_dir=$(dirname "$dst_dir/$relpath")
            if [ ! -d "$parent_dir" ]; then
                mkdir -p "${parent_dir}"
            fi
            cp $target $dst_dir/$relpath
        fi
    done
    rm -r $src_dir
}

function isSame() {
    src_file=${1}
    dst_file=${2}

    src_md5=$(md5sum $src_file | awk '{ print $1 }')
    dst_md5=$(md5sum $dst_file | awk '{ print $1 }')
    # LOG_INFO $src_md5 $dst_md5
    if [[ $src_md5 == $dst_md5 ]]; then
        return 0
    else
        return 1
    fi
}

function interactive_install_bin() {

    # 判断是否设置 USE_LOCAL_TOOL=True，是的话就忽略
    isLocal=$(readIni ${TCA_ROOT}/client/config.ini "COMMON" "USE_LOCAL_TOOL"|tr '[:upper:]' '[:lower:]')
    if [[ $isLocal == "true" ]]; then
        return 0
    fi

    download_lib
    deepmove "${TCA_ROOT}/${LIB_DIR_NAME}" $TCA_ROOT
}

interactive_install_bin
