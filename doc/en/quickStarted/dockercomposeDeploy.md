# Docker-Compose快速部署
TCA提供部署脚本，支持一键式快速部署 Server、Web、Client。  
脚本共提供三种部署方式：[Docker部署(平台体验首推)](./dockerDeploy.md)、Docker-Compose部署、[源码部署](./codeDeploy.md)，
可根据您的具体使用场景任意选择其一进行部署。

#### 部署对象
Server、Web 与 Client

:::warning
仅适用于 Docker-Compose 部署体验，生产环境建议使用专业的 MySQL、Redis 等服务
:::

#### 操作说明
##### 首次启动操作

1. 进入 CodeAnalysis 工作目录（例如``~/CodeAnalysis``)，以下路径均为目录内的相对路径

2. 执行命令：
``` bash
bash ./quick_install.sh docker-compose deploy #启动tca_server容器
```
注意：通过 Docker-Compose 部署默认会在当前根目录下的挂载三个路径：

- `.docker_data/logs`：存放 TCA 平台的各个服务日志输出目录；
- `.docker_data/mysql`：存放 TCA 平台的 MySQL 数据
- `.docker_data/redis`：存放 TCA 平台的 Redis 数据
- `.docker_data/filedata`：存放 TCA 平台文件服务器的文件


:::tip
完成 TCA 平台部署后，请在浏览器输入`http://部署机器IP/`，点击立即体验，完成登录后即可开启您的腾讯云代码分析。  
平台内操作指引请查看：[快速启动一次代码分析](../guide/快速入门/快速启动一次代码分析.md)

默认平台登录账号/密码：CodeDog/admin

如部署过程中，已调整默认账号密码，请按照调整后的账号密码进行登录
:::

##### 更新操作
1. 更新代码

2. 执行以下命令：

``` bash
bash ./quick_install.sh docker-compose build  #重新构建TCA相关镜像
bash ./quick_install.sh docker-compose stop  #停止运行中的TCA容器
bash ./quick_install.sh docker-compose deploy  #重新部署TCA相关容器与初始化（或刷新数据）
```
##### 运行操作
如果已经在机器上执行过``docker-compose deploy``，并保留容器数据的，可以执行以下命令启动容器，继续运行 TCA

```bash
bash ./quick_install.sh docker-compose start
```

##### 停止操作
如果容器正在运行，希望停止容器，可以执行以下命令

```bash
bash ./quick_install.sh docker-compose stop
```

##### 构建镜像操作
如果希望构建镜像，可以执行以下命令

```bash
bash ./quick_install.sh docker-compose build
```