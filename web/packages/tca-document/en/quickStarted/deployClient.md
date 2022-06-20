# 部署与配置客户端

## 通过源代码

### 依赖环境

- 系统要求

    - Linux，Windows或macOS
    - [Python 3.7](https://docs.python.org/zh-cn/3.7/using/unix.html)


### 部署步骤

#### 部署客户端

1. 安装Python环境和第三方库

    - 安装[Python3.7](https://docs.python.org/zh-cn/3.7/using/unix.html)、[pip3](https://pip.pypa.io/en/stable/installation/)
      > 通过``python3 --version``和``pip3 --version``检查是否正确配置环境。
    - 在本地源码目录下安装依赖
    ```bash
    pip3 install -r client/requirements/app_reqs.pip
    ```

2. 安装第三方工具

    - 进入到`client/requirements`目录  
    - 在命令行中执行安装脚本
    ```bash
    #Linux/macOS环境
    ./install.sh
    #Windows环境
    ./install.bat
    ```

#### 配置客户端

- 配置client/config.ini文件
将`<Server IP地址>`替换成实际的serve ip（可包含端口号）。
<img src="../../images/clientConfigIni.png" width = "80%" />

- 配置client/codedog.ini文件
    - 填写以下必填项：`token`,`org_sid`,`team_name`,`source_dir`
        - `token`: 从tca页面获取，前往[个人中心]-[个人令牌]-复制Token
        ![personalToken](../../images/personalToken.png)
        - `org_sid`(团队编号),`team_name`(项目名称): 从tca项目概览页面URL中获取，项目概览URL格式：http://{域名}/t/{org_sid}/p/{team_name}/profile
        ![orgsid](../../images/orgsid.png)
        - `source_dir`: 本地代码目录路径
- 按需填写其他可选项，也可以不填，按默认配置执行

#### 启动客户端

进入到`client`目录下，执行客户端脚本
```bash
python3 codepuppy.py localscan
```
> 使用`localscan`命令启动本地单次的代码分析，如需启动分布式并行分析任务，请参考[常驻节点分析](../guide/%E5%AE%A2%E6%88%B7%E7%AB%AF/%E5%B8%B8%E9%A9%BB%E8%8A%82%E7%82%B9%E5%88%86%E6%9E%90.md)进行配置。

## 通过Docker-Compose

> 适用于快速上手体验。使用docker运行，可以免去客户端环境依赖的安装，避免环境兼容性问题。
> 但是由于环境受限于docker，会无法复用本地的编译环境，部分需要编译的工具无法使用。


### 部署步骤

#### 配置客户端

- 配置client/config.ini文件
将`<Server IP地址>`替换成实际的serve ip（可包含端口号）。
<img src="../../images/clientConfigIni.png" width = "80%" />

- 配置client/codedog.ini文件
    - 填写以下必填项：`token`,`org_sid`,`team_name`,`source_dir`
        - `token`: 从tca页面获取，前往[个人中心]-[个人令牌]-复制Token
        ![personalToken](../../images/personalToken.png)
        - `org_sid`(团队编号),`team_name`(项目名称): 从tca项目概览页面URL中获取，项目概览URL格式：http://{域名}/t/{org_sid}/p/{team_name}/profile
        ![orgsid](../../images/orgsid.png)
        - `source_dir`: 本地代码目录路径
- 按需填写其他可选项，也可以不填，按默认配置执行

#### 构建客户端镜像

1. 安装Docker，安装教程：[官方文档](https://docs.docker.com/engine/install/)
2. 安装Docker-Compose，安装教程：[官方文档](https://docs.docker.com/compose/install/)
3. 进入`client`目录，构建docker镜像

```bash
docker build -t tca-client .
```

#### 启动客户端

##### 方案一：直接使用docker运行

1. 进入`client`目录，执行以下命令
```bash
# 按照实际情况填写`SOURCE_DIR`环境变量值
export SOURCE_DIR=需要扫描的代码目录绝对路径
docker run -it --rm  -v $PWD:/workspace/client -v $SOURCE_DIR:/workspace/src  --name tca-client tca-client
```

##### 方案二：使用docker内bash终端运行

1. 进入docker容器内的bash终端
```bash
# 按照实际情况填写`SOURCE_DIR`环境变量值
export SOURCE_DIR=需要扫描的代码目录绝对路径
docker run -it --rm  -v $PWD:/workspace/client -v $SOURCE_DIR:/workspace/src  --name tca-client tca-client bash
```
2. 通过命令行启动client代码
```bash
python3 codepuppy.py localscan
```

## 通过可执行文件

### 依赖环境

- 系统要求

    - Linux，Windows或macOS


### 部署步骤

#### 下载客户端

1. 从[发布页面](https://github.com/Tencent/CodeAnalysis/releases)下载与系统相对应的客户端压缩包到本地。

2. 解压缩。

#### 配置客户端

- 配置client/config.ini文件
将`<Server IP地址>`替换成实际的serve ip（可包含端口号）。
<img src="../../images/clientConfigIni.png" width = "80%" />

- 配置client/codedog.ini文件
    - 填写以下必填项：`token`,`org_sid`,`team_name`,`source_dir`
        - `token`: 从tca页面获取，前往[个人中心]-[个人令牌]-复制Token
        ![personalToken](../../images/personalToken.png)
        - `org_sid`(团队编号),`team_name`(项目名称): 从tca项目概览页面URL中获取，项目概览URL格式：http://{域名}/t/{org_sid}/p/{team_name}/profile
        ![orgsid](../../images/orgsid.png)
        - `source_dir`: 本地代码目录路径
- 按需填写其他可选项，也可以不填，按默认配置执行

#### 启动客户端

进入到`client`目录下，执行客户端
```bash
./codepuppy localscan
```
> 使用`localscan`命令启动本地单次的代码分析，如需启动分布式并行分析任务，请参考[常驻节点分析](../guide/%E5%AE%A2%E6%88%B7%E7%AB%AF/%E5%B8%B8%E9%A9%BB%E8%8A%82%E7%82%B9%E5%88%86%E6%9E%90.md)进行配置。