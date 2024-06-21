#!/bin/bash
CURRENT_SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")";pwd)
TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$(dirname $CURRENT_SCRIPT_PATH; pwd)"}
PYTHON_SRC_URL=${PYTHON_SRC_URL:-"https://www.python.org/ftp/python/3.7.12/Python-3.7.12.tgz"}
PYTHON_SRC_PKG_PATH=${PYTHON_SRC_PKG_PATH:-"/tmp/Python-3.7.12.tgz"}
PYTHON_SRC_PKG_CACHE_PATH=${PYTHON_SRC_PKG_CACHE_PATH}
PYTHON_SRC_PATH=${PYTHON_SRC_PATH:-"/usr/local/src/Python-3.7.12"}
PYTHON_SRC_DIR=$(dirname  $PYTHON_SRC_PATH)
PYTHON_INSTALL_PATH=${PYTHON_INSTALL_PATH:-"/usr/local/python3"}
PYPI_MIRROR_DOMAIN=${PYPI_MIRROR_DOMAIN:-"mirrors.cloud.tencent.com"}
PYPI_MIRROR_URL="https://$PYPI_MIRROR_DOMAIN/pypi/simple"
LINUX_OS=""

source $TCA_SCRIPT_ROOT/utils.sh

function check_python() {
    ret=""
    if command_exists python; then
        result=$( python --version | grep "^Python 3.7." )
        if [ "$result" = "" ]; then
            ret="false"
        else
            ret="true"
        fi
    else
        ret="false"
    fi
    echo "$ret"
}

function check_python_pkg_cache() {
    if [ -n "$PYTHON_SRC_PKG_CACHE_PATH" ]; then
        ret="true"
    else
        ret="false"
    fi
    echo "$ret"
}

function download_python_src() {
    LOG_INFO "[PythonInstall] Download Python src from $PYTHON_SRC_URL, save to $PYTHON_SRC_PKG_PATH"
    LOG_WARN "    * 注意：如果下载失败或速度较慢，可以中断当前脚本（中断后可以重新启动），然后手动下载上述链接的Python包，通过环境变量 [ PYTHON_SRC_PKG_CACHE_PATH ] 指定Python包的路径"
    LOG_WARN "    * 比如：手动下载了Python源码压缩包到 /tmp/ 目录下，可以在运行脚本前设置： export PYTHON_SRC_PKG_CACHE_PATH=/tmp/Python-3.7.12.tgz"
    wget -O $PYTHON_SRC_PKG_PATH $PYTHON_SRC_URL || error_exit "Download Python src failed"
}

function pre_install_for_python() {
    ## 安装编译依赖组件
    LOG_INFO "[PythonInstall] Pre install tools"
    case "$LINUX_OS" in
        centos|rhel|sles|tlinux|tencentos)
            tools="wget zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gcc make libffi-devel xz-devel openldap-devel"
            LOG_INFO "    Start run: yum install tools: $tools"
	        yum -q -y install $tools || error_exit "[PythonInstall] pre install tools failed"
        ;;
        ubuntu|debian|raspbian)
            tools="wget build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev libbz2-dev tk-dev gcc make libsasl2-dev libldap2-dev libssl-dev"
            LOG_INFO "    Start run: apt-get update and apt-get install $tools"
            apt-get update -qq >/dev/null || error_exit "[PythonInstall] pre install tools failed"
            DEBIAN_FRONTEND=noninteractive apt-get -y install -qq $tools >/dev/null || error_exit "[PythonInstall] pre install tools failed"
        ;;
        *)
            LOG_ERROR "$LINUX_OS not supported."
            exit 1
        ;;
    esac
    LOG_INFO "[PythonInstall] Pre install tools successfully."
}

function check_python_install_path() {
    test -d "$PYTHON_INSTALL_PATH" || error_exit "$PYTHON_INSTALL_PATH exists. Please set 'PYTHON_INSTALL_PATH' value to install other dir."
}

