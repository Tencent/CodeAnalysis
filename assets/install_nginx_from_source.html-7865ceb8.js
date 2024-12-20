import{_ as i,r as s,o as d,c as a,a as n,b as l,d as r,e as c}from"./app-697cd87e.js";const v={},u=c(`<h1 id="源码安装-nginx" tabindex="-1"><a class="header-anchor" href="#源码安装-nginx" aria-hidden="true">#</a> 源码安装 Nginx</h1><h2 id="运行环境" tabindex="-1"><a class="header-anchor" href="#运行环境" aria-hidden="true">#</a> 运行环境</h2><ol><li>基于x86_64的CentOS</li><li>基于aarch64（鲲鹏920）的UOS V20</li><li>基于aarch64（飞腾2000）的TencentOS Server</li></ol><h2 id="环境准备" tabindex="-1"><a class="header-anchor" href="#环境准备" aria-hidden="true">#</a> 环境准备</h2><p>安装编译打包需要的工具</p><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>yum -y install gcc zlib-devel pcre-devel bzip2-devel openssl-devel readline-devel
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><blockquote><p>Ubuntu: <code>apt install gcc libssl-dev zlib1g-dev libpcre3-dev libbz2-dev libreadline-dev</code></p></blockquote><h2 id="下载源码" tabindex="-1"><a class="header-anchor" href="#下载源码" aria-hidden="true">#</a> 下载源码</h2><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>wget http://nginx.org/download/nginx-1.20.2.tar.gz
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h2 id="解压安装" tabindex="-1"><a class="header-anchor" href="#解压安装" aria-hidden="true">#</a> 解压安装</h2><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code># 解压
$ tar zvxf nginx-1.20.2.tar.gz -C /usr/local/src

# 进入源码目录
$ cd /usr/local/src/nginx-1.20.2

# 配置
$ ./configure \\
--sbin-path=/usr/local/nginx/nginx \\
--conf-path=/etc/nginx/nginx.conf \\
--pid-path=/run/nginx.pid \\
--with-stream \\
--with-http_ssl_module --with-http_v2_module --with-http_auth_request_module

# 构建nginx
$ make -j4
$ make install
$ make clean

# 建立软链
$ ln -s /usr/local/nginx/nginx /usr/local/bin/nginx
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="添加nginx配置文件" tabindex="-1"><a class="header-anchor" href="#添加nginx配置文件" aria-hidden="true">#</a> 添加nginx配置文件</h2><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>mkdir /etc/nginx/conf.d/
vi /etc/nginx/nginx.conf
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div></div></div><p>检查<code>nginx.conf</code>配置文件：</p><ol><li>检查<code>pid /run/nginx.pid</code>，如果缺失或被注释则加上，加上位置如下所示：</li><li>检查是否缺失这一行<code>include conf.d/*.conf;</code>，如果缺失则加上，加上位置如下所示：</li></ol><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code># ...省略内容
#pid        logs/nginx.pid;  # 默认有的
pid         /run/nginx.pid;

events {
    # ...省略内容
}

# ...省略内容

http {
    # ...省略内容
    # 
    include conf.d/*.conf;    
    server {
        # ...省略内容
    }
}

</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>后续可以将nginx配置文件放置到<code>/etc/nginx/conf.d/</code>目录下</p><h2 id="配置开机自动启动" tabindex="-1"><a class="header-anchor" href="#配置开机自动启动" aria-hidden="true">#</a> 配置开机自动启动</h2><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>vim /usr/lib/systemd/system/nginx.service
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><p>输入以下内容：</p><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>[Unit]
Description=The nginx HTTP and reverse proxy server
After=network-online.target remote-fs.target nss-lookup.target
Wants=network-online.target

[Service]
Type=forking
PIDFile=/run/nginx.pid
# Nginx will fail to start if /run/nginx.pid already exists but has the wrong
# SELinux context. This might happen when running \`nginx -t\` from the cmdline.
# https://bugzilla.redhat.com/show_bug.cgi?id=1268621
ExecStartPre=/bin/rm -f /run/nginx.pid
ExecStartPre=/usr/local/bin/nginx -t
ExecStart=/usr/local/bin/nginx
ExecReload=/usr/local/bin/nginx -s reload
ExecStop=/usr/local/bin/nginx -s stop
KillSignal=SIGQUIT
TimeoutStopSec=5
KillMode=process
PrivateTmp=true

[Install]
WantedBy=multi-user.target
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>启动nginx：</p><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>systemctl start nginx
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><p>开机自动启动nginx：</p><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>systemctl enable nginx
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h2 id="参考文档" tabindex="-1"><a class="header-anchor" href="#参考文档" aria-hidden="true">#</a> 参考文档</h2>`,26),t={href:"https://docs.nginx.com/nginx/admin-guide/installing-nginx/installing-nginx-open-source/#downloading-the-sources",target:"_blank",rel:"noopener noreferrer"};function o(b,m){const e=s("ExternalLinkIcon");return d(),a("div",null,[u,n("ul",null,[n("li",null,[n("a",t,[l("Nginx官方文档"),r(e)])])])])}const g=i(v,[["render",o],["__file","install_nginx_from_source.html.vue"]]);export{g as default};
