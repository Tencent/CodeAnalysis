# 腾讯云代码分析

**腾讯云代码分析**（Tencent Cloud Code Analysis，简称TCA，内部曾用研发代号 **CodeDog** ）是集众多分析工具的云原生、分布式、高性能的代码综合分析跟踪平台，包含服务端、Web端和客户端三个组件，已集成一批自研工具，同时也支持动态集成业界各编程语言的分析工具。

通过以下步骤，您可以将腾讯云代码分析部署到本地，快速启动并运行您的代码分析项目。

:::tip

- 通过部署 TCA Server 和 Web 得到腾讯云代码分析平台，并在平台完成相关项目的创建；
- 完成项目创建后，您可以通过部署并配置腾讯云代码分析客户端，将客户端在**本地**或作为**在线常驻节点**执行代码分析。
- 如果您在部署或使用腾讯云代码分析的过程中遇到了问题，可以参考[常见问题](FAQ.md)。
:::

## 使用TCA Action快速体验
使用TCA Action，只需要在代码仓库中添加`.github/workflows/tca.yml`文件，就可以直接在GitHub工作流中快速体验代码分析。请参考：[TCA-action指引](https://github.com/TCATools/TCA-action/blob/main/README.md)

## 部署 Server 和 Web

拉取 [代码库](https://github.com/Tencent/CodeAnalysis) 后，您可以通过以下两种方式部署腾讯云代码分析的 Server 和 Web 服务：

- [通过源代码](./deploySever.md#通过源代码)

- [通过 Docker-Compose 部署](./deploySever.md#通过docker-compose)

## 创建首个代码分析项目

成功部署并启动 Server 与 Web 服务后，您可以按照 [指引](./initRepo.md) 创建您的首个代码分析项目。

:::tip
默认平台登录账号/密码：CodeDog/admin
:::

## 部署与配置客户端

在启动您的首个代码分析项目前，您需要在本地部署腾讯云代码分析的客户端。完成客户端的项目配置后，即可启动您的首个代码分析项目，并在腾讯云代码分析平台上查看您的分析结果。

您可以通过以下三种方式部署并使用腾讯云代码分析的客户端：

- [通过源代码](./deployClient.md#通过源代码)

- [通过 Docker-Compose](./deployClient.md#通过docker-compose)

- [通过可执行文件](./deployClient.md#通过可执行文件)

:::tip
客户端可在本地执行代码分析，也可以作为[在线常驻节点](../advanced/任务分布式执行.md)进行在线分析。
:::

## 了解更多

更多关于腾讯云代码分析平台的使用指南和配置说明，参见[帮助文档](../guide/README.md)。
