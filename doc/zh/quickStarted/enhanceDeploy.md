# 增强分析模块部署
TCA 除开集成业界知名的分析工具之外，也有自主研发的独立工具，作为 TCA 的增强分析模块。

TCA 增强分析模块，需要用户额外部署 License 鉴权微服务，并邮件申请 License 。

**注意：License申请完全免费！** 

## 概念
- 独立工具：TCA 自主研发的代码分析工具；
- CLS(Common License Server)： TCA 独立工具的 License 鉴权微服务。

## 模块功能
- 支持Objective-C/C++代码规范检查；
- 支持分析项目的依赖组件；
- 支持分析依赖组件是否存在漏洞等问题；
- 支持Java/Kotlin API和函数调用链分析；
- 支持代码安全、空指针检查、内存泄漏等规则。

## CLS部署

### 准备
- 一台 CLS 微服务专属机器，CLS 微服务需要跟该机器绑定

### 步骤
1. 在 CLS 目录下执行以下命令，获取 Server ID 和 Client License
```shell
$ ./cls server
2022-04-13 18:35:29.356510559 +0800 CST [INFO] Version: 20220328.1
2022-04-13 18:35:29.44083463 +0800 CST [INFO] The client license is:
xxx
2022-04-13 18:35:29.454552966 +0800 CST [INFO] License Server ID: xxx
```
- Server ID: 机器码，用于跟TCA团队申请License授权
- Client License: 提供给TCA Client, 方便TCA Client进行工具鉴权（重要，建议备份留底）

2. 在 TCA Client 的 config.ini 中配置 CLS 微服务，比如
```ini
[LICENSE_CONFIG]
; [可选]使用独立工具时，需要填写，默认不需要
; License服务器url, base_path, license
URL=http://<IP或者域名>:<port>
BASE_PATH=
LICENSE=<client License>
```

3. 跟 TCA 团队邮件申请 License

- 发送邮箱：
```
v_cocohwang@tencent.com
anjingliu@tencent.com
yalechen@tencent.com
tommyzhang@tencent.com
```

- 格式如下：

TCA独立工具License申请邮件

| |  |
|  :----:  | :----:  |
| 申请人名称  | xxx |
| 申请人所在组织名称 | xxx |
| 申请人所在组织类型 | 可选选项：公司/学校/个人 |
| 申请人邮箱 | xxx |
| 申请人手机号码 | xxx |
| 首次登记的机器码 | xxx |
| 体验申请用途 | xxx |

4. 收到 TCA 团队回复邮件之后，在 CLS 目录下的[config.yaml](config.yaml)文件中填写License  
注意！请遵从yaml格式，比如：
- 键值对中，冒号 `:` 后面一定要跟一个空白字符，示例 `key: value`.

5. 执行以下命令启动
```shell
./cls server -d
```

6. 启动 TCA 分析任务

### 运维
#### 自动重启
```shell
# 查找CLS进程ID
ps aux|grep cls
# 重启微服务
kill -USR2 <pid>
```

## 使用

在 TCA 对应项目的分析方案里面勾选名称以 `TCA-Armory` 开头的工具的规则。
