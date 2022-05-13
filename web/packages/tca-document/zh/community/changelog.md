# 更新日志

## V1.2.0 (2022-4-27)
### Features
- 【Web端】增加工具管理
- 【工具】增加logback检查的安全规则
- 【服务端】增加TCA server&web 一键部署脚本
- 【服务端】删除main部分异步任务；调整server nginx启动位置
- 【服务端】增加server健康监测
### Docs
- 完善部署和Q&A文档
- 上传工具列表


## V1.1.3 (2022-4-18)
### Features
- 【工具】上传开源合规检查规则
- 【工具】新增PHP安全相关规则
- 【服务端】上线license鉴权
- 【客户端】支持对工具license校验
### Docs
- 更新文档内的工具默认路径
- 增加任务分布式执行能力操作文档
- 增加PR操作流程


## V1.1.2 (2022-4-2)
### Features
- 【服务端】优化部署构建脚本 
### Docs
- 简化前端部署脚本&文档 
- 优化指引文档


## V1.1.1 (2022-3-31)
### Features
- 【工具】增加0daychecker工具
- 【工具】增加Log4j、LogBack漏洞检查规则包

### Docs
- 完善部署文档说明，推荐使用Docker-Compose 2.3.3版本

## V1.1.0 (2022-3-29)
### Features
- 【客户端】client支持arm64架构执行环境
- 【客户端】client新增分布式节点模式
- 【客户端】修改参数isTotal(是否开启全量扫描)判断方式及参数startCommand（启动客户端命令）拼接方式
- 【服务端】支持任务分布式下发
- 【服务端】完善基于minio的文件存储配置
- 【Web端】调整文件资源引用地址
- 【Web端】web模块部署脚本问题修复及优化
- 【Web端】增加管理后台、增加在线分析
- 【Web端】调整前端部署脚本，支持传递nginx配置地址、前端资源部署地址
### Bugfixes
- Jenkins插件命令拼装逻辑修正
### Docs
- 调整pypi下载失败提示
- 调整前端部署文档及脚本
- 更新License



## V1.0.1 (2022-03-01)
### Features
- feat: 【服务端】调整代码库登记ssh url链接格式适配  
- feat: 【工具】上线支持PHP安全工具-Rips  
- feat: 【工具】调整androidlint部分规则描述  
- feat: 【客户端】上线Jenkins插件  
- feat: 【客户端】增加工具拉取可选配置项  
- feat: 【客户端】支持在命令行参数中输入团队编号和项目名称  
- feat: 【客户端】限制PYTHON_VERSION环境变量可选值  
- feat: 【客户端】增加在docker中快速使用client的方式  

### Bugfixes
- fix: 【服务端】补充缺失的依赖  
- fix: 【Web端】修复下载codedog.ini失败提示
 
### Docs
- doc: 上线部署文档Q&A  
- doc: 优化部署文档、帮助文档说明  
- doc: 增加产品白皮书  
- doc: 补充redis和nginx源码安装参考文档



## V1.0.0
初始发布