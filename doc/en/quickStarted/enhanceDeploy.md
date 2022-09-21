# 增强分析模块部署
TCA 除开集成业界知名的分析工具之外，也有自主研发的独立工具，作为 TCA 的增强分析模块。

TCA 增强分析模块，需要用户额外部署 License 鉴权微服务，并邮件申请 License 。

::: tip
**注意：License申请完全免费！**
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
## CLS部署

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

3. 向 TCA 团队邮件申请 License

- 收件邮箱：
```
v_cocohwang@tencent.com
anjingliu@tencent.com
yalechen@tencent.com
tommyzhang@tencent.com
```

- 申请邮件格式如下：

主题：**TCA 独立工具 License 申请**

正文：
| | | 
|  :----:  | :----:  |
| 申请人名称  | xxx |
| 申请人所在组织名称 | xxx |
| 申请人所在组织类型 | 可选选项：公司/学校/个人 |
| 申请人邮箱 | xxx |
| 申请人手机号码 | xxx |
| 首次登记的机器码 | xxx |
| 体验申请用途 | xxx |

4. 收到 TCA 团队回复邮件之后，在 CLS 目录下的 [`config.yaml`](https://github.com/Tencent/CodeAnalysis/blob/main/server/cls/config.yaml) 文件中填写License  

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

