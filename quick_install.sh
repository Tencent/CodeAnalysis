#!/bin/sh
# -*-*-*-*-*- 持续完善ING -*-*-*-*-*-
# TCA Server与Web Docker-Compose 一键部署脚本
# 1. 支持检测Docker和安装Docker
# 2. 支持检测Docker状态，并进行启动
# 3. 支持检测Docker-Compose和安装Docker-Compose
# 4. 一键部署Server与Web服务
# -*-*-*-*-*- 持续完善ING -*-*-*-*-*-


is_dry_run() {
    if [ -z "$DRY_RUN" ]; then
        return 1
    else
        return 0
    fi
}

command_exists() {
    command -v "$@" > /dev/null 2>&1
}

install_docker() {
    echo "* Download docker and install"
    set -x
    $sh_c 'curl -fsSL https://get.docker.com -o get-docker.sh'
    $sh_c 'sh ./get-docker.sh'
    set +x
    if is_dry_run; then
        $sh_c 'rm ./get-docker.sh'
    fi
}

check_docker_service() {
    if [ -e /var/run/docker.sock ]; then
        set -x
        $sh_c 'docker version'
        set +x
        return 0
    else
        return 1
    fi
}

start_docker_service() {
    echo "* Start Docker service"
    set -x 
    $sh_c 'systemctl restart docker'
    start_docker_exit_code=$?
    set +x

    if is_dry_run; then
        return
    fi

    if [ "$start_docker_exit_code" = "0" ]; then
        echo "* Start Docker success"
    else
        ehco "\033[33m!! Start Docker failed. Please check log\033[0m"
        exit $start_docker_exit_code
    fi
}

install_docker_compose() {
    echo "# Download docker-compose and install"
    set -x
    docker_compose_url="https://github.com/docker/compose/releases/download/1.27.2/docker-compose-$(uname -s)-$(uname -m)"
    $sh_c "curl -L ${docker_compose_url} -o /usr/local/bin/docker-compose"
    $sh_c 'chmod +x /usr/local/bin/docker-compose'
    retval=$?
    set +x
    if [ "$retval" -ne 0 ]; then
        echo -e "\033[31m!! Download docker-compose failed.\033[0m"; 
        echo -e "\033[33m* Please download manually, url: ${docker_compose_url}"
        echo -e "   After download, copy to /usr/loca/bin/ and execute command: chmod +x /usr/local/bin/docker-compose"
        echo -e "   docker-compose install Tutorial: https://docs.docker.com/compose/install/#install-compose-on-linux-systems \033[0m"
        exit 1; 
    fi
}

start_tca_service() {
    set -x
    $sh_c './compose_init.sh'
    set +x
}

deploy() {
    echo "-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-"
    echo "         TCA deloy script          "
    echo "-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-"

    user="$(id -un 2>/dev/null || true)"

    sh_c='sh -c'
    if [ "$user" != 'root' ]; then
        if command_exists sudo; then
            sh_c='sudo -E sh -c'
        elif command_exists su; then
            sh_c='su -c'
        else
            echo -e "\033[31mError: this installer needs the ability to run commands as root."
            echo -e " We are unable to find either \"sudo\" or \"su\" available to make this happen.\033[0m"
            exit 1
        fi
    fi

    if is_dry_run; then
        sh_c="echo"
    fi

    echo
    echo "###################################"
    echo " 1. Check Docker                   "
    echo "###################################"
    echo

    if command_exists docker; then
        echo -e "\033[32m* This machine had installed Docker, continue to deploy. \033[0m\n"
        ( set -x; sleep 2 )
    else
        echo -e "\033[33m!! This machine does not install Docker. Do you want to install by this script?\033[0m"
        read -p " ?? Please enter:[Y/N] " result

        case $result in
            [yY])
                echo "* Start to install Docker..."
                ( set -x; sleep 2 )
                install_docker
                ;;
            [nN])
                echo -e "\033[33m!! Stop to deploy...\033[0m"
                exit 1
                ;;
            *)
                echo -e "\033[33m!! Invalid input. Stop to deploy...\033[0m"
                exit 1
                ;;
        esac
    fi

    check_docker_service
    if [ "$?" -ne 0 ] ; then
        echo -e "\033[33m!! Docker service was not working. Do you want to start it by this script?\033[0m"        
        read -p " ?? Please enter:[Y/N] " result

        case $result in
            [yY])
                echo "* Start to run Docker service..."
                ( set -x; sleep 2 )
                start_docker_service
                ;;
            [nN])
                echo -e "\033[33m!! Stop to deploy...\033[0m"
                exit 1
                ;;
            *)
                echo -e "\033[33m!! Invalid input. Stop to deploy...\033[0m"
                exit 1
                ;;
        esac
    fi

    echo
    echo "###################################"
    echo " 2. Check Docker-Compose           "
    echo "###################################"
    echo

    if command_exists docker-compose; then
        echo -e "\033[32m* This machine had installed docker-compose, continue to deploy\n\033[0m"
        ( set -x; sleep 2 )
    else
        echo -e "\033[33m !! This machine does not install docker-compose. Do you want to install by this script?\033[0m"
        read -p " ?? Please enter:[Y/N] " result

        case $result in
            [yY])
                echo " * Start to install docker-compose..."
                ( set -x; sleep 5 )
                install_docker_compose
                ;;
            [nN])
                echo -e "\033[33m!! Stop to deploy...\033[0m"
                exit 1
                ;;
            *)
                echo -e "\033[33m!! Invalid input. Stop to deploy...\033[0m"
                exit 1
                ;;
        esac
    fi

    echo 
    echo "###################################"
    echo " 3. Deploy TCA Server & Web        "
    echo "###################################"
    echo 
    ( set -x; sleep 2 )
    start_tca_service
}

deploy