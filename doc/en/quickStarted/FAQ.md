# FAQ

:::tip
该Q&A文档会持续更新，非常欢迎您的建议与共建！

如果您遇到任何未在此处列出的部署或使用问题，请在 GitHub issue 系统中进行搜索。如果仍未找到该错误消息，您可以通过[社区](../community/joingroup.md)提出问题，获得帮助。
:::

[[toc]]

## Server常见问题与处理方法

### 1. 环境部署

#### 1.1 pypi下载超时或失败

如果在执行``pip install``环节出现以下错误，可以调整一下镜像源：

```bash
WARNING: Retrying (Retry(total=4, connect=None, read=None, redirect=None, status=None)) after connection broken by 'ReadTimeoutError("HTTPSConnectionPool(host='files.pythonhosted. org', port=443): Read timed out.(read timeout=15)") '
```

该错误是访问官方``pypi``下载源时网络不通或者不稳定导致，可以通过以下方式调整：

本地部署时，调整``pypi``下载源配置方式：

```bash
mkdir ~/.pip/
echo "[global]\nindex-url = https://mirrors.cloud.tencent.com/pypi/simple" >> ~/.pip/pip.conf
```

Docker-Compose部署时，调整``pypi``下载源配置方式：

```bash
vi server/dockerconfs/Dockerfile-common
```

调整文件中最后一行 ``RUN``指令

```bash
RUN mkdir -p log/ && \
    mkdir ~/.pip/ && \
    echo "[global]\nindex-url = https://mirrors.cloud.tencent.com/pypi/simple" >> ~/.pip/pip.conf && \
    pip install -U setuptools pip && \
    pip install -r requirements.txt
```

注：如果需要指定其他``pypi``下载源，可以将``https://mirrors.cloud.tencent.com/pypi/simple``进行替换

如果出现以下错误：

```bash
WARNING: Retrying (Retry(total=4, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<pip._vendor.urllib3.connection.HTTPSConnection object at 0x7f6d4ac24910>: Failed to establish a new connection: [Errno -3] Temporary failure in name resolution')': /simple/setuptools/
```

该错误是无法正常解析``pypi``访问域名，需要检查一下本地的dns配置是否正常

#### 1.2 Docker未安装或版本过低

TCA Server使用Docker-Compose依赖的Docker版本需要是``1.13.0``及以上，可以执行以下命令查看Docker版本

```bash
$ docker --version
Docker version 18.09.7, build 2d0083d
```

文档相关：

