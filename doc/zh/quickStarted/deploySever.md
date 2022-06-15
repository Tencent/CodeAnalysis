# 部署 Server 和 Web

## 通过源代码

### 依赖环境

- 系统环境

  - Linux

  - 最低配置：2核4G内存、100G硬盘存储空间

- 环境准备

  - **Python 3.7**，[安装指引](./references/install_python37_on_centos.md)

  - **MySQL服务（5.7.8以上的版本）**，[安装指引](./references/install_mysql_on_centos.md)

  - **Redis服务（4.0版本以上）**，[安装指引](./references/install_redis_on_centos.md)

  - **Nginx服务**，可以使用包管理工具进行安装

    - CentOS 系统：`yum install nginx`

    - Ubuntu 系统：`apt-get install nginx`

  :::warning
  仅适用于本地部署体验，生产环境建议使用专业的 MySQL、Redis 等服务
  :::

- 权限准备

  - 安装 Server 依赖软件（python、nginx、yum 等软件包）需要使用 ROOT 权限

    启动 Server服务时可以使用非 ROOT 用户运行
  
  - 需要开放80端口的访问权限(80为TCA平台默认访问端口)，或调整 Web 服务默认的访问端口地址

  - Server 服务执行数据库初始化需要依赖 ``CREATE、ALTER、INDEX、DELETE、LOCK TABLES、SELECT、INSERT、REFERENCES、UPDATE`` 权限

### 部署步骤

#### 部署 Server

1. 进入 Server 服务工作目录（例如 ``~/CodeAnalysis/server/``），以下路径均为目录内的相对路径

2. 配置 MySQL 和 Redis 服务，初始化数据（MySQL版本运行版本：5.7）

    - 填写数据库和Redis信息以及根据需要调整配置信息，主要的工程配置已提供默认值，字段说明详见[TCA Server](../guide/服务端/server.md)。

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

    - 使环境变量生效，避免出现 `unknown command` 错误

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

#### 部署Web

1. 在完成 Server 部署后，进入 Web 服务工作目录（例如 ``~/CodeAnalysis/web/tca-deploy-source``），以下路径均为目录内的相对路径

2. 部署/更新前端服务

    ```bash
    # 部署、更新都使用此命令
    bash ./scripts/deploy.sh init -d

    # 注意
    # 前端 nginx 服务 SERVER_NAME 默认通过 `curl ifconfig.me` 获取
    # 可能是公网出口IP地址，如用户需要自定义 SERVER_NAME，可通过如下方式
    export LOCAL_IP=xxx 
    bash ./scripts/deploy.sh init -d
    ```

:::tip

- `./scripts/config.sh` 已配置默认环境变量，用户可根据需要调整环境变量再部署前端服务，具体可查阅脚本内容。
- TCA 平台初始登录账号是``CodeDog``，密码是``admin``，
:::

## 通过Docker-Compose

### 依赖环境

- 系统环境

  - Linux、macOS、Windows

  - 最低配置：2核4G内存、100G硬盘存储空间

- 环境准备

  - Docker

  - Docker-Compose 1.26 以上版本

  :::warning
  Compose file format需要为3.0及以上，Docker版本要求可以参考[官方文档](https://docs.docker.com/compose/compose-file/compose-file-v3/#compose-and-docker-compatibility-matrix)
  :::

- 权限准备

  - 需要开放80、8000端口的访问权限(80为TCA平台访问端口，8000为TCA Server访问端口)

### 部署步骤

#### 方案一：一键部署（持续完善中）

拉取代码进入源码根目录，执行``./quick_install.sh``命令，即可自动安装 Docker、Docker-Compose 和启动 Server 与 Web 服务

:::tip

- ``quick_install.sh`` 脚本中会自动下载 [Docker 安装脚本](https://get.docker.com) 、启动 Docker 服务、下载 ``docker-compose`` 可执行文件以及执行 ``compose_init.sh`` 脚本启动 Server、Web 服务

- 如果提示脚本没有执行权限，可以在源码目录下执行命令：``chmod +x compose_init.sh quick_install.sh``
:::

#### 方案二：手动部署

1. 安装 Docker，安装教程：[官方文档](https://docs.docker.com/engine/install/)

2. 安装 Docker-Compose，安装教程：[官方文档](https://docs.docker.com/compose/install/)

3. 拉取代码并进入源码根目录后，执行 ``./compose_init.sh`` 命令，即可启动 Server 与 Web 服务

:::tip

- 如果提示脚本没有执行权限，可以在源码执行命令：``chmod +x compose_init.sh``

- 首次启动会构建相关镜像，耗时会比较久

- ``compose_init.sh`` 脚本会包含各个服务的初始化操作

- 需要注意：如果是ARM平台，亲请将`docker-compose.yml`里面的数据库服务从`MySQL`切换到`MariaDB`，源代码里面有注释，注释掉现有`mysql`字段，取消`mariadb`字段注释即可，不然会出现使用`docker-compose up`命令无法启动项目状况。
:::

#### 启动/停止服务

进入源码目录后，执行 ``docker-compose up -d`` 命令，即可启动 Server 与 Web服务。执行 ``docker-compose stop`` 命令，即可停止 Server 与 Web 服务。

### 常见问题

- Q：如何查看服务启动的日志？

  A：可以先找服务名称，执行 ``docker-compose logs -f xxx``，xxx即服务的名称，比如``main-server``、``main-worker``等

- Q：TCA 初始登录账号密码是什么？
  
  A：初始登录账号是``CodeDog``，密码是``admin``，如果想要自定义，在初始化前，可以在``server/dockerconfs/.env.local``对``TCA_DEFAULT_ADMIN``和``TCA_DEFAULT_PASSWORD``变量值进行调整。如果初始化完成后需要调整，则需要登录到平台的``用户管理``页面进行调整。

**详细Q&A文档可以查阅[TCA使用常见问题](./FAQ.md)**
