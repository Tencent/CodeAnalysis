在实际的生产环境的部署过程中，团队的MySQL的管理员可能不会给到应用账号create等比较敏感的权限，这种情况下，我们可以通过手动迁移数据的方式起到和等同Django migrate的效果。

操作步骤：

1. 进入Server服务工作目录后（假设工作目录为 ``/data/CodeAnalysis/server/``，以下路径均为工作目录内的相对路径）
2. 在开发环境一个有全部权限的MySQL地址，初始化数据（MySQL版本运行版本：5.7）
    - 执行``vi ./scripts/config.sh``：填写一个有全部权限的MySQL数据库地址和Redis信息以及根据需要调整配置信息，主要的工程配置已提供默认值，字段说明可以查看[文档](../server/README.md)
    - 执行``bash ./scripts/deploy.sh init``：初始化DB、安装依赖和运行初始化脚本
    - 使用MySQLDump工具导出表结构与数据：``mysqldump -u user -p –databases codedog_main codedog_analysis codedog_file codedog_login > codedog_all.sql``
3. 在生产环境建数据库，详情见：``server/sql/init.sql``
4. 连接MySQL，导入数据：
    - 临时关闭外键检查: ``SET SESSION FOREIGN_KEY_CHECKS=0``，否则会因为数据中有外键关联导致导入失败
    - 导入表结构与数据: ``source /youdir/codedog_all.sql;``
    - 开启外键检查:  ``SET SESSION FOREIGN_KEY_CHECKS=1``
5. 启动服务: 直接执行 ``bash ./scripts/deploy.sh start``，无需执行 ``init``方法，否则会导致数据重复写入
