# 源码安装 Redis

## 运行环境
1. 基于x86_64的CentOS
2. 基于鲲鹏920（aarch64）的UOS V20
3. 基于飞腾2000（aarch64）的TencentOS Server

## 环境准备
安装编译打包需要的工具
```bash
$ yum install -y gcc make tcl wget
```

## 下载源码
```bash
$ wget http://download.redis.io/releases/redis-5.0.4.tar.gz
```

## 编译安装
```bash
# 解压
$ tar zvxf redis-5.0.4.tar.gz -C /usr/local/src

# 进入源码目录
$ cd /usr/local/src/redis-5.0.4

# 构建redis依赖库
$ cd deps; make -j4 hiredis jemalloc linenoise lua
$ cd ..

# 构建redis
$ make -j4
$ make install
$ make clean
```
安装后，可以在``/usr/local/src/redis-5.0.4/src``目录和``/usr/local/bin/``目录下找到``redis-server``与``redis-cli``两个文件

## 调整配置

```bash
$ cp /usr/local/src/redis/redis.conf  /etc/redis.conf
$ vim /usr/local/src/redis/redis.conf 
```

```bash
# 设置Redis密码
requirepass 123456

# 将 daemonize no 调整为 daemonize yes，将redis-server调整为默认后台启动
daemonize yes

# 配置日志
logfile '/var/log/redis/redis-server.log'
```

## 启动服务

```bash
$ redis-server /etc/redis.conf 
```

## 配置开机自动启动
```bash
$ vim /etc/systemd/system/redis.service
```
输入以下内容：
```
[Unit]
Description=redis-server
After=network.target

[Service]
Type=forking
ExecStart=/usr/local/bin/redis-server /etc/redis.conf
ExecStop=/usr/local/bin/redis-cli shutdown
Restart=always

PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

启动redis-server：
```bash
$ systemctl start redis
```

开机自动启动redis：
```bash
$ systemctl enable redis
```

## 参考文档
- [Redis官方文档](https://redis.io/topics/quickstart)