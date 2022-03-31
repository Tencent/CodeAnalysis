# Server与Web本地部署文档

## 前期部署准备

### 系统配置

运行环境：

- Linux
- Linux/Mac/Window上的Docker

最低配置要求：
2核4G内存100G硬盘存储空间

### 服务部署顺序

1. Server服务
2. Web服务

### 服务部署权限说明

#### Linux角色权限

1. 安装Server依赖软件（python、nginx、yum软件包）需要使用ROOT权限
2. 启动Server服务时可以使用非ROOT用户运行

#### 网络权限服务部署

1. 需要开放80端口的访问权限(80为TCA平台访问端口)

#### 数据库权限

1. Server服务执行数据库初始化需要依赖``CREATE、ALTER、INDEX、DELETE、LOCK TABLES、SELECT、INSERT、REFERENCES、UPDATE``权限

## 服务部署

### Server部署

#### 前置环境

1. MySQL服务（5.7.8以上的版本），安装指导: [文档](./references/install_mysql_on_centos.md)（仅适用于本地部署体验），生产环境建议使用专业的MySQL服务
2. Redis服务（4.0版本以上），安装指导: [文档](./references/install_redis_on_centos.md)（仅适用于本地部署体验），生产环境建议使用专业的Redis服务
3. Python3.7执行环境，安装指导: [文档](./references/install_python37_on_centos.md)
4. Nginx服务（可以使用包管理工具进行安装，比如CentOS系统执行``yum install nginx``，Ubuntu系统执行``apt-get install nginx``）

#### 部署步骤

1. 进入Server服务工作目录后（假设工作目录为 ``/data/CodeAnalysis/server/``，以下路径均为工作目录内的相对路径）
2. 配置MySQL和Redis服务，初始化数据（MySQL版本运行版本：5.7）
    - 执行``vi ./scripts/config.sh``：填写数据库和Redis信息以及根据需要调整配置信息，主要的工程配置已提供默认值，字段说明可以查看[文档](../server/README.md)
    - 执行``./scripts/deploy.sh init``：初始化DB、安装依赖和运行初始化脚本
    - 将安装好的``celery``与``gunicorn``可执行文件建立软链到``/usr/local/bin``路径下
        - ``ln -s /path/to/celery /usr/local/bin/celery``：``/path/to/``需要替换为``celery``可执行命令实际的路径，一般在python安装路径的``bin``目录下
        - ``ln -s /path/to/gunicorn /usr/local/bin/gunicorn``：``/path/to/``需要替换为实际的路径
        - 如果您按Python3.7安装指导，这里的/path/to/路径为/usr/local/python3/bin/celery
    - 执行``export PATH=/usr/local/bin:$PATH``环境变量生效避免出现unknown command错误
3. 启动服务
    - 执行``./scripts/deploy.sh start``：启动服务
4. 停止服务
    - 执行``./scripts/deploy.sh stop``：停止服务

### Web 部署

#### 前置部署

1. Linux 环境

2. 系统已安装 nginx

3. TCA Server 服务已部署完毕，具备后端服务地址，默认登陆账号/密码：`CodeDog/admin`

#### Web 部署步骤

1. **进入前端部署源码目录**
  
    进入web服务目录，并切换至`tca-deploy-source`目录，将其视为工作目录（假设工作目录为 `/data/CodeAnalysis/web/tca-deploy-source`）

2. **部署/更新前端服务**

    ```bash
    # 部署、更新都使用此命令
    sh ./scripts/deploy.sh init -d
    ```

    具体请查阅部署脚本内容，可根据业务调整配置。

3. **额外说明**

    `tca-deploy-source/scripts/config.sh` 已配置默认环境变量，用户可根据需要调整环境变量再部署前端服务，具体可查阅脚本内容。

**详细Q&A文档可以查阅[TCA使用常见问题](https://github.com/Tencent/CodeAnalysis/blob/main/doc/Q%26A.md)**
