#!/bin/bash

CURRENT_SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")";pwd)
TCA_SCRIPT_ROOT=${TCA_SCRIPT_ROOT:-"$( cd "$(dirname $CURRENT_SCRIPT_PATH)"; pwd )"}

source $TCA_SCRIPT_ROOT/utils.sh
source $TCA_SCRIPT_ROOT/base/get_os.sh

# 检查git lfs 是否安装
function check_git_lfs(){
    ret=""
    #判断是否存在 git lfs命令
    if command_exists git-lfs; then
        ret="true"
    else
        ret="false"
    fi
    echo "$ret"
}

function check_install_curl () {
    if command -v curl >/dev/null 2>&1; then
        echo "curl installed"
    else
        echo "curl is not installed. Start the installation"
        apt-get update -y && apt-get install curl -y
    fi
}

function check_install_sudo() {
    if command -v sudo >/dev/null 2>&1; then
        echo "sudo installed"
    else
        echo "sudo is not installed. Start the installation"
        apt-get update
        apt-get install sudo
    fi
}

function check_install_sudo_centos() {
    if command -v sudo >/dev/null 2>&1; then
        echo "sudo installed"
    else
        echo "sudo is not installed. Start the installation"
        yum update
        yum -y install sudo

        if [ $? -ne 0 ]; then
            echo "Installation failed, you can try to add a mirror source. url: http://mirror.centos.org "
            exit 1
        fi

    fi
}

function check_install_brew() {
    if command -v brew >/dev/null 2>&1; then
        echo "brew installed"
    else
        echo "brew is not installed. Start the installation. Please go to the official website to install yourself, url: https://brew.sh/ "
    fi
}


function ubuntu_debian_install(){
    LOG_INFO "git lfs installation requires administrator permissions. Are you sure to use administrator permissions?"
    read -p "Please enter:[Y/N]" result
    case $result in
            [yY])
                sleep 2
                curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
                sudo apt-get install git-lfs
                ;;
            [nN])
                echo -e "Cancel install git lfs"
                exit 1
                ;;
            *)
                LOG_ERROR "Invalid input. Stop."
                exit 1
                ;;
    esac
}

function centos_install(){
    LOG_INFO "git lfs installation requires administrator permissions. Are you sure to use administrator permissions?"
    read -p "Please enter:[Y/N]" result
    case $result in
            [yY])
                sleep 2
                curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.rpm.sh | sudo bash
                sudo yum install git-lfs

                if [ $? -ne 0 ]; then
                    echo "Installation failed, you can try to add a mirror source. url: http://mirror.centos.org "
                    exit 1
                fi
                ;;
            [nN])
                echo -e "Cancel install git lfs"
                exit 1
                ;;
            *)
                LOG_ERROR "Invalid input. Stop."
                exit 1
                ;;
    esac


}

function macos_install() {
    brew install git-lfs
}

function windows_install(){
    LOG_WARN "The current version of Windows does not have built-in support for the automatic installation of Git LFS."
    LOG_WARN "Please download manually, url: https://git-lfs.com/"
}


function install_git_lfs(){
    ret=$( check_git_lfs )
    if [ "$ret" == "true" ]; then
        LOG_WARN "This machine had installed git lfs"
        return 0
    fi

    LOG_INFO "Download git lfs and install"


    ret=$( get_os )

    case $ret in
  "Ubuntu")
    LOG_WARN "Your Operating system is Ubuntu"
    check_install_curl
    check_install_sudo
    ubuntu_debian_install
    ;;
  "Debian")
    LOG_WARN "Your Operating system is Debian"
    check_install_curl
    check_install_sudo
    ubuntu_debian_install
    ;;
  "TencentOS")
    LOG_WARN "Your Operating system is TencentOS"
    check_install_sudo_centos
    centos_install
    ;;
  "CentOS")
    LOG_WARN "Your Operating system is CentOS"
    check_install_sudo_centos
    centos_install
    ;;
  "macOS")
    LOG_WARN "Your Operating system is macOS"
    check_install_brew
    macos_install
    ;;
  "Windows")
    LOG_WARN "Your Operating system is Windows"
    windows_install
    exit 1;
    ;;
  *)
    LOG_ERROR "Your operating system is not recognized."
    ;;
esac


    retval=$?
    if [ "$retval" -ne 0 ]; then
        LOG_WARN "Download git lfs failed."
        LOG_WARN "  Please install git lfs manually, git lfs installation guide : https://github.com/git-lfs/git-lfs?tab=readme-ov-file#installing"
        exit 1;
    fi

}

function interactive_install_git_lfs() {
    ret=$( check_git_lfs )
    if [ "$ret" == "true" ]; then
        LOG_WARN "This machine had installed git lfs"
        return 0
    fi

    LOG_WARN "Current machine has not installed git lfs."
    LOG_INFO "Do you want to install git lfs by this script?"
    read -p "Please enter:[Y/N]" result
    case $result in
            [yY])
                sleep 2
                install_git_lfs
                ;;
            [nN])
                echo -e "Cancel install git lfs"
                return 1
                ;;
            *)
                LOG_ERROR "Invalid input. Stop."
                exit 1
                ;;
        esac

}

interactive_install_git_lfs





