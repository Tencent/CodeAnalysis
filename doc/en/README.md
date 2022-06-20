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

### Repo Mirror

[https://git.code.tencent.com/Tencent_Open_Source/CodeAnalysis.git](https://git.code.tencent.com/Tencent_Open_Source/CodeAnalysis.git)

### What is TCA

Tencent Cloud Code Analysis (TCA for short, code-named **CodeDog** inside the company early) is a comprehensive platform for code analysis and issue tracking. TCA consist of three components, server, web and client. It integrates of a number of self-developed tools, and also supports dynamic integration of code analysis tools in various programming languages.

Code analysis is a technology, using lexical analysis, syntax analysis, control-flow analysis, data-flow analysis to make a comprehensive analysis of the code, so as to verify whether the code meets the requirements of normative, security, reliability, maintainability and other indicators.

Using TCA can help team find normative, structural, security vulnerabilities and other issues in the code, continuously monitor the quality of the project code and issue alerts. At the same time, TCA opens up APIs to support connection with upstream and downstream systems, so as to integrate code analysis capabilities, ensure code quality, and be more conducive to inheriting an excellent team code culture.

![组件图](https://tencent.github.io/CodeAnalysis/media/Components.png)

![流程图](https://tencent.github.io/CodeAnalysis/media/Flow.png)

### Experience

[Experience Link](http://tca.tencent.com)

### Getting Started

- [How to get start](./quickStarted/intro.md)
- [How to deploy server and web](./quickStarted/deploySever.md#通过源代码)
- [How to deploy server and web with docker-compose](./quickStarted/deploySever.md#通过docker-compose)
- [How to use client](./quickStarted/deployClient.md)
- [Deploy Q&A](./quickStarted/FAQ.md)

### Community

- WeChat official account:腾讯云静态分析
- QQ Group: 361791391
- [Discussion](https://github.com/Tencent/CodeAnalysis/discussions)
- [Wiki](https://github.com/Tencent/CodeAnalysis/wiki)
- [White Paper](https://github.com/Tencent/CodeAnalysis/tree/main/腾讯云代码分析白皮书.pdf)

### Changelogs

- Check our [Changelog](https://github.com/Tencent/CodeAnalysis/tree/main/CHANGELOG.md)

### Contributing

- Check out [CONTRIBUTING](https://github.com/Tencent/CodeAnalysis/tree/main/CONTRIBUTING.md) to see how to develop with TCA.
- [Tencent WeOpen Star Project](https://github.com/weopenprojects/WeOpen-Star/issues/19#issue-1228583868)（From May 2022 to September 2022）
- [Tencent Open Source Incentive Program](https://opensource.tencent.com/contribution) encourages the participation and contribution of developers. We look forward to your active participation.

### License

TCA is [MIT licensed](https://github.com/Tencent/CodeAnalysis/tree/main/LICENSE)
