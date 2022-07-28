# Docker-Compose快速部署
#### 部署对象
Server、Web 与 Client

:::warning
仅适用于Docker-Compose部署体验，生产环境建议使用专业的 MySQL、Redis 等服务
兼容之前的部署方式
:::

#### 操作说明
##### 首次启动操作

1. 进入CodeAnalysis工作目录（例如``~/CodeAnalysis``)，以下路径均为目录内的相对路径
2. 执行命令：
    - `bash ./quick_install.sh docker-compose deploy`：启动tca_server容器

注意：通过Docker-Compose部署默认会在当前根目录下的挂载三个路径：

- `.docker_data/logs`：存放TCA平台的各个服务日志输出目录；
- `.docker_data/mysql`：存放TCA平台的MySQL数据
- `.docker_data/redis`：存放TCA平台的Redis数据
- `.docker_data/filedata`：存放TCA平台文件服务器的文件

##### 更新操作
1. 更新代码
2. 执行以下命令：
    - `bash ./quick_install.sh docker-compose build`：重新构建TCA相关镜像
    - `bash ./quick_install.sh docker-compose deploy`: 重新部署TCA相关容器与初始化（或刷新数据）

##### 运行操作
如果已经在机器上执行过``docker-compose deploy``，并保留容器数据的，可以执行以下命令启动容器，继续运行TCA

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

```
bash ./quick_install.sh docker-compose build
```