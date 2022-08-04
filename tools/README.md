用于统一存放工具（可外链仓库）

## **注意**
以下部分独立工具需要申请授权，具体操作可以参考[CLS使用文档](../server/cls/README.md).

## [TCA-Collie(测试版)](https://github.com/TCATools/collie)
一款多语言非编译型静态代码分析工具，支持C/C++/ObjectiveC/C#/CSS/Dart/Java/JavaScript/TypeScript/Kotlin/Lua/PHP/Python/Go/Ruby/Scala/Swift等17门语言，需要申请License。

## [TCA-Compass罗盘(测试版)](https://github.com/TCATools/compass)
一款依赖组件分析工具，支持：
- 分析项目的依赖组件；
- 分析依赖组件是否存在漏洞等问题。

需要申请License。

## TCA-Loong龙(测试版)
Java/Kotlin API和函数调用链分析工具，需要申请License。

### 如何在TCA上使用
在TCA Server上勾选以下工具规则：
- [JAAF](../server/projects/main/apps/scan_conf/management/commands/open_source/jaaf.json#L4)
- [JAFC](../server/projects/main/apps/scan_conf/management/commands/open_source/jafc.json#L4)
- [JAFF](../server/projects/main/apps/scan_conf/management/commands/open_source/jaff.json#L4)

### 底层命令行工具
涉及到的底层命令行工具有：
- [TCA-Loong龙(测试版)](https://github.com/TCATools/loong)

## TCA-Loong_Beta龙(测试版)
Java/Kotlin API和函数调用链分析工具，无需申请License。

### 如何在TCA上使用
在TCA Server上勾选以下工具规则：
- [JAFCBeta](../server/projects/main/apps/scan_conf/management/commands/open_source/jafc_beta.json#L4)
- [JAFFBeta](../server/projects/main/apps/scan_conf/management/commands/open_source/jaff_beta.json#L4)

### 底层命令行工具
涉及到的底层命令行工具有：
- [TCA-Loong_Beta龙(测试版)](https://github.com/TCATools/loong_beta)

## TCA-QL(测试版)
一款静态代码分析的解析端，开源测试版仅开放在linux上运行，需要申请License。

### 如何在TCA上使用
在TCA Server上勾选以下工具规则：
- [TCA_QL_CPP](../server/projects/main/apps/scan_conf/management/commands/open_source/tca_ql_cpp.json#L4)
- [TCA_QL_Go](../server/projects/main/apps/scan_conf/management/commands/open_source/tca_ql_go.json#L4)
- [TCA_QL_PHP](../server/projects/main/apps/scan_conf/management/commands/open_source/tca_ql_php.json#L4)
- [TCA_QL_Python](../server/projects/main/apps/scan_conf/management/commands/open_source/tca_ql_python.json#L4)

### 底层命令行工具
涉及到的底层命令行工具有：
- [TCA-Zeus(测试版)](https://github.com/TCATools/TCA-Zeus-linux)
- [TCA-Hades(测试版)](https://github.com/TCATools/TCA-Hades-linux)

### TCA-QL_Beta(测试版)
一款静态代码分析的解析端，开源测试版仅支持PHP语言，开源测试版仅开放在linux上运行，无需申请License。

### 如何在TCA上使用
在TCA Server上勾选以下工具规则：
- [TCA_QL_Beta_PHP](../server/projects/main/apps/scan_conf/management/commands/open_source/tca_ql_php_beta.json#L4)

### 底层命令行工具
涉及到的底层命令行工具有：
- [TCA-Zeus_Beta(测试版)](https://github.com/TCATools/Zeus_Beta)
- [TCA-Hades_Beta(测试版)](https://github.com/TCATools/Hades_Beta)

## [TCA-0Day_Checker(测试版)](https://github.com/TCATools/codedog_0Day_checker)
用于一些爆出高危漏洞的组件检查，主要用于前段时间的log4j检查，支持自定义规则用于检查其他组件，无需申请License。

### 如何在TCA上使用
在TCA Server上勾选以下工具规则：
- [0DayChecker](../server/projects/main/apps/scan_conf/management/commands/open_source/0daychecker.json#L4)
