import{_ as d,r as c,o as n,c as t,a as l,b as e,d as a,w as o,e as s}from"./app-e552612a.js";const r={},h=l("h1",{id:"源代码快速部署",tabindex:"-1"},[l("a",{class:"header-anchor",href:"#源代码快速部署","aria-hidden":"true"},"#"),e(" 源代码快速部署")],-1),p=l("br",null,null,-1),u=s(`<h4 id="依赖环境" tabindex="-1"><a class="header-anchor" href="#依赖环境" aria-hidden="true">#</a> 依赖环境</h4><ul><li><p>系统环境</p><ul><li>Linux</li><li>最低配置：2核4G内存、100G硬盘存储空间</li></ul></li><li><p>环境准备</p><div class="custom-container tip"><p class="custom-container-title">TIP</p><p>TCA 一键部署脚本已封装好 Python、Mariadb、Redis 与 Nginx 安装步骤，<strong>无需自行安装</strong>，<strong>本地部署体验</strong>可按 <a href="#%E6%93%8D%E4%BD%9C%E8%AF%B4%E6%98%8E">操作说明</a> 内容直接进行部署操作。</p><p><strong>注意：生产环境建议使用专业的 MySQL、Redis 等服务</strong></p></div><ul><li><p>Python 3.7</p></li><li><p>MySQL 服务（MySQL5.7.8 以上版本或 Mariadb 10.5 以上版本）</p></li><li><p>Redis 服务（4.0版本以上）</p></li><li><p>Nginx 服务</p></li></ul></li><li><p>权限准备</p><ul><li>环境权限：安装 Server 依赖软件（python、nginx、yum 等软件包）需要使用 ROOT 权限 <ul><li>启动 Server 服务时可以使用非 ROOT 用户运行</li></ul></li><li>数据库权限：Server 服务执行数据库初始化需要依赖 <code>CREATE、ALTER、INDEX、DELETE、LOCK TABLES、SELECT、INSERT、REFERENCES、UPDATE</code> 权限</li></ul></li><li><p>端口使用：需要开放80端口的访问权限(80为TCA平台默认访问端口)，或调整 Web 服务默认的访问端口地址</p></li></ul><h4 id="操作说明" tabindex="-1"><a class="header-anchor" href="#操作说明" aria-hidden="true">#</a> 操作说明</h4><h5 id="首次启动操作" tabindex="-1"><a class="header-anchor" href="#首次启动操作" aria-hidden="true">#</a> 首次启动操作</h5><ol><li><p>进入 CodeAnalysis 工作目录（例如<code>~/CodeAnalysis</code>)，以下路径均为目录内的相对路径</p></li><li><p>安装基础软件与部署 TCA（可根据脚本选项确定是否要安装 Python、MySQL、Redis、Nginx 相关基础软件），执行</p></li></ol><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>$ bash ./quick_install.sh local deploy
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><p>执行该命令会做以下四个步骤：</p><ul><li><code>Install</code>：检测本地 Python3.7、Mariadb/MySQL、Redis 与 Nginx，如果不存在会提示安装</li><li><code>Init</code>：部署 TCA Server、Web与Client，并进行初始化</li><li><code>Start</code>：启动 TCA Server、Web与Client</li><li><code>Check</code>：检测 TCA 的运行状态</li></ul><p><strong>注意</strong>：在运行过程中，脚本会检测本地是否安装了相关基础软件（Python3.7、MySQL/Mariadb、Redis、Nignx），如果未安装会输出以下类似提示语：</p><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>Do you want to install [Redis] by this script?
Please enter:[Y/N]
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div></div></div><p>如果确定通过脚本安装可以输入<code>Y</code>。</p><ol start="3"><li>执行完成，无其他报错，即可登录：</li></ol>`,12),b={class:"custom-container tip"},_=l("p",{class:"custom-container-title"},"TIP",-1),g=l("code",null,"http://部署机器IP/",-1),m=l("br",null,null,-1),v=l("p",null,"默认平台登录账号/密码：CodeDog/admin",-1),E=l("p",null,"如部署过程中，已调整默认账号密码，请按照调整后的账号密码进行登录",-1),y=s(`<h5 id="更新操作" tabindex="-1"><a class="header-anchor" href="#更新操作" aria-hidden="true">#</a> 更新操作</h5><p><strong>1. 更新代码</strong></p><p><strong>2. 执行以下命令</strong></p><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>bash ./quick_install.sh local install tca  #更新相关配置
bash ./quick_install.sh local start  #启动服务（会自动关闭之前的服务）
bash ./quick_install.sh local check  #检查服务是否启动失败
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p><strong>注意：</strong><br><code>local install</code>命令行参数说明：<br> - <code>base</code>：安装 Python、Mariadb/MySQL、Redis 与 Nginx<br> - <code>tca</code>：初始化或更新 TCA Server、Web、Client 相关配置和数据<br> - <code>server</code>：初始化或更新 TCA Server 相关配置和数据<br> - <code>web</code>：初始化或更新 TCA Web 相关配置和数据<br> - <code>client</code>：初始化或更新 TCA Client 相关配置和数据<br> - 不填参数，默认会执行<code>base</code>、<code>tca</code>相关操作</p><h5 id="启动和停止服务" tabindex="-1"><a class="header-anchor" href="#启动和停止服务" aria-hidden="true">#</a> 启动和停止服务</h5><ul><li><p>启动所有服务：<code>bash ./quick_install.sh local start</code></p></li><li><p>启动Main相关服务：<code>bash ./quick_install.sh local start main</code></p><ul><li><code>local start</code>支持启动指定服务，如上述的启动Main服务，还支持<code>mysql/redis/analysis/file/login/scmproxy/nginx/client/all</code></li></ul></li><li><p>停止所有服务：<code>bash ./quick_install.sh local stop</code></p></li><li><p>停止Main相关服务：<code>bash ./quick_install.sh local stop main</code></p><ul><li><code>local stop</code>支持停止指定服务，如上述的停止Main服务，还支持<code>analysis/file/login/scmproxy/nginx/client/all</code></li></ul></li></ul><p><strong>注意：</strong></p><ol><li><p>启动时会自动关闭之前已经运行的服务</p></li><li><p><code>mysql</code>和<code>redis</code>默认会使用<code>systemctl</code>进行启动，如果<code>systemctl</code>无法使用，则会直接使用<code>nohup</code>方式运行相关服务</p></li></ol><h5 id="检查服务运行状态" tabindex="-1"><a class="header-anchor" href="#检查服务运行状态" aria-hidden="true">#</a> 检查服务运行状态</h5><p>检查服务运行状态：<code>bash ./quick_install.sh local check</code></p><ul><li>目前支持检查 server 与 web，暂不支持 client</li></ul><h5 id="获取服务输出日志" tabindex="-1"><a class="header-anchor" href="#获取服务输出日志" aria-hidden="true">#</a> 获取服务输出日志</h5><p>打印 TCA Server 各个服务的日志路径： <code>bash ./quick_install.sh local log</code></p>`,14);function A(C,x){const i=c("RouterLink");return n(),t("div",null,[h,l("p",null,[e("TCA提供部署脚本，支持一键式快速部署Server、Web、Client。"),p,e(" 脚本共提供三种部署方式："),a(i,{to:"/en/quickStarted/dockerDeploy.html"},{default:o(()=>[e("Docker部署(平台体验首推)")]),_:1}),e("、"),a(i,{to:"/en/quickStarted/dockercomposeDeploy.html"},{default:o(()=>[e("Docker-Compose部署")]),_:1}),e("、源码部署， 可根据您的具体使用场景任意选择其一进行部署。")]),u,l("div",b,[_,l("p",null,[e("至此，您已完成 TCA 平台部署，请在浏览器输入"),g,e("，点击立即体验，完成登录后即可开启您的腾讯云代码分析。"),m,e(" 平台内操作指引请查看："),a(i,{to:"/en/guide/%E5%BF%AB%E9%80%9F%E5%85%A5%E9%97%A8/%E5%BF%AB%E9%80%9F%E5%90%AF%E5%8A%A8%E4%B8%80%E6%AC%A1%E4%BB%A3%E7%A0%81%E5%88%86%E6%9E%90.html"},{default:o(()=>[e("快速启动一次代码分析")]),_:1})]),v,E]),y])}const S=d(r,[["render",A],["__file","codeDeploy.html.vue"]]);export{S as default};
