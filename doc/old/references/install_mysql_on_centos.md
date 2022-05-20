# 在CentOS安装MySQL指导
## 注意
本文档仅供参考，不适用于正式环境部署，正式环境建议使用专业的MySQL服务（比如[腾讯云的MySQL产品](https://cloud.tencent.com/product/cdb)）

## 环境
CentOS 7.3 版本

## 安装 mysql yum源

```bash
$ wget https://repo.mysql.com//mysql57-community-release-el7-11.noarch.rpm
$ yum localinstall mysql57-community-release-el7-11.noarch.rpm
```

安装成功后，查看MySQL版本：
```bash
$ yum repolist all | grep mysql
```
输出结果：
```bash
mysql-cluster-7.5-community/x86_64   MySQL Cluster 7.5 Community    禁用
mysql-cluster-7.5-community-source   MySQL Cluster 7.5 Community -  禁用
mysql-cluster-7.6-community/x86_64   MySQL Cluster 7.6 Community    禁用
mysql-cluster-7.6-community-source   MySQL Cluster 7.6 Community -  禁用
!mysql-connectors-community/x86_64   MySQL Connectors Community     启用:    221
mysql-connectors-community-source    MySQL Connectors Community - S 禁用
!mysql-tools-community/x86_64        MySQL Tools Community          启用:    135
mysql-tools-community-source         MySQL Tools Community - Source 禁用
mysql-tools-preview/x86_64           MySQL Tools Preview            禁用
mysql-tools-preview-source           MySQL Tools Preview - Source   禁用
mysql55-community/x86_64             MySQL 5.5 Community Server     禁用
mysql55-community-source             MySQL 5.5 Community Server - S 禁用
mysql56-community/x86_64             MySQL 5.6 Community Server     禁用
mysql56-community-source             MySQL 5.6 Community Server - S 禁用
!mysql57-community/x86_64            MySQL 5.7 Community Server     启用:    544
mysql57-community-source             MySQL 5.7 Community Server - S 禁用
mysql80-community/x86_64             MySQL 8.0 Community Server     禁用
mysql80-community-source             MySQL 8.0 Community Server - S 禁用
```

## 安装MySQL

```bash
$ yum install mysql-community-server
```
>1.如遇以下报错，可尝试运行`yum install mysql-community-server --nogpgcheck`安装  
> Public key for mysql-community-libs-compat-5.7.37-1.el7.x86_64.rpm is not installed  
> Failing package is: mysql-community-libs-compat-5.7.37-1.el7.x86_64    
> GPG Keys are configured as: file:///etc/pki/rpm-gpg/RPM-GPG-KEY-mysql  
>2.如遇以下报错，可执行`yum module disable mysql`后重试安装  
>All matches were filtered out by modular filtering for argument: mysql-community-serve  
>Error: Unable to find a match: mysql-community-server

## 配置MySQL服务
安装好的MySQL配置文件路径是``/etc/my.cnf``，这里可以根据需要调整，比如可以调整：
- datadir：MySQL存放数据的路径，如果有额外挂载磁盘，可以考虑指向相关路径

## 启动MySQL服务

```bash
$ systemctl start mysqld
```

确认MySQL正常启动

```bash
$ systemctl status mysqld
```

查看生成 MySQL root用户临时密码：
```bash
$ grep 'temporary password' /var/log/mysqld.log
```

### 修改root用户密码：

连接MySQL服务
```bash
$ mysql -uroot -p
# 输出上述查询到的临时密码
```

修改root用户的密码（下面是改成 ``Password@2021``，这里根据自行需要进行调整）：
```SQL
ALTER USER 'root'@'localhost' IDENTIFIED BY 'Password@2021';
```

## 参考文档
- [Installing MySQL on Linux Using the MySQL Yum Repository](https://dev.mysql.com/doc/refman/5.7/en/linux-installation-yum-repo.html)