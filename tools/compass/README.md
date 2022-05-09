# 罗盘Compass(测试版)
一款依赖组件分析工具，支持：
- 分析项目的依赖组件；
- 分析依赖组件是否存在漏洞等问题。

## 准备
- 部署TCA Server；
- 部署[CLS](../../server/cls/README.md#部署)，启动License校验功能；
- 在TCA Client的[config.ini](../../client/config.ini)中设置LICENSE_CONFIG信息。

## 使用
- 在TCA上创建对应的分析项目；
- 在分析项目对应的分析方案中添加Compass的规则；
- 启动分析任务，等待任务执行完成，既可看到对应的问题。
