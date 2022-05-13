# 源代码安装服务端

## 依赖环境

- 系统要求

    - Linux
    - [Pythn 3.7](https://docs.python.org/zh-cn/3.7/using/unix.html)
    - [MySQL 5.7.8](https://dev.mysql.com/doc/mysql-installation-excerpt/5.7/en/) 或更高版本
    - [Redis 4.0](https://redis.io/docs/getting-started/installation/install-redis-on-linux/) 或更高版本
    - [Nginx 1.20.2](https://nginx.org/en/docs/install.html) 或更高版本

- 硬件要求

    - 2核4G内存
    - 100G可用硬盘存储空间

- 权限要求

    - 安装Server依赖软件（python、nginx、yum软件包）需要使用ROOT权限（启动Server服务时可以使用非ROOT用户运行）
    - 需要开放80端口的访问权限(80为TCA平台访问端口)
    - Server服务执行数据库初始化需要依赖``CREATE、ALTER、INDEX、DELETE、LOCK TABLES、SELECT、INSERT、REFERENCES、UPDATE``权限


## 安装步骤

### 部署Server

1. 进入Server服务工作目录（例如 ``~/CodeAnalysis/server/``），以下路径均为目录内的相对路径
2. 配置MySQL和Redis服务，初始化数据（MySQL版本运行版本：5.7）
    - 填写数据库和Redis信息以及根据需要调整配置信息，主要的工程配置已提供默认值，字段说明详见[TCA Server](../references/parameters/server.md)。
    ```bash
    vi ./scripts/config.sh
    ```
    - 初始化DB、安装依赖和运行初始化脚本
    ```bash
    bash ./scripts/deploy.sh init
    ```
    - 将安装好的``celery``与``gunicorn``可执行文件建立软链接到``/usr/local/bin``路径下
    ```bash
    # /path/to/需要替换为celery可执行命令实际的路径，一般在python安装路径的bin目录下，如/usr/local/python3/bin/
    ln -s /path/to/celery /usr/local/bin/celery
    # /path/to/需要替换为gunicorn可执行命令实际的路径，一般在python安装路径的bin目录下，如/usr/local/python3/bin/
    ln -s /path/to/gunicorn /usr/local/bin/gunicorn
    ```
    - 使环境变量生效，避免出现unknown command错误
    ```bash
    export PATH=/usr/local/bin:$PATH
    ```
3. 启动/停止服务
    ```bash
    # 启动服务
    bash ./scripts/deploy.sh start
    # 停止服务
    bash ./scripts/deploy.sh stop
    ```

### 部署Web


1. 完成部署Server并启动服务，后端服务默认登陆账号/密码为：`CodeDog/admin`。

2. 进入web服务部署目录（例如 ``~/CodeAnalysis/web/tca-deploy-source``），以下路径均为目录内的相对路径

3. 部署/更新前端服务

    ```bash
    # 部署、更新都使用此命令
    bash ./scripts/deploy.sh init -d
    ```

    具体请查阅部署脚本内容，可根据业务调整配置。

3. **额外说明**

    `tca-deploy-source/scripts/config.sh` 已配置默认环境变量，用户可根据需要调整环境变量再部署前端服务，具体可查阅脚本内容。
