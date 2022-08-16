# 平台概述

**腾讯云代码分析**（Tencent Cloud Code Analysis，简称TCA，内部曾用研发代号 **CodeDog** ）是集众多分析工具的云原生、分布式、高性能的代码综合分析跟踪平台，包含服务端、Web端和客户端三个组件，已集成一批自研工具，同时也支持动态集成业界各编程语言的分析工具。

### 使用TCA Action快速体验
使用TCA Action，只需要在代码仓库中添加`.github/workflows/tca.yml`文件，就可以直接在GitHub工作流中快速体验代码分析。请参考：[TCA-action指引](https://github.com/TCATools/TCA-action/blob/main/README.md)

### 部署TCA

拉取 [代码库](https://github.com/Tencent/CodeAnalysis) 后，您可以通过以下三种方式部署腾讯云代码分析平台：

- [通过 Docker 部署](./deploySever.md#通过docker)

- [通过源代码](./codeDeploy.md#通过源代码)

- [通过 Docker-Compose 部署](./dockercomposeDeploy.md#通过docker-compose)

### 创建首个代码分析项目

成功部署并启动TCA后，您可以按照 [指引](./deploySever.md) 创建您的首个代码分析项目。

:::tip
默认平台登录账号/密码：CodeDog/admin
:::

### 快速扩展客户端

TCA客户端支持通过可执行文件进行快速扩展部署，详见[通过可执行文件](./deployClient.md#通过可执行文件)

:::tip
客户端可在本地执行代码分析，也可以作为[在线常驻节点](../advanced/任务分布式执行.md)进行在线分析。
:::

### 了解更多

更多关于腾讯云代码分析平台的使用指南和配置说明，参见[帮助文档](../guide/README.md)。
