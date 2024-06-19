#!/bin/bash

function get_os(){
    ret=""
    # 判断当前操作系统的类型是不是linux
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # 检查当前操作系统是 Ubuntu、Debian 还是 CentOS
      if command -v lsb_release > /dev/null; then
        #检查 lsb_release 命令是否可用,如果该命令可用,用下面这种方式判断
        if [[ $(lsb_release -si) == "Ubuntu" ]]; then
          #echo "Your Operating system is Ubuntu"
          ret="Ubuntu"

        elif [[ $(lsb_release -si) == "Debian" ]]; then
          #echo "Your Operating system is Debian"
          ret="Debian"


        elif [[ $(lsb_release -si) == "TencentOS" ]]; then
          #echo "Your Operating system is TencentOS"
          ret="TencentOS"


        elif [[ $(lsb_release -si) == "CentOS" ]]; then
          #echo "Your Operating system is CentOS"
          ret="CentOS"

        fi
      else
        # 检查 /etc/os-release 文件中是否包含“NAME="CentOS"”字符串，如果包含，则用下面这种方式判断。
        if [[ -f /etc/os-release ]]; then
          if grep -q "Ubuntu" /etc/os-release; then
            #echo "Your Operating system is Ubuntu"
            ret="Ubuntu"

          elif grep -q "Debian" /etc/os-release; then
            #echo "Your Operating system is Debian"
            ret="Debian"

          elif grep -q "TencentOS" /etc/os-release; then
            #echo "Your Operating system is TencentOS"
            ret="TencentOS"


          elif grep -q "CentOS" /etc/os-release; then
            #echo "Your Operating system is CentOS"
            ret="CentOS"

          fi
        fi
      fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
      # 检查当前操作系统是 macOS
      #echo "Your Operating system is macOS"
      ret="macOS"

    elif [[ "$OSTYPE" == "msys" ]]; then
      # 检查当前操作系统是 Windows
      #echo "Your Operating system is Windows"
      ret="Windows"

    elif [[ "$OSTYPE" == "win32" ]]; then
      # 检查当前操作系统是 Windows
      #echo "Your Operating system is Windows"
      ret="Windows"

    else
      #echo "Unknown operating system"
      ret="others"
    fi

    echo "$ret"

}









