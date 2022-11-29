# 源代码快速部署
TCA提供部署脚本，支持一键式快速部署Server、Web、Client。  
脚本共提供三种部署方式：[Docker部署(平台体验首推)](./dockerDeploy.md)、[Docker-Compose部署](./dockercomposeDeploy.md)、源码部署，
可根据您的具体使用场景任意选择其一进行部署。

#### 依赖环境

- 系统环境
  - Linux
  - 最低配置：2核4G内存、100G硬盘存储空间

- 环境准备

  :::tip
  TCA 一键部署脚本已封装好 Python、Mariadb、Redis 与 Nginx 安装步骤，**无需自行安装**，**本地部署体验**可按 [操作说明](#操作说明) 内容直接进行部署操作。

  **注意：生产环境建议使用专业的 MySQL、Redis 等服务**
  :::
  - Python 3.7

  - MySQL 服务（MySQL5.7.8 以上版本或 Mariadb 10.5 以上版本）

  - Redis 服务（4.0版本以上）

  - Nginx 服务

- 权限准备

  - 环境权限：安装 Server 依赖软件（python、nginx、yum 等软件包）需要使用 ROOT 权限
    - 启动 Server 服务时可以使用非 ROOT 用户运行
  - 数据库权限：Server 服务执行数据库初始化需要依赖 ``CREATE、ALTER、INDEX、DELETE、LOCK TABLES、SELECT、INSERT、REFERENCES、UPDATE`` 权限
- 端口使用：需要开放80端口的访问权限(80为TCA平台默认访问端口)，或调整 Web 服务默认的访问端口地址

#### 操作说明

##### 首次启动操作

1. 进入 CodeAnalysis 工作目录（例如``~/CodeAnalysis``)，以下路径均为目录内的相对路径

2. 安装基础软件与部署 TCA（可根据脚本选项确定是否要安装 Python、MySQL、Redis、Nginx 相关基础软件），执行
  ```bash
  $ bash ./quick_install.sh local deploy
  ```

  执行该命令会做以下四个步骤：
  - `Install`：检测本地 Python3.7、Mariadb/MySQL、Redis 与 Nginx，如果不存在会提示安装
  - `Init`：部署 TCA Server、Web与Client，并进行初始化
  - `Start`：启动 TCA Server、Web与Client
  - `Check`：检测 TCA 的运行状态
   
  **注意**：在运行过程中，脚本会检测本地是否安装了相关基础软件（Python3.7、MySQL/Mariadb、Redis、Nignx），如果未安装会输出以下类似提示语：
  ```bash
  Do you want to install [Redis] by this script?
  Please enter:[Y/N]
  ```
  如果确定通过脚本安装可以输入`Y`。


3. 执行完成，无其他报错，即可登录：

:::tip
至此，您已完成 TCA 平台部署，请在浏览器输入`http://部署机器IP/`，点击立即体验，完成登录后即可开启您的腾讯云代码分析。  
平台内操作指引请查看：[快速启动一次代码分析](../guide/快速入门/快速启动一次代码分析.md)

默认平台登录账号/密码：CodeDog/admin

如部署过程中，已调整默认账号密码，请按照调整后的账号密码进行登录
:::


##### 更新操作
**1. 更新代码**

**2. 执行以下命令**
```bash
bash ./quick_install.sh local install tca  #更新相关配置
bash ./quick_install.sh local start  #启动服务（会自动关闭之前的服务）
bash ./quick_install.sh local check  #检查服务是否启动失败
```
**注意：**  
 `local install`命令行参数说明：    
    - `base`：安装 Python、Mariadb/MySQL、Redis 与 Nginx  
    - `tca`：初始化或更新 TCA Server、Web、Client 相关配置和数据  
    - `server`：初始化或更新 TCA Server 相关配置和数据  
    - `web`：初始化或更新 TCA Web 相关配置和数据  
    - `client`：初始化或更新 TCA Client 相关配置和数据  
    - 不填参数，默认会执行`base`、`tca`相关操作  

##### 启动和停止服务

- 启动所有服务：`bash ./quick_install.sh local start`

- 启动Main相关服务：`bash ./quick_install.sh local start main`
  - `local start`支持启动指定服务，如上述的启动Main服务，还支持`mysql/redis/analysis/file/login/scmproxy/nginx/client/all`

- 停止所有服务：`bash ./quick_install.sh local stop`

- 停止Main相关服务：`bash ./quick_install.sh local stop main`
  - `local stop`支持停止指定服务，如上述的停止Main服务，还支持`analysis/file/login/scmproxy/nginx/client/all`

**注意：**  
1. 启动时会自动关闭之前已经运行的服务

2. `mysql`和`redis`默认会使用`systemctl`进行启动，如果`systemctl`无法使用，则会直接使用`nohup`方式运行相关服务

##### 检查服务运行状态
检查服务运行状态：`bash ./quick_install.sh local check`
  - 目前支持检查 server 与 web，暂不支持 client

##### 获取服务输出日志
打印 TCA Server 各个服务的日志路径： `bash ./quick_install.sh local log`

