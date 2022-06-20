# 在CentOS安装Redis指导
## 注意
本文档仅供参考，不适用于正式环境部署，正式环境建议使用专业的Redis服务（比如[腾讯云的Redis产品](https://cloud.tencent.com/product/crs)）

## 环境
CentOS 7.3 版本

## yum 安装 redis
```bash
$ yum install redis
```
注：安装redis可能会出现"no package redis available"的错误提示，请执行``yum install epel-release``后重试redis安装命令。

## 修改redis密码
```bash
$ vi /etc/redis.conf

# 找到 requirepass foobared
# 复制一行并根据自己需要调整密码，比如
requirepass tca123
```

## 启动redis

```bash
$ systemctl start redis
```

查看redis运行状态
```bash
$ systemctl status redis
```

## 访问redis
```bash
$ redis-cli

127.0.0.1:6379> auth tca123
OK # 鉴权通过
```
