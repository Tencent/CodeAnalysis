# 增强分析模块部署
TCA 除开集成业界知名的分析工具之外，也有自主研发的独立工具，作为 TCA 的增强分析模块。

TCA 增强分析模块，需要用户额外部署 License 鉴权微服务，并邮件申请 License 。

::: tip
**1. License申请完全免费！**
2. 优先企业或高校申请License。
:::

## 概念
- 独立工具：TCA 自主研发的代码分析工具；
- CLS(Common License Server)： TCA 独立工具的 License 鉴权微服务。

## 模块功能
- 支持Objective-C/C++代码规范检查；
- 支持分析项目的依赖组件；
- 支持分析依赖组件是否存在漏洞等问题；
- 支持Java/Kotlin API和函数调用链分析；
- 支持代码安全、空指针检查、内存泄漏等规则。

**持续更新中……**

## TCA 官网版增强能力申请
如果用户平常使用的是 [TCA 官网版公共服务](https://tca.tencent.com/)，并想在官网版上体验到增强分析模块的分析能力，可以按照[这篇帮助文档](https://tca.tencent.com/document/zh/guide/%E5%AE%A2%E6%88%B7%E7%AB%AF%E6%8E%A5%E5%85%A5/License%E9%85%8D%E7%BD%AE.html)进行申请配置。


## TCA 私有化部署增强能力申请
如果用户是在企业内网环境内使用 TCA，并想在内网体验 TCA 的增强分析模块能力，可以参考下面步骤申请。

### 准备
- 一台 CLS 微服务专属机器，CLS 微服务需要跟该机器绑定

::: warning
**注意：不能随意删除CLS目录**
:::

### 步骤
1. 在 TCA 源码中[`server/cls`](https://github.com/Tencent/CodeAnalysis/tree/main/server/cls) 目录下执行以下命令，获取 `Server ID` 和 `Client License`

::: warning
**注意：需要在 CLS 目录下执行命令**
:::

```shell
# 安装 Git LFS
$ bash ./scripts/base/install_git_lfs.sh
# 如果在该目录下没有找到 cls 二进制文件，可以执行以下命令进行同步
$ bash ./scripts/base/install_bin.sh
$ cd server/cls
$ ./cls server
2022-04-13 18:35:29.356510559 +0800 CST [INFO] Version: 20220328.1
2022-04-13 18:35:29.44083463 +0800 CST [INFO] The client license is:
xxx
2022-04-13 18:35:29.454552966 +0800 CST [INFO] License Server ID: xxx
```
- `Server ID`: 机器码，用于向 TCA 团队申请 License 授权
- `Client License`: 提供给 TCA Client，方便 TCA Client 进行工具鉴权（重要，建议备份留底）

2. 在 TCA Client目录的 [`config.ini`](https://github.com/Tencent/CodeAnalysis/blob/main/client/config.ini) 中配置 CLS 微服务信息，比如

```ini
[LICENSE_CONFIG]
; [可选]使用独立工具时，需要填写，默认不需要
; License服务的域名和端口
URL=http://<IP或者域名>:<port>
BASE_PATH=
LICENSE=<Client License>
```

::: warning
注意：URL对应值的最后不需要跟斜杆`/`.
:::

::: warning
不同的部署方式可以根据下面方法修改`config.ini`配置

- 源码部署：
  - 修改源码目录下的`client/config.ini`
  - 重启客户端：`./quick_install.sh local start client`
- Docker部署：
  - 方式1: 修改源码目录下的`.docker_temp/configs/client/config.ini`，并重启`tca-services`容器
  - 方式2: 进入`tca-service`容器后，修改`/CodeAnalysis/client/config.ini`，并退出重启`tca-services`容器
  - 重启容器方式：`docker restart tca-service`
- Docker-Compose部署:
  - 修改源码目录下的`client/config.ini`，并重启`client`容器
  - 重启容器方式：`docker-compose restart client`
:::

3. 在 TCA 云官网上提交私有云 License 申请
- (1) 在 [TCA 云官网](https://tca.tencent.com/)上注册或登录账号;
- (2) 进入需要申请私有云 License 申请的团队（如果没有的话需要创建对应团队）；
- (3) 在团队页面上，依次进入【节点管理】->【私有云 License 配置】页面，然后点击右上角的【申请License】按钮，填写相关信息即可提交申请。具体的信息内容如下：
  - 申请人名称
  - 申请人所在组织名称
  - 申请人所在组织类型：公司/高校/个人
  - 申请人邮箱
  - 申请人手机号码
  - Server ID：步骤一中输出的`Server ID`，首次登记的机器码
  - Client License：步骤一中输出的`Client License`
  - 应用场景
- (4) 然后等待申请License审核通过，即可拷贝出该私有云 License 继续进行下面第4步的操作。

4. 在 CLS 目录下的 [`config.yaml`](https://github.com/Tencent/CodeAnalysis/blob/main/server/cls/config.yaml) 文件中填写License  

::: warning
注意：遵从 yaml 格式，比如：
- 键值对中，冒号 `:` 后面跟一个空白字符，示例 `key: value`。
:::

5. 执行以下命令启动 CLS

```shell
./cls server -d
```

6. 验证 CLS 进程正常启动

```bash
# 查找是否存在CLS进程
ps aux|grep cls
```

::: warning
注意：如果以上命令没有发现 CLS 的进程，则说明 CLS 没有正常启动。  
请尝试更改 [`config.yaml`](https://github.com/Tencent/CodeAnalysis/blob/main/server/cls/config.yaml) 文件中的 port 为其他 port，比如8080，目前默认是80端口，然后重新执行步骤5的命令。
:::

7. 启动 TCA 分析任务
在 TCA 平台的分析方案里面勾选独立工具相关的规则包，比如依赖组件分析规则包，然后启动一次分析任务，执行正常则表明设置生效。

### CLS 运维
#### 自动重启
```shell
# 查找CLS进程ID
ps aux|grep cls
# 重启微服务
kill -USR2 <pid>
```

#### 网络异常
如果以上部署步骤已经完成，但是增强功能还是出现 `License check failed! Please check the license. License Server is not available!` 异常。可以按照以下步骤进行排查：

- 进入任务页面，点击异常工具，下载该工具的执行日志。如果日志中出现以下日志，则表明网络访问CLS异常；
```log
method(head) call fails on error: <urlopen error [Errno 111] Connection refused>
```
- 继续验证。如果是 Docker 或者 Docker-Compose 部署方式的话，进入 TCA Client 所在容器中。如果是源码部署，则来到 TCA Client 所在机器上。执行以下命令确认网络是否通路：
```bash
ping <config.ini中填写的 CLS IP或者域名>
telnet <config.ini中填写的 CLS IP或者域名> <对应端口>
```
- 如果网络不通，请排查：
  * 防火墙是否开启对应端口；
  * CLS 对应域名是否在host中设置；
  * 是否IP设置错误。

##### 案例分享
背景：
小明以 Docker 方式部署 TCA，并在相同宿主机上部署 CLS 服务，然后在 config.ini 中设置的 URL 中的 IP 为 `127.0.0.1`, 重启后启动增强功能任务遇到上述网络不通异常。  
原因：
原因是此时的 `127.0.0.1` 指向的是 TCA Client 容器自身，而不是部署在宿主机上的 CLS 服务。  
解决方案：
将 `127.0.0.1` 改成宿主机自身IP即可。

#### CLS 更新

1. 使用以下命令查找 cls 进程并杀掉进程
```shell
# 查找CLS进程ID
ps aux|grep cls
# 重启微服务
kill -9 <pid>
```
2. 下载最新版的 cls 并覆盖掉其中的 cls 二进制文件  
::: warning
注意：不能删除原来的 cls 目录，只需要替换其中的 cls 二进制文件即可。
:::
3. 使用以下命令重启 cls 服务
```shell
./cls server -d
```