- [Compose文件版本与对应的Docker版本说明文档](https://docs.docker.com/compose/compose-file/compose-versioning/)
- [CentOS安装Docker官方文档](https://docs.docker.com/engine/install/centos/)
- [Ubuntu安装Docker文档](https://docs.docker.com/engine/install/ubuntu/)

#### 1.3 Docker-Compose启动失败

如果启动Docker-Compose输出以下错误：

```bash
* Error response from daemon: Error processing tar file(exit status 1): unexpected EOF
* Error response from daemon: Error processing tar file(exit status 1): unexpected EOF
* Error response from daemon: Error processing tar file(exit status 1): unexpected EOF
```

问题原因：可能镜像构建目录权限不足，导致异常。
解决方案：

1. 执行``docker-compose build``可以通过日志查看是哪个镜像构建异常
2. 切换到具体目录执行``docker build .``可以看到详细错误信息，结合具体错误信息进行处理
3. 收集常见的错误日志，整理相关解决方案(注：欢迎大家补充)

文档相关：

- [Docker-Compose官方安装文档](https://docs.docker.com/compose/install/)
- [Docker-ComposeV2官方安装文档](https://docs.docker.com/compose/cli-command/)

#### 1.4 Docker镜像源下载超时或失败

目前TCA基础镜像是使用``python:3.7.12-slim``，该镜像是基于``debian bullseye(debian 11)``版本构建的，对应的源需要选择 ``bullseye`` 版本的源。

如果使用默认的下载源会报错或访问速度比较慢，可以调整``server/dockerconfs/Dockerfile-common``，指定其他国内下载源：

```DockerFile
# FROM python:3.7.12-slim

# 增加一下内容用于指定下载源
RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak && \
    echo 'deb http://mirrors.tencent.com/debian/ bullseye main non-free contrib' > /etc/apt/sources.list && \
    echo 'deb http://mirrors.tencent.com/debian/ bullseye-updates main non-free contrib' >> /etc/apt/sources.list && \
    echo 'deb http://mirrors.tencent.com/debian-security bullseye-security main non-free contrib' >> /etc/apt/sources.list

# ARG EXTRA_TOOLS=...
```

如果出现以下错误：``E: Error, pkgProblemResolver::Resolve generated breaks, this may be caused by held packages``
可以做以下检查，确认是什么原因：

1. 检查一下本地服务器的时间配置是否正常
2. 调整下载源

#### 1.5 Python安装或执行失败

使用Python执行时提示``ImportError: libpython3.7m.so.1.0: cannot open shared object file: No such file or directory``，该如何处理

1. 在本地安装Python的目录中查找该文件，比如Python的安装目录是``/usr/local/python3``，可以执行``find /usr/local/python3 -name "libpython3.7m.so.1.0"``，确认本地是否存在该文件
2. 如果本地存在该文件，则执行以下命令：（注：需要将``/usr/local/python3``调整为本地实际的Python3安装路径）

    ```bash
    # 链接构建产出的Python动态库
    $ ln -s /usr/local/python3/lib/libpython3.7m.so.1.0 /usr/lib/libpython3.7m.so.1.0
    # 配置动态库
    $ ldconfig
    ```

3. 如果本地不存在该文件，则可能需要重新安装Python3：（注：以下是将Python安装到``/usr/local/python3``，可以根据实际情况进行调整）

    ```bash
    # 编译前配置，注意重点：需要加上参数 --enable-shared
    $ ./configure prefix=/usr/local/python3 --enable-shared
    ```

文档相关：

- [CentOS安装Python3.7文档](https://github.com/Tencent/CodeAnalysis/blob/main/doc/references/install_python37_on_centos.md)
- [Ubuntu安装Python3.7文档](https://github.com/Tencent/CodeAnalysis/blob/main/doc/references/install_python37_on_ubuntu.md)

#### 1.6 执行``compose_init.sh``脚本的``pip install``提示``sha256``不匹配错误

在构建镜像的``pip install``步骤提示以下报错时：

```
ERROR: THESE PACKAGES DO NOT MATCH THE HASHES FROM THE REQUIREMENTS FILE. If you have updated the package versions, please update the hashes. Otherwise, examine the package contents carefully; someone may have tampered with them.
    setuptools from https://mirrors.cloud.tencent.com/pypi/packages/fb/58/9efbfe68482dab9557c49d433a60fff9efd7ed8835f829eba8297c2c124a/setuptools-62.1.0-py3-none-any.whl#sha256=26ead7d1f93efc0f8c804d9fafafbe4a44b179580a7105754b245155f9af05a8:
        Expected sha256 26ead7d1f93efc0f8c804d9fafafbe4a44b179580a7105754b245155f9af05a8
             Got        ddaacc49de5c08c09d744573240a9a49f24f65c5c72380e972433784caa68d98
```

可以执行``export ORIGIN=normal``，然后再执行``./compose_init.sh``
>注：执行``export``命令的作用是调整为``pypi``默认官方下载源进行``pip install``

#### 1.7 MacBook M1 使用 Docker-Compose报错

在M1机器上使用默认配置启动docker-compose，会出现``mysql``和``scmproxy``服务启动失败，需要做以下两步调整

1. 调整``docker-compose.yml``文件，修改MySQL的镜像版本：

    ```bash
    # 默认：
    image: mysql:5.7.24

    # 调整后：
    image: mariadb:10.5.8
    ```

2. 调整``server/dockerconfs/Dockerfile-common``文件，修改Python的镜像版本：

    ```bash
    # 默认：
    FROM python:3.7.12-slim

    # 调整后：
    FROM amd64/python:3.7.12-slim
    ```

#### 1.8 celery、gunicorn命令找不到

如果启动服务时，提示：``celery could not be found``或``gunicorn could not be found``，需要做以下检查

1. 执行``python -v``检查输出，确认当前python版本是否为python3.7
2. 执行``pip install celery``和``pip install gunicorn``检查celery和gunicorn是否已经安装
3. 如果已经安装，可以执行以下命令建立软链：（注：需要将``/usr/local/python3``调整为本地实际的Python3安装路径）

```bash
ln -s /usr/local/python3/bin/gunicorn /usr/local/bin/gunicorn
ln -s /usr/local/python3/bin/celery /usr/local/bin/celery
```

### 2. 服务启动与初始化

#### 2.1 服务占用端口异常

TCA 本地部署启动后，会监听多个端口：

- web服务：80
- nginx服务：8000
- main服务：8001
- analysis服务：8002
- login服务：8003
- file-nginx服务：8004
- file服务：8804
- scmproxy服务：8009

如果出现端口占用冲突，建议采用以下方式解决：

1. 调整其他程序监听的端口号，避免跟上述TCA服务的端口号出现冲突
2. 采用Docker-Compose方式启动TCA，仅监听80端口

不推荐调整TCA指定服务的端口号，需要调整多处配置，以及可能会影响到后续服务的升级

#### 2.2 服务输出日志找不到

本地部署输出的日志位置：

1. ``main``服务输出的日志目录：``server/projects/main/log``
    - 服务启动日志：``server/projects/main/log/gunicorn_error.log``
    - 服务接收请求日志：``server/projects/main/log/gunicorn_access.log``
    - Celery Worker启动日志（处理异步任务）：``server/projects/main/nohup_worker.out``
    - Celery Beat启动日志（启动定时任务）：``server/projects/main/nohup_beat.out``
    - 服务运行日志：``server/projects/main/log/codedog.log``
    - Celery Worker运行日志：``server/projects/main/log/main_celery.log``
    - Celery Beat运行日志：``server/projects/main/log/main_beat.log``
2. ``analysis``服务输出的日志目录：``server/projects/analysis/log``
    - 服务启动日志：``server/projects/analysis/log/gunicorn_error.log``
    - Celery Worker启动日志：``server/projects/analysis/nohup.out``
    - 服务接收请求日志：``server/projects/analysis/log/gunicorn_access.log``
    - 服务运行日志：``server/projects/analysis/log/codedog.log``
    - Celery Worker运行日志（处理结果入库）：``server/projects/analysis/log/celery.log``
3. ``login``服务输出的日志目录：``server/projects/login/log``
    - 服务启动日志：``server/projects/login/log/gunicorn_error.log``
    - 服务接收请求日志：``server/projects/login/log/gunicorn_access.log``
    - 服务运行日志：``server/projects/login/log/codedog.log``
4. ``file``服务输出的日志目录：``server/projects/file/log``
    - 服务启动日志：``server/projects/file/log/gunicorn_error.log``
    - 服务接收请求日志：``server/projects/file/log/gunicorn_access.log``
    - 服务运行日志：``server/projects/file/log/codedog_file.log``
5. ``scmproxy``服务输出的日志目录：``server/projects/scmproxy/logs``
    - 服务启动日志：``server/projects/scmproxy/nohup.out``
    - 服务运行日志：``server/projects/scmproxy/logs/scmproxy.log``

### 3. 平台使用

#### 3.1 平台登录的默认账号密码是什么？

默认账号: ``CodeDog``，密码: ``admin``

#### 3.2 平台默认的API Token是什么？

默认Token是``0712b895f30c5e958ec71a7c22e1b1a2ad1d5c6b``

如果在平台上刷新了``CodeDog``用户的Token，需要将刷新后的Token填写到以下文件中：

1. ``server/scripts/config.sh``文件
    - 更新``CODEDOG_TOKEN``、``FILE_SERVER_TOKEN``变量的值（3个位置）
2. ``server/dockerconfs/.env.local``文件
    - 更新``CODEDOG_TOKEN``、``FILE_SERVER_TOKEN``变量的值（3个位置）

然后重启服务。

1. 本地部署：

    ```bash
    cd server/
    ./scripts/deploy.sh start
    ```

2. docker-compose部署：

    ```bash
    $ docker-compose stop
    # 稍等片刻
    $ docker-compose up -d
    ```

#### 3.3 代码库登记出错，出现代码库及账号不匹配

该错误出现可能有以下几个原因：

1. 账号密码不准确或登记的代码库地址不存在
2. 登记``github``使用的密码需要使用[``personal access token``](https://github.com/settings/tokens)
3. scmproxy服务启动失败
    - 本地部署：执行``ps aux | grep proxyserver``看看是否有``python proxyserver.py``执行进程，如果不存在可以看一下``server/projects/scmproxy/nohup.out``看看启动失败的原因
    - docker-compose部署：在项目根目录执行``docker-compose ps``看看``scmproxy``容器是否正常启动，如果没有启动，可以执行``docker-compose logs scmproxy``看看启动失败的原因
4. scmproxy所在的机器/容器因为网络问题无法访问对应的代码库
    - 可以手动在机器/容器中执行``git clone xxxx``（xxx表示待登记的代码库），检查看看是否能够正常拉取
5. scmproxy所在的机器git版本较低，出现``unknown option `local` ``错误
    - 可以升级机器上的git版本，目前工具支持最低的git版本为``1.8.3.1``

#### 3.4 查看问题文件提示**获取代码信息耗时较久，请稍后再试**

出现该提示的原因是，代码库偏大或``clone``代码库时间较长，可以稍等一会再刷新重试

#### 3.5 客户端访问文件服务器，提示``method(upload_file) call fails on error: Expecting value: line 1 column 1 (char 0)``

出现这种错误，可能是本地配置异常或token配置有问题，检查方式如下：

1. 检查客户端的``config.ini``文件配置的URL是否为当前Server部署的地址：（xxx需要调整为实际的路径）

    ```bash
    [SERVER_URL]
    URL=http://xxx/server/main/
    [FILE_SERVER]
    URL=http:/xxx/server/files/
    ```

    如果xxx不一致需要调整为一致
    > 注: xxx地址与在浏览器访问平台的xxx地址是一致的，不需要区分端口
2. 检查客户端访问Server是否能通：

    ```bash
    curl -v http://xxx/server/main/
    ```

    如果不通，则需要检查客户端机器访问Server机器是否有网络限制
3. 检查当前在``codedog.ini``-``[config]token``与``config.ini``文件配置的``[FILE_SERVER]TOKEN``是否一致，如果不一致需要调整为一致
4. 检查用户``CodeDog``的``Token``是否被刷新了然后没有更新到配置文件中

#### 3.6 客户端访问文件服务器，提示``Connection timed out``

本地客户端执行过程提示``method (upload file) call fails on error: <urlopen error [Errno 110] Connection timed out>`` 该如何处理？
一般情况下，这个问题是客户端与Server之间网络不通导致，可以检查一下是否有防火墙限制或者配置的URL是内部IP或地址，可以通过以下方式检查

1. 检查客户端的``config.ini``文件配置的URL是否为当前Server部署的地址：（xxx需要调整为实际的路径）

    ```bash
    [SERVER_URL]
    URL=http://xxx/server/main/
    [FILE_SERVER]
    URL=http:/xxx/server/files/
    ```

2. 检查客户端访问Server是否能通：

    ```bash
    curl -v http://xxx/server/main/
    ```

    如果不通，则需要检查客户端机器访问Server机器是否有网络限制

#### 3.7 任务执行结果异常，提示**第三方依赖文件服务器异常**

出现该错误提示，一般是访问文件器出错或文件服务器本身有问题，可以通过以下方式检查：
需要检查``analysis-worker``的日志（本地部署：``server/projects/analysis/log/celery.log``，docker-compose部署：``docker-compose exec analysis-worker /bin/bash``进入容器后访问``log/celery.log``查看具体错误原因

如果提示``no route to host``可能是当前机器/容器无法访问当前宿主机的IP，可以检查一下当前防火墙的设置，是否限制了``analysis-worker``来源的访问

#### 3.8 客户端执行时提示**工具(xxx)扫描进程为空，请联系管理员配置工具进程!**

出现该错误提示，一般是Server未进行初始化，可以通过执行以下命令初始化后再启动测试

- 本地部署：``cd server && ./scripts/deploy.sh init``
- docker-compose部署：``./compose_init.sh``

## CodeAnalysis仓库文件问题

### 1. clone到本地时相关md文件内资源图片无法显示

为防止国内用户访问CodeAnalysis Github首页时图片资源加载失败，目前各个md文件中的图片资源引用地址调整增加了URL前缀`https://tencent.github.io/CodeAnalysis/`。

用户下载代码库到本地后，发现无法访问资源文件时，请检查本地网络是否能够连通外网，如果无法连通外网，可以在文档引入资源地址中进行**相对路径**替换，调整各个资源文件的链接。

- 对于根目录下的md文件，直接删除URL前缀即可：

  例如在`https://tencent.github.io/CodeAnalysis/media/homepage.png`这个链接可以调整为`media/homepage.png`

- 对于其他目录下的md文件，删除URL前缀后，需调整文件相对路径链接：

  例如对于`doc/client.md`, 需将`https://tencent.github.io/CodeAnalysis/media/clientConfigIni.png`这个链接调整为`../media/clientConfigIni.png`
