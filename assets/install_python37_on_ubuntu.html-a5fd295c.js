import{_ as e,o as n,c as i,e as a}from"./app-697cd87e.js";const l={},s=a(`<h1 id="在-ubuntu-安装-python3-7" tabindex="-1"><a class="header-anchor" href="#在-ubuntu-安装-python3-7" aria-hidden="true">#</a> 在 Ubuntu 安装 Python3.7</h1><blockquote><p>注：当前Ubuntu版本为18.04</p></blockquote><h2 id="下载python源码包" tabindex="-1"><a class="header-anchor" href="#下载python源码包" aria-hidden="true">#</a> 下载Python源码包</h2><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>wget https://www.python.org/ftp/python/3.7.12/Python-3.7.12.tgz
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h2 id="安装前准备" tabindex="-1"><a class="header-anchor" href="#安装前准备" aria-hidden="true">#</a> 安装前准备</h2><p>安装依赖组件</p><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>apt-get update
apt-get install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev wget libbz2-dev tk-dev gcc make
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="解压安装" tabindex="-1"><a class="header-anchor" href="#解压安装" aria-hidden="true">#</a> 解压安装</h2><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code># 解压到/usr/local/src目录
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
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div></div></div><p>注：</p><ol><li>链接到/usr/local/bin/目录不会影响系统软件</li><li>一般情况下，PATH配置是先<code>/usr/local/bin</code>再<code>/usr/bin</code></li><li>检查<code>python -v</code>输出结果是否为<code>Python 3.7.12</code>版本，如果不是该版本，可能影响后续依赖安装和服务运行</li></ol><h2 id="pypi下载源配置" tabindex="-1"><a class="header-anchor" href="#pypi下载源配置" aria-hidden="true">#</a> pypi下载源配置</h2><p>pip默认是到<code>pypi</code>官方源下载第三方依赖包，下载速度可能会比较慢，可以考虑调整为腾讯云的<code>pypi</code>下载源，调整方式：</p><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>mkdir ~/.pip/
echo &quot;[global]\\nindex-url = https://mirrors.cloud.tencent.com/pypi/simple&quot; &gt;&gt; ~/.pip/pip.conf
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div></div></div>`,17),d=[s];function r(c,o){return n(),i("div",null,d)}const u=e(l,[["render",r],["__file","install_python37_on_ubuntu.html.vue"]]);export{u as default};
