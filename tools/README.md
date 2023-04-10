用于统一存放工具（可外链仓库）

## **注意**
以下部分独立工具需要申请授权，具体操作可以参考[CLS使用文档](https://tencent.github.io/CodeAnalysis/zh/quickStarted/enhanceDeploy.html).

## [TCA-Armory(测试版)](https://github.com/TCATools/TCA-Armory)
一款多功能的多语言静态代码分析工具，需申请License。
## 功能
- 支持Objective-C/C++代码规范检查；
- 支持分析项目的依赖组件；
- 支持分析依赖组件是否存在漏洞等问题；
- 支持Java/Kotlin API和函数调用链分析；
- 支持代码安全、空指针检查、内存泄漏等规则。

### 如何在TCA上使用
在TCA上勾选名称以 `TCA-Armory` 开头的工具的规则。

## TCA-Loong_Beta龙(测试版)
Java/Kotlin API和函数调用链分析工具，无需申请License。

### 如何在TCA上使用
在TCA上勾选以下工具规则：
- [JAFCBeta](../server/projects/main/apps/scan_conf/management/commands/open_source/jafc_beta.json#L4)
- [JAFFBeta](../server/projects/main/apps/scan_conf/management/commands/open_source/jaff_beta.json#L4)

### 底层命令行工具
涉及到的底层命令行工具有：
- [TCA-Loong_Beta龙(测试版)](https://github.com/TCATools/loong_beta)

## [TCA-0Day_Checker(测试版)](https://github.com/TCATools/codedog_0Day_checker)
用于一些爆出高危漏洞的组件检查，主要用于前段时间的log4j检查，支持自定义规则用于检查其他组件，无需申请License。

### 如何在TCA上使用
在TCA上勾选以下工具规则：
- [0DayChecker](../server/projects/main/apps/scan_conf/management/commands/open_source/0daychecker.json#L4)
