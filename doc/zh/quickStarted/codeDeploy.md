# 源码部署
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
  $ bash ./quick_install.sh local deploy
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
    - `bash ./quick_install.sh local install tca`：更新相关配置
    - `bash ./quick_install.sh local start`：启动服务（会自动关闭之前的服务）
    - `bash ./quick_install.sh local check`：检查服务是否启动失败

注：
1. `local install`命令行参数说明：
    - `base`：安装Python、Mariadb/MySQL、Redis与Nginx
    - `tca`：初始化或更新TCA Server、Web、Client相关配置和数据
    - `server`：初始化或更新TCA Server相关配置和数据
    - `web`：初始化或更新TCA Web相关配置和数据
    - `client`：初始化或更新TCA Client相关配置和数据
    - 不填参数，默认会执行`base`、`tca`相关操作

#### 启动和停止服务

- 启动所有服务：`bash ./quick_install.sh local start`
- 启动Main相关服务：`bash ./quick_install.sh local start main`
  - `local start`支持启动指定服务，如上述的启动Main服务，还支持`mysql/redis/analysis/file/login/scmproxy/nginx/client/all`
- 停止所有服务：`.bash /quick_install.sh local stop`
- 停止Main相关服务：`bash ./quick_install.sh local stop main`
  - `local stop`支持停止指定服务，如上述的停止Main服务，还支持`analysis/file/login/scmproxy/nginx/client/all`

注：
1. 启动时会自动关闭之前已经运行的服务
2. `local start`支持启动指定服务，如上述的启动Main服务，还支持`mysql/redis/main/analysis/file/login/scmproxy/nginx/all`
  - `mysql`和`redis`默认会使用`systemctl`进行启动，如果`systemctl`无法使用，则会直接使用`nohup`方式运行相关服务

#### 检查服务运行状态
检查服务运行状态：`bash ./quick_install.sh local check`
  - 目前支持检查server与web，暂不支持client

#### 获取服务输出日志
打印TCA Server各个服务的日志路径： `bash ./quick_install.sh local log`