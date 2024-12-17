# TCA Client 客户端使用文档

## 一、基础配置

### 1. 机器配置推荐
|   操作系统 | 推荐配置                                       |
| --------: | :------------------------------------------- |
|     Linux | 8核16G内存，硬盘空间256G（可用空间不低于100G）     |   
|       Mac | 8核16G内存，硬盘空间256G（可用空间不低于100G）     |
|   Windows | 8核16G内存，硬盘空间256G（可用空间不低于100G）     |

以上为推荐配置，实际情况需要考虑扫描对象代码库的大小，按实际情况增加磁盘空间。

### 2. 安装Python环境和第三方库(docker模式无需配置)
- (1) 预装Python3.7、pip，支持 `python3` 和 `pip3` 命令 
- (2) 安装依赖：`pip3 install -r client/requirements/app_reqs.pip`

### 3. 安装第三方工具(docker模式无需配置)
- (1) 进入到`client/requirements`目录
- (2) 在命令行中执行安装脚本`install.sh`(linux/mac环境)或`install.bat`(windows环境)

### 4. 配置client/config.ini文件
- 将`<Server IP地址>`替换成实际的serve ip（可包含端口号）。

### 5. 配置client/codedog.ini文件（分布式节点模式无需配置）
填写以下必填项：`token`,`org_sid`,`team_name`,`source_dir`

|   字段名 | 填写说明                                       |
| --------: | :------------------------------------------- |
| `token` | 从tca页面获取，前往[个人中心]-[个人令牌]-复制Token |
|  `org_sid`(团队编号) | 从tca项目概览页面URL中获取，项目概览URL格式：`http://{域名}/t/{org_sid}/p/{team_name}/profile` |
|  `team_name`(项目名称) | 同上 |
|  `source_dir` | 本地代码目录路径 |

其他可选项按需填写。各字段获取方式，详见文档`doc/client.md`。

## 二、使用本地机器环境运行
> 适用于深度体验，可以复用本地编译环境，使用编译型代码分析工具。
> 可能会有系统环境兼容问题。

### 1. 启动代码分析
- (1) 进入到`client`目录下
- (2) 执行命令：`python3 codepuppy.py localscan`

## 三、使用docker模式运行
> 适用于快速上手体验。使用docker运行，可以免去客户端环境依赖的安装，避免环境兼容性问题。
> 但是由于环境受限于docker，会无法复用本地的编译环境，部分需要编译的工具无法使用。
### 1. 下载和安装Docker
参考Docker官方文档：[Docker下载和安装](https://docs.docker.com/get-started/)

### 2. 构建docker镜像
在`client`目录下，执行以下命令：
- `docker build --build-arg TARGETARCH={ARCH} -t tca-client .`
> 变量`{ARCH}`替换为需要构建的架构，可选值：amd64, arm64.

### 3. 执行docker容器，扫描代码，可选以下两种方式

- 注意：因为以下步骤会将代码目录挂载到容器中，需要先将codedog.ini里面的source_dir修改为`/workspace/src`，其他参数保持不变。

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

## 四、使用分布式节点模式执行客户端
> TCA客户端除了通过`localscan`命令启动单次的代码分析，也可以作为一个分布式分析节点启动，作为常驻进程，多个节点可以分布式并行执行服务端下发的任务，提高扫描效率。
> 和本地执行任务一样，需要先安装环境和必要的工具，并配置好服务端地址。

### 1. 启动代码分析节点
- （1）从tca页面`个人中心`-`个人令牌`-复制Token
- （2）进入到`client`目录下，执行命令：`python3 codepuppy.py -l codepuppy.log start -t <token>`
- （3）启动后，可以在命令行输出或`codepuppy.log`中查看运行日志，如果未报异常，且输出`task loop is started.`，表示节点已经正常启动。

> 注：节点首次运行会提示“节点处于不可用状态”，此时需要到平台上管理后台的“节点管理”模块将节点标记为“活跃”（[参考文档](https://github.com/Tencent/CodeAnalysis/blob/main/doc/%E3%80%90%E8%85%BE%E8%AE%AF%E4%BA%91%E4%BB%A3%E7%A0%81%E5%88%86%E6%9E%90%E3%80%91%E4%BB%BB%E5%8A%A1%E5%88%86%E5%B8%83%E5%BC%8F%E6%89%A7%E8%A1%8C%E8%83%BD%E5%8A%9B.md)）

### 2. 配置节点
- 从tca页面`管理入口`-`节点管理`，可以看到当前在线的节点，可以修改节点名称、标签、负责人等信息。
- 可以进入工具进程配置页面，对节点支持的工具进程进行管理（默认会全部勾选），未勾选的工具进程，将不会在该节点上执行。
- 节点所属标签会与分析方案中的运行环境标签进行匹配，只有相同标签的任务才会下发到该机器节点上。


## 五、其他配置与用法

### 1. 配置使用本地工具

> 如果由于网络原因，执行时无法从github自动拉取工具，或拉取比较慢，优先考虑使用腾讯工蜂地址（参考基础配置第4点）; 或使用以下方式预先下载好工具，配置使用本地工具目录。

- （1）下载工具配置库（二选一：https://git.code.tencent.com/TCA/tca-tools/puppy-tools-config.git 或 https://github.com/TCATools/puppy-tools-config.git ），存放到 tools 目录下。
- （2）根据当前机器操作系统，查看 puppy-tools-config 目录下的 linux_tools.ini 或 mac_tools.ini 或 windows_tools.ini 文件，将`[tool_url]`中声明的所有工具下载到 tools 目录下。
- （3）填写`client/config.ini`中的配置：`USE_LOCAL_TOOL`=`True`，即可使用下载好的本地工具，不自动拉取和更新工具。

### 2. 使用自建 git server 存放工具

> 如果自己搭建了一套git server，可以将工具配置库以及里面声明的工具仓库，存放到自建 git server 上。

- （1）将工具配置库（二选一：https://git.code.tencent.com/TCA/tca-tools/puppy-tools-config.git 或 https://github.com/TCATools/puppy-tools-config.git ）上传到自建git仓库。
- （2）按所需的操作系统，将`puppy-tools-config`仓库下的`xxx_tools.ini`文件中`[tool_url]`声明的所有工具库，上传到自建git仓库。
- （3）修改`xxx_tools.ini`文件中`[base_value]`中的`git_url`为自建 git server 地址。
- （4）修改`client/config.ini`中的`TOOL_CONFIG_URL`为自建git server的`puppy-tools-config`仓库地址。
- （5）填写`client/config.ini`中的`[TOOL_LOAD_ACCOUNT]`配置，输入有拉取权限的用户名密码，即可使用自建git server拉取工具。

### 3. git lfs带宽和存储配额不够问题
- 优先考虑切换为腾讯工蜂源（参考基础配置第4点）
- 如果git拉取工具时，出现git lfs拉取失败，可能是lfs带宽和存储配额不够，可以打开对应的工具github页面，通过`Download ZIP`的方式下载工具压缩包，再解压到`tools`目录下。
