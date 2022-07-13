#!/bin/bash
CURRENT_SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")";pwd)
TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$(dirname $CURRENT_SCRIPT_PATH; pwd)"}
PYTHON_SRC_URL=${PYTHON_SRC_URL:-"https://www.python.org/ftp/python/3.7.12/Python-3.7.12.tgz"}
PYTHON_SRC_PKG_PATH=${PYTHON_SRC_PKG_PATH:-"/tmp/Python-3.7.12.tgz"}
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
        result=$(python --version | grep "^Python 3.7.")
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

function download_python_src() {
    LOG_INFO "Download Python src from $PYTHON_SRC_URL, save to $PYTHON_SRC_PKG_PATH"
    wget -O $PYTHON_SRC_PKG_PATH $PYTHON_SRC_URL || error_exit "Download Python src failed"
}

function pre_install() {
    ## 安装编译依赖组件
    LOG_INFO "Pre install tools"
    case "$LINUX_OS" in
        centos|rhel|sles|tlinux|tencentos)
            tools="wget zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gcc make libffi-devel xz-devel"
            LOG_INFO "tools: $tools"
	        yum -y install $tools
        ;;
        ubuntu|debian|raspbian)
            tools="wget build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev libbz2-dev tk-dev gcc make"
            LOG_INFO "tools: $tools"
            apt update
            DEBIAN_FRONTEND=noninteractive apt -y install $tools
        ;;
        *)
            LOG_ERROR "$LINUX_OS not supported."
            exit 1
        ;;
    esac
}

function check_python_install_path() {
    test -d "$PYTHON_INSTALL_PATH" || error_exit "$PYTHON_INSTALL_PATH exists. Please set 'PYTHON_INSTALL_PATH' value to install other dir."
}

function install_python() {	
    LOG_INFO "Extract into $PYTHON_SRC_PATH"
    # 解压源码到/usr/local/src目录
	tar zvxf $PYTHON_SRC_PKG_PATH -C $PYTHON_SRC_DIR && cd $PYTHON_SRC_PATH
    LOG_INFO "Config and install to $PYTHON_INSTALL_PATH"
    # 编译配置和安装
	./configure prefix=$PYTHON_INSTALL_PATH --enable-shared && make -j8 && make install && make clean || error_exit "Install Python src failed"
    # 链接构建产出的Python可执行文件到/usr/local/bin目录
	ln -s $PYTHON_INSTALL_PATH/bin/python3 /usr/local/bin/python
	# 链接构建产出的pip3可执行文件到/usr/local/bin目录
	ln -s $PYTHON_INSTALL_PATH/bin/pip3 /usr/local/bin/pip
	# 链接构建产出的Python动态库
	ln -s $PYTHON_INSTALL_PATH/lib/libpython3.7m.so.1.0 /usr/lib/libpython3.7m.so.1.0
	# 配置动态库
	ldconfig
}

function set_pypi_mirror() {
    LOG_INFO "set pypi config [ $PYPI_MIRROR_URL ]"
	mkdir -p ~/.pip/
	echo "[global]
	index-url = $PYPI_MIRROR_URL
	[install]
	trusted-host=$PYPI_MIRROR_DOMAIN" > ~/.pip/pip.conf
}

function quiet_install_python() {
    LINUX_OS=$( get_linux_os )
    LOG_INFO "Check Python version"
    ret=$( check_python )
    if [ "$ret" == "true" ]; then
        LOG_WARN "This machine had installed Python3.7"
        return 0
    fi
    pre_install
    download_python_src  
    install_python
    check_python
    set_pypi_mirror
    LOG_INFO "Install Python3.7.12 successfully."
}

function interactive_install_python() {
    LOG_INFO "Do you want to install python3.7 by this script?"
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
