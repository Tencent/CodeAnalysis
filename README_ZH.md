<p align="center">
    <img src='https://tencent.github.io/CodeAnalysis/media/Logo.png' width="200"/>
    <br />
    <em>腾讯云代码分析</em>
</p>

## TCA

腾讯云代码分析（Tencent Cloud Code Analysis，简称TCA，内部曾用研发代号CodeDog）是集众多分析工具的云原生、分布式、高性能的代码综合分析跟踪平台，包含服务端、Web端和客户端三个组件，已集成一批自研工具，同时也支持动态集成业界各编程语言的分析工具。

代码分析是通过词法分析、语法分析、控制流、数据流分析等技术对程序代码进行扫描，对代码进行综合分析，验证代码是否满足规范性、安全性、可靠性、可维护性等指标的一种代码分析技术。

使用TCA可以帮助团队用代码分析技术查找代码中的规范性、结构性、安全漏洞等问题，持续监控项目代码质量并进行告警。同时TCA开放API，支持与上下游系统对接，从而集成代码分析能力，为代码质量提供保障，更有益于传承优良的团队代码文化。

![组件图](https://tencent.github.io/CodeAnalysis/media/Components.png)

![流程图](https://tencent.github.io/CodeAnalysis/media/Flow.png)

## 体验

[官方体验申请链接](https://cloud.tencent.com/apply/p/44ncv4hzp1)

## 关键功能

1. **语言支持**：支持 Java/C++/Objective-C/C#/JavaScript/Python/Go/PHP 等数十种语言，覆盖常用编程语言。
2. **代码检查**：通过代码分析精准跟踪管理发现的代码质量缺陷、代码规范问题、代码安全漏洞、无效代码等。目前已集成众多自研、知名开源分析工具，并采用了分层分离架构，可以支持团队快速自助管理工具。
3. **代码度量**：支持代码圈复杂度、代码重复率和代码统计三个维度对代码进行综合度量。
4. **DevOps集成**：客户端通过命令行启动方式，通过标准API接口对接上下游系统，可以快速对接各个DevOps调度体系。

## 快速入门

- [快速入门](GettingStart(快速入门).md)
- [如何在本地部署Server与Web](doc/deploy.md)
- [如何通过Docker-Compose部署Server与Web](doc/deploy_dc.md)
- [如何使用客户端](doc/client.md)
- [部署常见问题与解决方式](doc/Q&A.md)

## 社区

- QQ交流群：361791391
- [GitHub讨论区](https://github.com/Tencent/CodeAnalysis/discussions)
- [Wiki](https://github.com/Tencent/CodeAnalysis/wiki)
- [腾讯云代码分析白皮书](腾讯云代码分析白皮书.pdf)

## 更新

[Changelog](CHANGELOG.md)

## 贡献

- 查看我们的[贡献说明](CONTRIBUTING.md)
- [腾讯开源激励计划](https://opensource.tencent.com/contribution) 鼓励开发者的参与和贡献，期待你的加入

## 许可

TCA 使用 [MIT 许可证](LICENSE)
