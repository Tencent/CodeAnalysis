# 部署 Server 和 Web

## 本地快速部署
兼容旧版的部署方式
### 依赖环境

- 系统环境
  - Linux
  - 最低配置：2核4G内存、100G硬盘存储空间

- 环境准备
> 目前TCA脚本已封装好Python、Mariadb、Redis与Nginx安装步骤，可以按“部署步骤”文档进行操作

  - **Python 3.7**，[安装指引](./references/install_python37_on_centos.md)

  - **MySQL服务（MySQL5.7.8以上版本或Mariadb 10.5以上版本）**，[安装指引](./references/install_mysql_on_centos.md)

  - **Redis服务（4.0版本以上）**，[安装指引](./references/install_redis_on_centos.md)

  - **Nginx服务**

  :::warning
  仅适用于本地部署体验，生产环境建议使用专业的 MySQL、Redis 等服务
  :::

- 权限准备

  - 环境权限：安装 Server 依赖软件（python、nginx、yum 等软件包）需要使用 ROOT 权限
    - 启动 Server服务时可以使用非 ROOT 用户运行
  - 数据库权限：Server 服务执行数据库初始化需要依赖 ``CREATE、ALTER、INDEX、DELETE、LOCK TABLES、SELECT、INSERT、REFERENCES、UPDATE`` 权限
- 端口使用：需要开放80端口的访问权限(80为TCA平台默认访问端口)，或调整 Web 服务默认的访问端口地址

### 操作说明

#### 首次启动操作

1. 进入CodeAnalysis工作目录（例如``~/CodeAnalysis``)，以下路径均为目录内的相对路径
2. 安装基础软件与部署TCA（可根据脚本选项确定是否要安装相关基础软件），执行
  ```bash
  $ ./quick_install.sh local deploy
  ```
  执行该命令会做以下事情：
  - 检测本地Python3.7、Mariadb/MySQL、Redis与Nginx，如果不存在会提示安装（install）
  - 部署TCA Server、Web与Client，并进行初始化（install）
  - 启动TCA Server、Web与Client（start）
  - 检测TCA的运行状态（check）
   
  >注：在运行过程中，脚本会检测本地是否安装了相关基础软件（Python3.7、MySQL/Mariadb、Redis、Nignx），如果未安装会输出以下类似提示语：
  >```
  >Do you want to install [Redis] by this script?
  >Please enter:[Y/N]
  >```
  >如果确定通过脚本安装可以输入`Y`。
3. 执行完成，无其他报错，即可登录：
    - TCA 平台初始登录账号是``CodeDog``，密码是``admin``，

#### 更新操作
1. 更新代码
2. 执行以下命令：
    - `./quick_install.sh local install tca`：更新相关配置
    - `./quick_install.sh local start`：启动服务（会自动关闭之前的服务）
    - `./quick_install.sh local check`：检查服务是否启动失败

注：
1. `local install`命令行参数说明：
    - `base`：安装Python、Mariadb/MySQL、Redis与Nginx
    - `tca`：初始化或更新TCA Server、Web、Client相关配置和数据
    - `server`：初始化或更新TCA Server相关配置和数据
    - `web`：初始化或更新TCA Web相关配置和数据
    - `client`：初始化或更新TCA Client相关配置和数据
    - 不填参数，默认会执行`base`、`tca`相关操作

#### 启动和停止服务

- 启动所有服务：`./quick_install.sh local start`
- 启动Main相关服务：`./quick_install.sh local start main`
  - `local start`支持启动指定服务，如上述的启动Main服务，还支持`mysql/redis/analysis/file/login/scmproxy/nginx/client/all`
- 停止所有服务：`./quick_install.sh local stop`
- 停止Main相关服务：`./quick_install.sh local stop main`
  - `local stop`支持停止指定服务，如上述的停止Main服务，还支持`analysis/file/login/scmproxy/nginx/client/all`

注：
1. 启动时会自动关闭之前已经运行的服务
2. `local start`支持启动指定服务，如上述的启动Main服务，还支持`mysql/redis/main/analysis/file/login/scmproxy/nginx/all`
  - `mysql`和`redis`默认会使用`systemctl`进行启动，如果`systemctl`无法使用，则会直接使用`nohup`方式运行相关服务

#### 检查服务运行状态
检查服务运行状态：`./quick_install.sh local check`
  - 目前支持检查server与web，暂不支持client

#### 获取服务输出日志
打印TCA Server各个服务的日志路径： `./quick_install.sh local log`

## Docker快速部署