function compile_and_link_python() {	
    LOG_INFO "[PythonInstall] Extract into $PYTHON_SRC_PATH"
    # 解压源码到/usr/local/src目录
	tar zxf $PYTHON_SRC_PKG_PATH -C $PYTHON_SRC_DIR && cd $PYTHON_SRC_PATH
    LOG_INFO "[PythonInstall] Config and install to $PYTHON_INSTALL_PATH [Please wait for moment.]"
    # 编译配置和安装
    ./configure prefix=$PYTHON_INSTALL_PATH --enable-shared >/dev/null && make -j8 >/dev/null && make install >/dev/null && make clean >/dev/null || error_exit "Install Python src failed"
    # 链接构建产出的Python可执行文件到/usr/local/bin目录
    check_ln_file /usr/local/bin/python $PYTHON_INSTALL_PATH/bin/python3
    ln -s $PYTHON_INSTALL_PATH/bin/python3 /usr/local/bin/python
    check_ln_file /usr/local/bin/python3 $PYTHON_INSTALL_PATH/bin/python3
    ln -s $PYTHON_INSTALL_PATH/bin/python3 /usr/local/bin/python3
    # 链接构建产出的pip3可执行文件到/usr/local/bin目录
    check_ln_file /usr/local/bin/pip $PYTHON_INSTALL_PATH/bin/pip3
    ln -s $PYTHON_INSTALL_PATH/bin/pip3 /usr/local/bin/pip
    check_ln_file /usr/local/bin/pip3 $PYTHON_INSTALL_PATH/bin/pip3
    ln -s $PYTHON_INSTALL_PATH/bin/pip3 /usr/local/bin/pip3
    # 链接构建产出的Python动态库
    ln -s $PYTHON_INSTALL_PATH/lib/libpython3.7m.so.1.0 /usr/lib/libpython3.7m.so.1.0
    # 配置动态库
    ldconfig
    # 配置路径
    export PATH=/usr/local/bin:$PATH
}

function set_pypi_mirror() {
    LOG_INFO "[PythonInstall] Set pypi config [ $PYPI_MIRROR_URL ]"
    mkdir -p ~/.pip/
    echo "[global]
index-url = $PYPI_MIRROR_URL
[install]
trusted-host=$PYPI_MIRROR_DOMAIN" > ~/.pip/pip.conf
    use_right_pip "install -q -U pip"
}

function quiet_install_python() {
    LINUX_OS=$( get_linux_os )
    LOG_INFO "[PythonInstall] Check Python version"
    ret=$( check_python )
    if [ "$ret" == "true" ]; then
        LOG_WARN "This machine had installed Python3.7"
        return 0
    fi
    
    pre_install_for_python

    cache=$( check_python_pkg_cache )
    if [ "$cache" == "false" ]; then
        download_python_src
    else
        LOG_INFO "[PythonInstall] Use Python PKG Cache: "$PYTHON_SRC_PKG_CACHE_PATH
        PYTHON_SRC_PKG_PATH=$PYTHON_SRC_PKG_CACHE_PATH
    fi
    compile_and_link_python
    check_python
    set_pypi_mirror
    LOG_INFO "[PythonInstall] Install Python3.7.12 successfully."
}

function interactive_install_python() {
    ret=$( check_python )
    if [ "$ret" == "true" ]; then
        return 0
    fi
    LOG_WARN "Deploying TCA depend on Python3.7. Current machine has not installed Python3.7."
    LOG_INFO "Do you want to install [Python3.7] by this script?"
    read -p "Please enter:[Y/N]" result
    case $result in
            [yY])
                quiet_install_python
                ;;
            [nN])
                LOG_WARN "Cancel install Python3.7"
                return 1
                ;;
            *)
                LOG_ERROR "Invalid input. Stop."
                exit 1
                ;;
        esac
}
