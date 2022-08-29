# 腾讯云代码分析介绍

**腾讯云代码分析**（Tencent Cloud Code Analysis，简称TCA，内部曾用研发代号 CodeDog ）是集众多分析工具的云原生、分布式、高性能的代码综合分析跟踪平台，包含**服务端、Web端、客户端**三个组件，已集成一批自研工具，同时也支持动态集成业界各编程语言的分析工具。

**代码分析**是通过词法分析、语法分析、控制流、数据流分析等技术对程序代码进行扫描，对代码进行综合分析，验证代码是否满足规范性、安全性、可靠性、可维护性等指标的一种代码分析技术。

使用TCA可以帮助团队用代码分析技术查找代码中的规范性、结构性、安全漏洞等问题，持续监控项目代码质量并进行告警。同时TCA开放API，支持与上下游系统对接，从而集成代码分析能力，为代码质量提供保障，更有益于传承优良的团队代码文化。  

![组件图](https://tencent.github.io/CodeAnalysis/media/Components.png)

![流程图](https://tencent.github.io/CodeAnalysis/media/Flow.png)

--- 

拉取 TCA [代码库](https://github.com/Tencent/CodeAnalysis) 后，首次体验推荐您使用[ Docker 快速部署](./dockerDeploy.md)方式快速搭建和体验腾讯云代码分析平台。  

如您更多环境需求，也可通过以下两种方式部署腾讯云代码分析平台：
- [通过 Docker-Compose 部署](./dockercomposeDeploy.md)
- [通过源代码部署](./codeDeploy.md)


