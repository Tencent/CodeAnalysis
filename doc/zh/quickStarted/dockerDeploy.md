# Docker快速部署（平台体验首推）

:::warning
Docker部署会包含Mariadb和Redis，如果需要更大规模使用，可以调整配置文件使用运维规范的 MySQL/Mariadb 和 Redis。  

:::

#### 依赖环境

- 系统环境
  - Linux、macOS、Windows
  - 最低配置：2核4G内存、100G硬盘存储空间
- 环境准备
  - Docker
- 权限准备
  - 需要开放80、8000端口的访问权限(80为TCA平台访问端口，8000为TCA Server访问端口)

#### 部署对象
Server、Web 与 Client

#### 操作说明
##### 首次启动操作

1. 进入CodeAnalysis工作目录（例如``~/CodeAnalysis``)，以下路径均为目录内的相对路径
2. 执行命令：
    ```bash
    bash ./quick_install.sh docker deploy
    ```
::: tip
1. 通过Docker部署默认会从DockerHub上拉取``tencenttca/tca:latest``镜像
2. 通过Docker部署默认会在当前根目录下的挂载三个路径：
   - `.docker_temp/logs`：容器内的`/var/log/tca/`，存放TCA平台的日输出文件；
   - `.docker_temp/data`：容器内的`/var/opt/tca/`， 存放TCA平台的服务数据，主要是Mariadb、Redis；
   - `.docker_temp/configs`：容器内的``/etc/tca``，存放TCA平台的配置文件，主要是`config.sh`
:::

##### 更新操作
1. 更新代码
2. 执行以下命令：
```bash
TCA_IMAGE_BUILD=true ./quick_install.sh docker deploy  #重新构建并启动tca容器
```
::: tip
`TCA_IMAGE_BUILD=true`表示从本地构建TCA镜像运行
:::



##### 运行容器
如果已经在机器上执行过`docker deploy`，并保留容器数据的，可以执行以下命令启动容器，继续运行TCA

```bash
bash ./quick_install.sh docker start
```

##### 停止容器
如果容器正在运行，希望停止容器，可以运行

```bash
bash ./quick_install.sh docker stop
```

#### 使用TCA
至此，您已完成第一个TCA平台部署，请在浏览器输入`http://部署机器IP/`，点击立即体验，完成登录后即可开启您的腾讯云代码分析。  
平台内操作指引请查看：[快速启动一次代码分析](../guide/快速入门/快速启动一次代码分析.md)
:::tip
默认平台登录账号/密码：CodeDog/admin

如部署过程中，已调整默认账号密码，请按照调整后的账号密码进行登录
:::
