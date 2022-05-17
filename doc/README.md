---
home: true
title: 腾讯云代码分析文档
heroImage: /images/Logo.svg
actions:
  - text: 快速入门
    link: /zh/quickStarted/intro.html
    type: primary
  - text: 帮助文档
    link: /zh/guide/
    type: secondary
features:
  - title: 稳定可靠的架构
    details: 支持分布式云原生计算架构，支持灵活扩缩容，执行更快更稳定。
  - title: 多工具支持
    details: 已集成众多自研、知名开源工具等，采用分层分离架构，可满足团队快速自助管理工具。
  - title: 多语言覆盖
    details: 支持 Java/C++/Objective-C/C#/JavaScript/Python/Go/PHP 等数29种语言，覆盖常用编程语言。
  - title: 增量全量分析
    details: 增量分析快速发现问题，全量分析保证问题全覆盖。
  - title: 自定义指标
    details: 自定义代码标准，逐步优化代码。
  - title: 全方位质量报告
    details: 图形化可视报告，轻松监管代码综合质量趋势。
  - title: 全方位质量报告
    details: 图形化可视报告，轻松监管代码综合质量趋势。
  - title: 标准化 API 接口
    details: 提供标准化 API 接口，支持快速对接 DevOps 平台。
  - title: 分布式客户端
    details: 支持分布式客户端，包含 Linux、Mac、Windows，满足用户本地高频分析场景。
footer: MIT Licensed | Copyright © 1998-present Tencent. All Rights Reserved.
---

### 腾讯工蜂代码库镜像库

[https://git.code.tencent.com/Tencent_Open_Source/CodeAnalysis.git](https://git.code.tencent.com/Tencent_Open_Source/CodeAnalysis.git)

### 腾讯云代码分析简介

腾讯云代码分析（Tencent Cloud Code Analysis，简称TCA，内部曾用研发代号 **CodeDog** ）是集众多分析工具的云原生、分布式、高性能的代码综合分析跟踪平台，包含服务端、Web端和客户端三个组件，已集成一批自研工具，同时也支持动态集成业界各编程语言的分析工具。

代码分析是通过词法分析、语法分析、控制流、数据流分析等技术对程序代码进行扫描，对代码进行综合分析，验证代码是否满足规范性、安全性、可靠性、可维护性等指标的一种代码分析技术。

使用TCA可以帮助团队用代码分析技术查找代码中的规范性、结构性、安全漏洞等问题，持续监控项目代码质量并进行告警。同时TCA开放API，支持与上下游系统对接，从而集成代码分析能力，为代码质量提供保障，更有益于传承优良的团队代码文化。  

![组件图](https://tencent.github.io/CodeAnalysis/media/Components.png)

![流程图](https://tencent.github.io/CodeAnalysis/media/Flow.png)

### 体验

[官方版本](http://tca.tencent.com)

### 快速入门

- [快速入门](./zh/quickStarted/intro.md)
- [如何在本地部署Server与Web](./zh/quickStarted/deploySever.md#通过源代码)
- [如何通过Docker-Compose部署Server与Web](./zh/quickStarted/deploySever.md#通过docker-compose)
- [如何使用客户端](./zh/quickStarted/deployClient.md)
- [部署常见问题与解决方式](./zh/quickStarted/FAQ.md)

## 社区

- 微信公众号：「腾讯云静态分析」，关注并发送“进群”即可加入官方开源交流微信群
- QQ交流群：361791391  
- [GitHub讨论区](https://github.com/Tencent/CodeAnalysis/discussions)
- [Wiki](https://github.com/Tencent/CodeAnalysis/wiki)
- [腾讯云代码分析白皮书](https://github.com/Tencent/CodeAnalysis/tree/main/腾讯云代码分析白皮书.pdf)

## 更新日志

[Changelog](https://github.com/Tencent/CodeAnalysis/tree/main/CHANGELOG.md)

## 贡献

- 查看我们的[贡献说明](https://github.com/Tencent/CodeAnalysis/tree/main/CONTRIBUTING.md)
- [腾讯开源摘星计划2022](https://github.com/weopenprojects/WeOpen-Star/issues/19#issue-1228583868)（活动时间：2022年5月~12月）
- [腾讯开源激励计划](https://opensource.tencent.com/contribution) 鼓励开发者的参与和贡献，期待你的加入

### License

[MIT licensed](https://github.com/Tencent/CodeAnalysis/tree/main/LICENSE)
