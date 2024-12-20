import{_ as e,o as n,c as i,e as l}from"./app-697cd87e.js";const s={},d=l(`<h1 id="在-centos-安装-python3-7" tabindex="-1"><a class="header-anchor" href="#在-centos-安装-python3-7" aria-hidden="true">#</a> 在 CentOS 安装 Python3.7</h1><h2 id="下载python源码包" tabindex="-1"><a class="header-anchor" href="#下载python源码包" aria-hidden="true">#</a> 下载Python源码包</h2><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>wget https://www.python.org/ftp/python/3.7.12/Python-3.7.12.tgz
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h2 id="安装前准备" tabindex="-1"><a class="header-anchor" href="#安装前准备" aria-hidden="true">#</a> 安装前准备</h2><p>安装依赖组件</p><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>yum -y install wget zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gcc make libffi-devel xz-devel
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h2 id="解压安装" tabindex="-1"><a class="header-anchor" href="#解压安装" aria-hidden="true">#</a> 解压安装</h2><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code># 解压到/usr/local/src目录
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
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="检查" tabindex="-1"><a class="header-anchor" href="#检查" aria-hidden="true">#</a> 检查</h2><p>检查Python版本是否安装成功</p><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>$ python --version
Python 3.7.12  # 正常输出，表示安装成功
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div></div></div><p>注：</p><ol><li>链接到/usr/local/bin/目录不会影响系统软件（比如yum）的使用，因为 yum 工具指定的Python路径是<code>/usr/bin/python</code></li><li>一般情况下，PATH配置是先<code>/usr/local/bin</code>再<code>/usr/bin</code></li><li>检查<code>python -v</code>输出结果是否为<code>Python 3.7.12</code>版本，如果不是该版本，可能影响后续依赖安装和服务运行</li></ol><h2 id="pypi下载源配置" tabindex="-1"><a class="header-anchor" href="#pypi下载源配置" aria-hidden="true">#</a> pypi下载源配置</h2><p>pip默认是到<code>pypi</code>官方源下载第三方依赖包，下载速度可能会比较慢，可以考虑调整为腾讯云的<code>pypi</code>下载源，调整方式：</p><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>mkdir ~/.pip/
echo &quot;extra-index-url = https://mirrors.cloud.tencent.com/pypi/simple&quot; &gt;&gt; ~/.pip/pip.conf
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="一键安装脚本" tabindex="-1"><a class="header-anchor" href="#一键安装脚本" aria-hidden="true">#</a> 一键安装脚本</h2><p>以下脚本内容是上面的步骤集合，省去了复制粘贴的重复动作。</p><ol><li>创建文件 <code>install_py37.sh</code>，写入以下 shell 脚本</li><li>赋予执行权限，<code>chmox +x install_py37.sh</code></li><li>执行脚本，<code>./install_py37.sh</code></li></ol><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>#!/bin/env bash

## 下载 Python 源码，如果已下载源码在脚本当前目录下，可注释跳过下载步骤
wget https://www.python.org/ftp/python/3.7.12/Python-3.7.12.tgz

## 安装编译依赖组件
yum -y install wget zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gcc make libffi-devel xz-devel

## 解压安装
# 解压到/usr/local/src目录
tar zvxf Python-3.7.12.tgz -C /usr/local/src
cd /usr/local/src/Python-3.7.12
# 编译前配置
./configure prefix=/usr/local/python3 --enable-shared
# 编译构建
make -j8
# 安装Python
make install
# 清理编译产出的中间文件
make clean
# 链接构建产出的Python可执行文件到/usr/local/bin目录
ln -s /usr/local/python3/bin/python3 /usr/local/bin/python
# 链接构建产出的pip3可执行文件到/usr/local/bin目录
ln -s /usr/local/python3/bin/pip3 /usr/local/bin/pip
# 链接构建产出的Python动态库
ln -s /usr/local/python3/lib/libpython3.7m.so.1.0 /usr/lib/libpython3.7m.so.1.0
# 配置动态库
ldconfig

## 检查Python版本是否安装成功
echo -e &quot;\\033[1;42;37m[$(date &quot;+%Y/%m/%d %H:%M:%S&quot;)] [Check]: 检查Python版本\\033[0m&quot;
python --version
echo -e &quot;\\033[1;42;37m[$(date &quot;+%Y/%m/%d %H:%M:%S&quot;)] [Check]: 检查Python版本\\033[0m&quot;

## pypi下载源配置
mkdir ~/.pip/
echo &quot;extra-index-url = https://mirrors.cloud.tencent.com/pypi/simple&quot; &gt;&gt; ~/.pip/pip.conf
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div>`,20),a=[d];function r(c,o){return n(),i("div",null,a)}const t=e(s,[["render",r],["__file","install_python37_on_centos.html.vue"]]);export{t as default};