:::warning
仅适用于Docker部署体验，生产环境建议使用专业的 MySQL、Redis 等服务
:::

### 依赖环境

- 系统环境
  - Linux、macOS、Windows
  - 最低配置：2核4G内存、100G硬盘存储空间
- 环境准备
  - Docker
- 权限准备
  - 需要开放80、8000端口的访问权限(80为TCA平台访问端口，8000为TCA Server访问端口)

### 部署对象
Server、Web 与 Client

### 操作说明
#### 首次启动操作

1. 进入CodeAnalysis工作目录（例如``~/CodeAnalysis``)，以下路径均为目录内的相对路径
2. 执行命令：
    ```bash
    ./quick_install.sh docker deploy
    ```

注：通过Docker部署默认会在当前根目录下的挂载三个路径：

- `.docker_temp/logs`：容器内的`/var/log/tca/`，存放TCA平台的日输出文件；
- `.docker_temp/data`：容器内的`/var/opt/tca/`, 存放TCA平台的服务数据，主要是Mariadb、Redis；
- `.docker_temp/configs`：容器内的``/etc/tca``，存放TCA平台的配置文件，主要是`config.sh`

#### 更新操作
1. 更新代码
2. 执行以下命令：
    - `TCA_IMAGE_BUILD=true ./quick_install.sh docker deploy`：重新构建并启动tca容器

注：`TCA_IMAGE_BUILD=true`表示从本地构建TCA镜像运行

#### 运行容器
如果已经在机器上执行过``docker deploy``，并保留容器数据的，可以执行以下命令启动容器，继续运行TCA

```bash
./quick_install.sh docker start
```

#### 停止容器
如果容器正在运行，希望停止容器，可以运行

```bash
./quick_install.sh docker stop
```

## Docker-Compose快速部署
### 部署对象
Server、Web 与 Client

:::warning
仅适用于Docker-Compose部署体验，生产环境建议使用专业的 MySQL、Redis 等服务
兼容之前的部署方式
:::

### 操作说明
#### 首次启动操作

1. 进入CodeAnalysis工作目录（例如``~/CodeAnalysis``)，以下路径均为目录内的相对路径
2. 执行命令：
    - `./quick_install.sh docker-compose deploy`：启动tca_server容器

注意：通过Docker-Compose部署默认会在当前根目录下的挂载三个路径：

- `.docker_data/logs`：存放TCA平台的各个服务日志输出目录；
- `.docker_data/mysql`：存放TCA平台的MySQL数据
- `.docker_data/redis`：存放TCA平台的Redis数据
- `.docker_data/filedata`：存放TCA平台文件服务器的文件

#### 更新操作
1. 更新代码
2. 执行以下命令：
    - `./quick_install.sh docker-compose build`：重新构建TCA相关镜像
    - `./quick_install.sh docker-compose deploy`: 重新部署TCA相关容器与初始化（或刷新数据）

#### 运行操作
如果已经在机器上执行过``docker-compose deploy``，并保留容器数据的，可以执行以下命令启动容器，继续运行TCA

```bash
./quick_install.sh docker-compose start
```

#### 停止操作
如果容器正在运行，希望停止容器，可以执行以下命令

```bash
./quick_install.sh docker-compose stop
```

#### 构建镜像操作
如果希望构建镜像，可以执行以下命令

```
./quick_install.sh docker-compose build
```

### 旧部署方式
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

- 需要注意：如果是ARM平台，请将`docker-compose.yml`里面的数据库服务从`MySQL`切换到`MariaDB`，源代码里面有注释，注释掉现有`mysql`字段，取消`mariadb`字段注释即可，不然会出现使用`docker-compose up`命令无法启动项目状况。
:::

#### 启动/停止服务

进入源码目录后，执行 ``docker-compose up -d`` 命令，即可启动 Server 与 Web服务。执行 ``docker-compose stop`` 命令，即可停止 Server 与 Web 服务。

### 常见问题

- Q：如何查看服务启动的日志？

  A：可以先找服务名称，执行 ``docker-compose logs -f xxx``，xxx即服务的名称，比如``main-server``、``main-worker``等

- Q：TCA 初始登录账号密码是什么？
  
  A：初始登录账号是``CodeDog``，密码是``admin``，如果想要自定义，在初始化前，可以在``server/dockerconfs/.env.local``对``TCA_DEFAULT_ADMIN``和``TCA_DEFAULT_PASSWORD``变量值进行调整。如果初始化完成后需要调整，则需要登录到平台的``用户管理``页面进行调整。

**详细Q&A文档可以查阅[TCA使用常见问题](./FAQ.md)**
