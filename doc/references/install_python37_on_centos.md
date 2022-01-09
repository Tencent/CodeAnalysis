# 在CentOS安装Python3.7指导
## 下载Python源码包
```bash
$ wget https://www.python.org/ftp/python/3.7.12/Python-3.7.12.tgz
```
## 安装前准备
安装依赖组件
```bash
$ yum -y install wget zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gcc make libffi-devel xz-devel
```

## 解压安装
```bash
# 解压到/usr/local/src目录
$ tar zvxf Python-3.7.12.tgz -C /usr/local/src
$ cd /usr/local/src/Python-3.7.12
# 编译前配置
$ ./configure prefix=/usr/local/python3 --enable-shared
# 编译构建
$ make -j8
# 安装Python
$ make install
# 清理编译产出的中间文件
$ make clean
# 删除系统内置的python2的软连接
rm /usr/bin/python
# 链接构建产出的Python可执行文件到/usr/local/bin目录
$ ln -s /usr/local/python3/bin/python3 /usr/local/bin/python
# 链接构建产出的pip3可执行文件到/usr/local/bin目录
$ ln -s /usr/local/python3/bin/pip3 /usr/local/bin/pip
# 链接构建产出的Python动态库
$ ln -s /usr/local/python3/lib/libpython3.7m.so.1.0 /usr/lib/libpython3.7m.so.1.0
# 配置动态库
$ ldconfig
```

注：
1. 链接到/usr/local/bin/目录不会影响系统软件（比如yum）的使用，因为 yum 工具指定的Python路径是``/usr/bin/python``
2. 一般情况下，PATH配置是先``/usr/local/bin``再``/usr/bin``

