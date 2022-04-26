## Hades简介

配合Zeus生成数据库使用的分析工具
该版本为beta版, 主要用于支持php安全问题的分析.
具体可以在平台选用 thinkphp安全分析 php安全分析两个规则包

### 单机命令

- -h 查看help
- analyze 分析命令
- inc_compile 增量解析代码目录文件
- -c 配置文件位置, 可参考demo.xml进行配置, 主要包含代目目录信息, 分析规则, 分析文件列表
- -l 语言，目前beta版支持php语言
- -d 输出debug级别日志
- -db zeus生成的数据库文件

### 规则列表
见 `server/projects/main/apps/scan_conf/management/commands/open_source/tca_ql_php_beta.json`