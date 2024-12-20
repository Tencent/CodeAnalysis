import{_ as e,o as n,c as i,e as a}from"./app-697cd87e.js";const d={},s=a(`<h1 id="基于minio部署文件服务器" tabindex="-1"><a class="header-anchor" href="#基于minio部署文件服务器" aria-hidden="true">#</a> 基于MinIO部署文件服务器</h1><p>TCA的<code>file</code>服务支持对接<code>MinIO</code>作为底层存储，将文件转发到已部署的MinIO平台上进行持久化存储</p><h2 id="本地部署" tabindex="-1"><a class="header-anchor" href="#本地部署" aria-hidden="true">#</a> 本地部署</h2><blockquote><p>注意：如果之前已经使用本地进行存储，切换为MinIO后，之前已经上传的文件只能到服务部署的目录<code>server/projects/file/data</code>查看，不支持通过页面进行下载</p></blockquote><h3 id="前置步骤" tabindex="-1"><a class="header-anchor" href="#前置步骤" aria-hidden="true">#</a> 前置步骤</h3><p>获取MinIO平台登录的账号密码，用于上传文件</p><h3 id="配置步骤" tabindex="-1"><a class="header-anchor" href="#配置步骤" aria-hidden="true">#</a> 配置步骤</h3><h4 id="_1-调整file服务的配置" tabindex="-1"><a class="header-anchor" href="#_1-调整file服务的配置" aria-hidden="true">#</a> 1. 调整<code>file</code>服务的配置</h4><p>修改<code>server/configs/django/local_file.py</code>文件，取消以下代码的注释</p><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code># MINIO
STORAGE = {
    &quot;CLIENT&quot;: os.environ.get(&quot;FILE_STORAGE_CLIENT&quot;, &quot;MINIO&quot;),  # 存储方式
    &quot;OPTIONS&quot;: {
        &quot;MINIO_ENTRYPOINT&quot;: os.environ.get(&quot;FILE_MINIO_ENTRYPOINT&quot;),
        &quot;MINIO_ACCESS_KEY&quot;: os.environ.get(&quot;FILE_MINIO_ACCESS_KEY&quot;),
        &quot;MINIO_SECRET_KEY&quot;: os.environ.get(&quot;FILE_MINIO_SECRET_KEY&quot;),
    }
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>修改<code>server/scripts/config.sh</code>文件，填写MinIO的信息</p><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>export FILE_MINIO_ENTRYPOINT=&lt;MinIO平台的地址&gt;
export FILE_MINIO_ACCESS_KEY=&lt;MinIO平台的登录账号&gt;
export FILE_MINIO_SECRET_KEY=&lt;MinIO平台的登录密码&gt;
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>修改完配置后，如果服务已经正在运行，则执行以下命令重启服务</p><div class="language-Bash line-numbers-mode" data-ext="Bash"><pre class="language-Bash"><code>$ cd server
$ ./scripts/deploy.sh start
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div></div></div><h4 id="_2-修改nginx服务的配置文件" tabindex="-1"><a class="header-anchor" href="#_2-修改nginx服务的配置文件" aria-hidden="true">#</a> 2. 修改nginx服务的配置文件</h4><p>删除nginx已有的文件服务器配置文件<code>/etc/nginx/conf.d/tca_file_local.conf</code>文件，然后执行</p><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>rm /etc/nginx/conf.d/tca_file_local.conf
ln -s $CURRENT_PATH/configs/nginx/tca_file_minio.conf /etc/nginx/conf.d/tca_file_local.conf
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div></div></div><blockquote><p>也可以修改<code>server/scripts/init_config.sh</code></p><div class="language-Bash line-numbers-mode" data-ext="Bash"><pre class="language-Bash"><code># 注释这一行
ln -s $CURRENT_PATH/configs/nginx/tca_file_local.conf /etc/nginx/conf.d/tca_file_local.conf
# 取消注释这一行
ln -s $CURRENT_PATH/configs/nginx/tca_file_minio.conf /etc/nginx/conf.d/tca_file_local.conf
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div></blockquote><p>修改完配置后，如果nginx已经正在运行，则执行<code>nginx -s reload</code></p><h3 id="结尾" tabindex="-1"><a class="header-anchor" href="#结尾" aria-hidden="true">#</a> 结尾</h3><p>以上两个步骤操作完成后，就可以通过<code>MinIO</code>存储文件了~</p>`,21),c=[s];function o(l,r){return n(),i("div",null,c)}const u=e(d,[["render",o],["__file","deploy_with_minio.html.vue"]]);export{u as default};
