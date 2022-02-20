# 源码安装 Nginx

## 运行环境
1. 基于x86_64的CentOS
2. 基于aarch64（鲲鹏920）的UOS V20
3. 基于aarch64（飞腾2000）的TencentOS Server

## 环境准备
安装编译打包需要的工具
```bash
$ yum -y install gcc zlib-devel pcre-devel bzip2-devel openssl-devel readline-devel
```

## 下载源码
```bash
$ wget http://nginx.org/download/nginx-1.20.2.tar.gz
```

## 解压安装
```bash
# 解压
$ tar zvxf nginx-1.20.2.tar.gz -C /usr/local/src

# 进入源码目录
$ cd /usr/local/src/nginx-1.20.2

# 配置
$ ./configure \
--sbin-path=/usr/local/nginx/nginx \
--conf-path=/usr/local/nginx/nginx.conf \
--pid-path=/usr/local/nginx/nginx.pid \
--with-stream \
--with-http_ssl_module --with-http_v2_module --with-http_auth_request_module

# 构建nginx
$ make -j4
$ make install
$ make clean

# 建立软链
$ ln -s /usr/local/nginx/nginx /usr/local/bin/nginx
```
## 添加nginx配置文件

```bash
$ mkdir /usr/local/nginx/conf.d/
$ vi /usr/local/nginx/nginx.conf
```

检查``nginx.conf``配置文件，检查是否缺失这一行``include conf.d/*.conf;``，如果缺失则加上，加上位置如下所示：

```bash
http {
    # ...
    # 
    include conf.d/*.conf;
    
    server {
        # ...
    }
}

```
后续可以将nginx配置文件放置到``/usr/local/nginx/conf.d/``目录下


## 配置开机自动启动
```
vim /usr/lib/systemd/system/nginx.service
```

输入以下内容：
```
[Unit]
Description=The nginx HTTP and reverse proxy server
After=network-online.target remote-fs.target nss-lookup.target
Wants=network-online.target

[Service]
Type=forking
PIDFile=/run/nginx.pid
# Nginx will fail to start if /run/nginx.pid already exists but has the wrong
# SELinux context. This might happen when running `nginx -t` from the cmdline.
# https://bugzilla.redhat.com/show_bug.cgi?id=1268621
ExecStartPre=/usr/bin/rm -f /run/nginx.pid
ExecStartPre=/usr/local/bin/nginx -t
ExecStart=/usr/local/bin/nginx
ExecReload=/usr/local/bin/nginx -s reload
KillSignal=SIGQUIT
TimeoutStopSec=5
KillMode=process
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

启动nginx：

```bash
$ nginx
```

开机自动启动nginx：

```bash
$ systemctl enable nginx
```

## 参考文档
- [Nginx官方文档](https://docs.nginx.com/nginx/admin-guide/installing-nginx/installing-nginx-open-source/#downloading-the-sources)