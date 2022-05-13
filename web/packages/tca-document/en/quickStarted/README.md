# 腾讯云代码分析

**腾讯云代码分析**（**Code Analysis, TCA**）支持Linux、Windows和macOS等多种平台。通过以下步骤，您可以将腾讯云代码分析部署到本地，快速启动并运行您的代码分析项目。

> 如果您在部署或使用腾讯云代码分析的过程中遇到了问题，可以参考[常见问题](FAQ.md)。

## 部署Server和Web

拉取[代码库](https://github.com/Tencent/CodeAnalysis)后，您可以通过以下两种方式部署腾讯云代码分析的Server和Web服务：

- [通过源代码](deploySever.html#通过源代码)

- [通过Docker-Compose](deploySever.md#通过docker-compose)

## 创建首个代码分析项目

成功部署并启动Server与Web服务后，您可以使用管理员凭据登陆到腾讯云代码分析平台，开始[创建您的首个代码分析项目](.)。

## 部署与配置客户端

在启动您的首个代码分析项目前，您需要在本地部署腾讯云代码分析的客户端。完成客户端的项目配置后，即可启动您的首个代码分析项目，并在腾讯云代码分析平台上查看您的分析结果。

您可以通过以下三种方式部署并使用腾讯云代码分析的客户端：

- [通过源代码](deployClient.md#通过源代码)

- [通过Docker-Compose](deployClient.md#通过docker-compose)

- [通过可执行文件](deployClient.md#通过可执行文件)


## 了解更多

更多关于腾讯云代码分析平台的使用指南和配置说明，参见[帮助文档](../guide/README.md)。