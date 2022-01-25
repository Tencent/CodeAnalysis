# TCA Client 客户端使用文档

## 一、基础配置

### 机器配置推荐
|   操作系统 | 推荐配置                                       |
| --------: | :------------------------------------------- |
|     Linux | 8核16G内存，硬盘空间256G（可用空间不低于100G）     |   
|       Mac | 8核16G内存，硬盘空间256G（可用空间不低于100G）     |
|   Windows | 8核16G内存，硬盘空间256G（可用空间不低于100G）     |

> 以上为推荐配置，实际情况需要考虑扫描对象代码库的大小，按实际情况增加磁盘空间。

## 二、使用docker环境快速体验
> 适用于快速上手体验。使用docker运行，可以免去客户端环境依赖的安装，避免环境兼容性问题。
> 但是由于环境受限于docker，会无法复用本地的编译环境，部分需要编译的工具无法使用。
### 1. 下载和安装Docker
参考Docker官方文档：[Docker下载和安装](https://docs.docker.com/get-started/)

### 2. 构建docker镜像
在`client`目录下，执行以下命令：`docker build -t tca-client .`

### 3. 配置client/config.ini文件
将`<Server IP地址>`替换成实际的serve ip（可包含端口号）。

### 4. 配置client/codedog.ini文件
1. 填写以下必填项：`token`,`org_sid`,`team_name`,`source_dir`
- 各字段获取方式，详见根目录下文档`《GettingStart(TCA快速入门).pdf》`
- 注意：`source_dir`此处填写为固定的docker内路径：`/workspace/src`
2. 按需填写其他可选项，也可以不填，按默认配置执行

### 5. 执行docker容器，扫描代码，可选以下两种方式
#### (1)直接使用docker运行
- 在client目录下，执行以下命令：
- (注意：按照实际情况填写`SOURCE_DIR`环境变量值)
```bash
export SOURCE_DIR=需要扫描的代码目录绝对路径
docker run -it --rm  -v $PWD:/workspace/client -v $SOURCE_DIR:/workspace/src  --name tca-client tca-client
```
#### (2)使用docker内bash终端运行
- 通过以下方式，进入容器内的bash终端后，通过命令行启动client代码：
- 在client目录下，执行以下命令：
- (注意：按照实际情况填写`SOURCE_DIR`环境变量值)
```bash
export SOURCE_DIR=需要扫描的代码目录绝对路径
docker run -it --rm  -v $PWD:/workspace/client -v $SOURCE_DIR:/workspace/src  --name tca-client tca-client bash
# 进入容器内终端，通过命令行执行扫描
python3 codepuppy.py localscan
```


## 三、使用本地机器环境运行
> 适用于深度体验，可以复用本地编译环境，使用编译型代码分析工具。
> 可能会有系统环境兼容问题。

### 安装Python环境和第三方库
1. 预装Python3.7、pip，支持 `python3` 和 `pip3` 命令 
2. 安装依赖：`pip3 install -r client/requirements/app_reqs.pip`

### 安装第三方工具
1. 进入到`client/requirements`目录
2. 在命令行中执行安装脚本`install.sh`(linux/mac环境)或`install.bat`(windows环境)

### 配置client/config.ini文件
将`<Server IP地址>`替换成实际的serve ip（可包含端口号）。

### 配置client/codedog.ini文件
1. 填写以下必填项：`token`,`org_sid`,`team_name`,`source_dir`
- 各字段获取方式，详见根目录下文档`《GettingStart(TCA快速入门).pdf》`
2. 按需填写其他可选项，也可以不填，按默认配置执行

### 启动代码分析
1. 进入到`client`目录下
2. 执行命令：`python3 codepuppy.py localscan`


## 四、其他配置与用法

### 1. 配置使用本地工具

> 如果由于网络原因，执行时无法从github自动拉取工具，或拉取比较慢，可以预先下载好工具，配置使用本地工具目录。

- （1）下载工具配置库 `https://github.com/TCATools/puppy-tools-config.git` ，存放到 `client/data/tools`目录下（如果未生成，可先创建该目录）。
- （2）根据当前机器操作系统，查看`puppy-tools-config`目录下的`linux_tools.ini`或`mac_tools.ini`或`windows_tools.ini`文件，将`[tool_url]`中声明的所有工具下载到 `client/data/tools`目录下。
- （3）填写`client/config.ini`中的配置：`USE_LOCAL_TOOL`=`True`，即可使用下载好的本地工具，不自动拉取和更新工具。

### 2. 使用自建git server存放工具

> 如果自己搭建了一套git server，可以将工具配置库 `https://github.com/TCATools/puppy-tools-config.git` 以及里面声明的工具仓库，存放到自建git serevr上。

- （1）将工具配置库 `https://github.com/TCATools/puppy-tools-config.git` 上传到自建git仓库。
- （2）按所需的操作系统，将`puppy-tools-config`仓库下的`linux_tools.ini`或`mac_tools.ini`或`windows_tools.ini`文件中`[tool_url]`声明的所有工具库，上传到自建git仓库。
- （3）修改`linux_tools.ini`或`mac_tools.ini`或`windows_tools.ini`文件中`[base_value]`中的`git_url`为自建git server地址。
- （4）修改`client/config.ini`中的`TOOL_CONFIG_URL`为自建git server的`puppy-tools-config`仓库地址。
- （5）填写`client/config.ini`中的`[TOOL_LOAD_ACCOUNT]`配置，输入有拉取权限的用户名密码，即可使用自建git server拉取工具。

### 3. git lfs带宽和存储配额不够问题

- 如果git拉取工具时，出现git lfs拉取失败，可能是lfs带宽和存储配额不够，可以打开对应的工具github页面，通过`Download ZIP`的方式下载工具压缩包，再解压到`client/data/tools`目录下。