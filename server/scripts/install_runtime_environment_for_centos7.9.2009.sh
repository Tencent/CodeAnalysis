#!/bin/env bash

#################################################################################
# util function
#################################################################################

function info(){
	echo ""
	echo -e "\033[32m[$(date "+%Y/%m/%d %H:%M:%S")] [INFO]: $1\033[0m"
	echo -e "\033[32m__________________________________________________________________________________________\033[0m"
	sleep 3
}


#################################################################################
# Install python3.7.12
#################################################################################
function install_python(){
	info '开始安装 python3.7.12'
	
	# 参数：again，覆盖安装
	if [ "again" != "$1" ];then
		# 检测是否已安装, 
		version=`python --version`
		if [ "$version" == "Python 3.7.12" ];then
			echo '已安装：[ python3.7.12 ]'
			return 1;
		fi
	fi
	

	## 下载 Python 源码，如果已下载源码在脚本当前目录下，可注释跳过下载步骤
	wget https://www.python.org/ftp/python/3.7.12/Python-3.7.12.tgz

	info 'yum -y install wget zlib-devel bzip2-devel openssl-devel [ gcc, make, ....... ]: '
	## 安装编译依赖组件
	yum -y install wget zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gcc make libffi-devel xz-devel

	## 解压安装
	# 解压到/usr/local/src目录
	tar zvxf Python-3.7.12.tgz -C /usr/local/src
	cd /usr/local/src/Python-3.7.12
	# 编译前配置
	./configure prefix=/usr/local/python3 --enable-shared
	# 编译构建
	make -j8
	# 安装Python
	make install
	# 清理编译产出的中间文件
	make clean
	# 链接构建产出的Python可执行文件到/usr/local/bin目录
	ln -s /usr/local/python3/bin/python3 /usr/local/bin/python
	# 链接构建产出的pip3可执行文件到/usr/local/bin目录
	ln -s /usr/local/python3/bin/pip3 /usr/local/bin/pip
	# 链接构建产出的Python动态库
	ln -s /usr/local/python3/lib/libpython3.7m.so.1.0 /usr/lib/libpython3.7m.so.1.0
	# 配置动态库
	ldconfig

	## 检查Python版本是否安装成功
	info '检查 Python 版本'
	python --version
	echo ''

	## pypi下载源配置
	info '更新pypi源 [ https://mirrors.cloud.tencent.com/pypi/simple ]'
	mkdir ~/.pip/
	echo "[global]
	index-url = https://mirrors.cloud.tencent.com/pypi/simple
	[install]
	trusted-host=mirrors.cloud.tencent.com" > ~/.pip/pip.conf
	echo '完成!'

	## for server deploy
	info '安装 [pip install gunicorn==20.1.0] 并生成软链'
	pip install gunicorn==20.1.0
	ln -s /usr/local/python3/bin/gunicorn /usr/local/bin/gunicorn
	echo -e "\033[1;42;37m[$(date "+%Y/%m/%d %H:%M:%S")] [Check]: 检查 gunicorn\033[0m"
	gunicorn -v
	echo -e "\033[1;42;37m[$(date "+%Y/%m/%d %H:%M:%S")] [Check]: 检查 gunicorn\033[0m"
	echo '完成!'

	## for celery
	info '安装 [pip install celery==5.2.2] 并生成软链'
	pip install celery==5.2.2
	ln -s /usr/local/python3/bin/celery /usr/local/bin/celery
	echo -e "\033[1;42;37m[$(date "+%Y/%m/%d %H:%M:%S")] [Check]: 检查 celery\033[0m"
	celery --version
	echo -e "\033[1;42;37m[$(date "+%Y/%m/%d %H:%M:%S")] [Check]: 检查 celery\033[0m"

	# 使环境变量生效，避免出现 unknown command 错误
	export PATH=/usr/local/bin:$PATH
	echo '完成!'
}



#################################################################################
# Install redis
#################################################################################
function install_redis(){
	info '开始安装 redis [ yum install -y redis --nogpgcheck ]'

	cd ~/
	# 安装 redis
	yum install -y epel-release
	yum install -y redis --nogpgcheck

	# 修改配置文件
	cp /etc/redis.conf /etc/redis.conf.bak
	REDIS_PASS=tca123
	echo requirepass $REDIS_PASS >> /etc/redis.conf

	# 启动 redis
	systemctl start redis

	# 设置开机启动
	systemctl enable redis

	# 查看redis运行状态
	systemctl status redis
}



