# Ubuntu安装Python3.7文档
> 注：当前Ubuntu版本为18.04

## 下载Python源码包
```bash
$ wget https://www.python.org/ftp/python/3.7.12/Python-3.7.12.tgz
```
## 安装前准备
安装依赖组件
```bash
$ apt-get update
$ apt-get install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev wget libbz2-dev tk-dev gcc make
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
# 链接构建产出的Python可执行文件到/usr/local/bin目录
$ ln -s /usr/local/python3/bin/python3 /usr/local/bin/python
# 链接构建产出的pip3可执行文件到/usr/local/bin目录
$ ln -s /usr/local/python3/bin/pip3 /usr/local/bin/pip
# 链接构建产出的Python动态库
$ ln -s /usr/local/python3/lib/libpython3.7m.so.1.0 /usr/lib/libpython3.7m.so.1.0
# 配置动态库
$ ldconfig
```

## 检查
检查Python版本是否安装成功
```
$ python --version
Python 3.7.12  # 正常输出，表示安装成功
```

注：
1. 链接到/usr/local/bin/目录不会影响系统软件
2. 一般情况下，PATH配置是先``/usr/local/bin``再``/usr/bin``
3. 检查``python -v``输出结果是否为``Python 3.7.12``版本，如果不是该版本，可能影响后续依赖安装和服务运行


## pypi下载源配置
pip默认是到``pypi``官方源下载第三方依赖包，下载速度可能会比较慢，可以考虑调整为腾讯云的``pypi``下载源，调整方式：

```bash
$ mkdir ~/.pip/
$ echo "[global]\nindex-url = https://mirrors.cloud.tencent.com/pypi/simple" >> ~/.pip/pip.conf
```