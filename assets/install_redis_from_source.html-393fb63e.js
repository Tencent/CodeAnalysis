import{_ as s,r as a,o as d,c as n,a as e,b as r,d as l,e as c}from"./app-697cd87e.js";const v={},t=c(`<h1 id="源码安装-redis" tabindex="-1"><a class="header-anchor" href="#源码安装-redis" aria-hidden="true">#</a> 源码安装 Redis</h1><h2 id="运行环境" tabindex="-1"><a class="header-anchor" href="#运行环境" aria-hidden="true">#</a> 运行环境</h2><ol><li>基于x86_64的CentOS</li><li>基于鲲鹏920（aarch64）的UOS V20</li><li>基于飞腾2000（aarch64）的TencentOS Server</li></ol><h2 id="环境准备" tabindex="-1"><a class="header-anchor" href="#环境准备" aria-hidden="true">#</a> 环境准备</h2><p>安装编译打包需要的工具</p><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>yum install -y gcc make tcl wget
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h2 id="下载源码" tabindex="-1"><a class="header-anchor" href="#下载源码" aria-hidden="true">#</a> 下载源码</h2><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>wget http://download.redis.io/releases/redis-5.0.4.tar.gz
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h2 id="编译安装" tabindex="-1"><a class="header-anchor" href="#编译安装" aria-hidden="true">#</a> 编译安装</h2><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code># 解压
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
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>安装后，可以在<code>/usr/local/src/redis-5.0.4/src</code>目录和<code>/usr/local/bin/</code>目录下找到<code>redis-server</code>与<code>redis-cli</code>两个文件</p><h2 id="调整配置" tabindex="-1"><a class="header-anchor" href="#调整配置" aria-hidden="true">#</a> 调整配置</h2><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>cp /usr/local/src/redis/redis.conf  /etc/redis.conf
vim /usr/local/src/redis/redis.conf 
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div></div></div><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code># 设置Redis密码
requirepass 123456

# 将 daemonize no 调整为 daemonize yes，将redis-server调整为默认后台启动
daemonize yes

# 配置日志
logfile &#39;/var/log/redis/redis-server.log&#39;
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="启动服务" tabindex="-1"><a class="header-anchor" href="#启动服务" aria-hidden="true">#</a> 启动服务</h2><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>redis-server /etc/redis.conf 
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h2 id="配置开机自动启动" tabindex="-1"><a class="header-anchor" href="#配置开机自动启动" aria-hidden="true">#</a> 配置开机自动启动</h2><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>vim /etc/systemd/system/redis.service
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><p>输入以下内容：</p><div class="language-service line-numbers-mode" data-ext="service"><pre class="language-service"><code>[Unit]
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
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>启动redis-server：</p><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>systemctl start redis
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><p>开机自动启动redis：</p><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>systemctl enable redis
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h2 id="参考文档" tabindex="-1"><a class="header-anchor" href="#参考文档" aria-hidden="true">#</a> 参考文档</h2>`,25),u={href:"https://redis.io/topics/quickstart",target:"_blank",rel:"noopener noreferrer"};function o(h,m){const i=a("ExternalLinkIcon");return d(),n("div",null,[t,e("ul",null,[e("li",null,[e("a",u,[r("Redis官方文档"),l(i)])])])])}const g=s(v,[["render",o],["__file","install_redis_from_source.html.vue"]]);export{g as default};
