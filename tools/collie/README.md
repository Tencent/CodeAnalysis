# Collie(测试版)
一款多语言非编译型静态代码分析工具，支持C/C++/ObjectiveC/C#/CSS/Dart/Java/JavaScript/TypeScript/Kotlin/Lua/PHP/Python/Go/Ruby/Scala/Swift等17门语言。

## 准备
- 部署TCA Server；
- 部署[CLS](../../server/cls/README.md#部署)，启动License校验功能；
- 在TCA Client的[config.ini](../../client/config.ini)中设置LICENSE_CONFIG信息。

## 使用
- 在TCA上创建对应的分析项目；
- 在分析项目对应的分析方案中添加Collie的规则；
- 启动分析任务，等待任务执行完成，既可看到对应的问题。