#################################################################################
# Install MySQL
#################################################################################
function install_mysql(){
	info '开始安装 MySQL [ yum install -y mysql-community-server --nogpgcheck ]'

	cd ~/
	# 安装 mysql yum源
	wget https://repo.mysql.com//mysql57-community-release-el7-11.noarch.rpm
	yum localinstall -y mysql57-community-release-el7-11.noarch.rpm

	# 安装 MySQL
	yum install -y mysql-community-server --nogpgcheck

	# 启动MySQL服务，默认开机启动
	systemctl start mysqld

	# 查看 MySQL 服务状态
	systemctl status mysqld

	# 获取初始密码
	MYSQL_PASS=`grep "A temporary password" /var/log/mysqld.log | awk -F ": " '{ print $2 }'`

	# 修改密码
	NEW_PASS=Password@2021
	mysql -uroot -p$MYSQL_PASS  --connect-expired-password -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '"$NEW_PASS"';"
}



#################################################################################
# Install nginx
#################################################################################
function install_nginx(){
	info '开始安装 nginx [ yum install -y nginx ]'

	cd ~/
	# 安装 nginx
	yum install -y nginx

	# 启动 nginx
	systemctl start nginx.service

	# 设置开机启动
	systemctl enable nginx.service

	# 查看服务状态
	systemctl status nginx.service
}


#################################################################################
# export http_proxy for pip
#################################################################################


#################################################################################
# report
#################################################################################
function report(){
	info '服务器使用了 HTTP 代理网络的环境可能还需要为 pip 设置代理，命令如下'
	echo '为 pip 配置代理(替换为自己的代理服务地址): 
	export HTTP_PROXY=http://172.29.1.1:19191
	export HTTPS_PROXY=http://172.29.1.1:19191'
	
	
	info '运行环境安装完成并启动，关键信息如下：'
	echo -e '\tMySQL:'
	echo -e '\t_______________________________________________________________'
	echo -e "\t\tHostname: 127.0.0.1"
	echo -e "\t\tUsername: root"
	echo -e "\t\tPassword: $NEW_PASS"
	echo -e ""
	
	echo -e '\tRedis:'
	echo -e '\t_______________________________________________________________'
	echo -e "\t\tHostname: 127.0.0.1"
	echo -e "\t\tPassword: $REDIS_PASS"
	echo -e ""
	
	info '下一步，部署服务提示......'
	echo -e '\t部署 Server:'
	echo -e '\t_______________________________________________________________'
	echo -e "\t\t1. 初始化DB、安装依赖和运行初始化脚本: [ bash ./scripts/deploy.sh init ]"
	echo -e "\t\t2. 启动服务 [ bash ./scripts/deploy.sh start ]"
	echo -e "\t\t   停止服务 [ bash ./scripts/deploy.sh stop ]"
	echo -e ""
	
	
	echo -e '\t部署 Web:'
	echo -e '\t_______________________________________________________________'
	echo -e "\t\t1. 进入 Web 服务工作目录: [ ~/CodeAnalysis/web/tca-deploy-source ]"
	echo -e "\t\t2. 自定义 SERVER_NAME 设置(可选)： [ export LOCAL_IP=xxx.xxx.xxx .xxx  ]"
	echo -e "\t\t3. 启动 Web 服务：[ bash ./scripts/deploy.sh init -d ]"
	echo -e ""
	
	echo -e '\t完成以上部署步骤后，可能存在一些问题，可进行以下尝试：'
	echo -e '\t_______________________________________________________________'
	echo -e "\t\t1. [ bash ./scripts/deploy.sh start ] && [ nginx -c /etc/nginx/nginx.conf ]"
	echo -e "\t\t2. 或者重启后执行第一步"
	echo -e ""
}



#################################################################################
# main function
#################################################################################
function main(){
	info '[ Tested with CentOS7.9.2009 ] Start installing......'
	cat << EOF
网络不佳，或者访问国外网站慢的情况下，
	1. 建议先下载以下两个文件，放置到本脚本同一目录下，
	2. 然后注释脚本相关下载代码，如下：
		wget https://www.python.org/ftp/python/3.7.12/Python-3.7.12.tgz
		wget https://repo.mysql.com//mysql57-community-release-el7-11.noarch.rpm
EOF
	
	# 1. python3.7.12
	install_python
	
	# 2. redis
	install_redis
	
	# 3. mysql
	install_mysql
	
	# 4. nginx
	install_nginx
	
	# *. report
	report

}

# Go for it!
main
