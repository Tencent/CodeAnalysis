# 部署与配置客户端

## 通过源代码

### 依赖环境

- 系统环境

  - Linux，Windows或macOS

- 环境准备

  - **Python 3.7**，[安装指引](./references/install_python37_on_centos.md)

### 使用步骤

#### 安装第三方库

```bash
# 源码根目录下执行
pip3 install -r client/requirements/app_reqs.pip
```

#### 安装第三方工具

```bash
# 源码根目录
cd client/requirements

# 执行安装脚本
# Linux/macOS环境
./install.sh
# Windows环境
./install.bat
```

#### 配置客户端

- 配置 `client/config.ini` 文件

  将 `<Server IP地址>` 替换成实际的serve ip（可包含端口号）。  

  ![客户端执行环境配置](https://tencent.github.io/CodeAnalysis/media/clientConfigIni.png)

- 配置 `client/codedog.ini` 文件

  必填项：`token`、`org_sid`、`team_name`、`source_dir`

  - **个人令牌** - `token`：从 TCA 页面获取，前往[个人中心]-[个人令牌]-复制Token

    ![personalToken](../../images/personalToken.png)

  - **团队编号** - `org_sid`：进入 TCA 项目概览页，从 URL 中获取

  - **项目名称** - `team_name`：：进入 TCA 项目概览页，从 URL 中获取

      :::tip
      项目概览URL格式：`http://{域名}/t/{org_sid}/p/{team_name}/profile`
      :::

  - **分析路径** - `source_dir`: 本地代码目录路径

  :::tip
  - 如果项目代码为编译型语言（比如：C/C++，C#，Go，Java，Kotlin，Objective-C等），且使用的分析方案中配置了编译型工具（如图，使用了OC推荐规则包），需要填写`build_cmd`编译命令。

  - 其他可选项按需填写，不填写时按默认配置执行
  :::
  
#### 启动客户端

```bash
# 源码根目录
cd client

# 执行客户端脚本
python3 codepuppy.py localscan
```

:::warning
Client 的实现及启动脚本均依赖 Python3 版本为 3.7，可执行 ``python3 --version`` 查看版本。若版本有误，可安装版本为3.7的python并软链接到python3命令。
:::

:::tip

- `codedog.ini` 各项参数可由命令行传入，获取详细参数说明可运行 `python3 codepuppy.py localscan -h`

- 使用`localscan`命令启动本地单次的代码分析，如需启动分布式并行分析任务，请参考[使用分布式节点模式](../client/README.md#五使用分布式节点模式执行客户端)进行配置。
:::

## 通过Docker-Compose

:::tip
适用于快速上手体验。使用docker运行，可以免去客户端环境依赖的安装，避免环境兼容性问题。

但是由于环境受限于docker，会无法复用本地的编译环境，部分需要编译的工具无法使用。
:::

### 使用步骤

#### 配置客户端

- 配置 `client/config.ini` 文件

- 配置 `client/codedog.ini` 文件

:::tip
同通过源代码使用-[配置客户端](./deployClient.md#配置客户端)
:::

#### 构建镜像

1. 安装Docker，安装教程：[官方文档](https://docs.docker.com/engine/install/)

2. 安装Docker-Compose，安装教程：[官方文档](https://docs.docker.com/compose/install/)

3. 进入`client`目录，构建docker镜像

```bash
docker build -t tca-client .
```

#### 启动客户端

##### 方案一：直接使用docker运行

进入`client`目录，执行以下命令

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
    docker run -it --rm  -v $PWD:/workspace/client -v $SOURCE_DIR:/workspace/src --name tca-client tca-client bash
    ```

2. 通过命令行启动client代码

    ```bash
    python3 codepuppy.py localscan
    ```

## 通过可执行文件

### 依赖环境

- 系统环境

  - Linux，Windows或macOS

### 使用步骤

#### 下载客户端

1. 从[发布页面](https://github.com/Tencent/CodeAnalysis/releases)下载与系统相对应的客户端压缩包到本地。

2. 解压缩。

#### 配置客户端

- 配置 `client/config.ini` 文件

- 配置 `client/codedog.ini` 文件

:::tip
同通过源代码使用-[配置客户端](./deployClient.md#配置客户端)
:::

#### 启动客户端

进入到`client`目录下，执行客户端

```bash
./codepuppy localscan
```
