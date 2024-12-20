import{_ as e}from"./API的个人令牌-d33dd7b6.js";import{_ as n,o as i,c as t,e as u}from"./app-697cd87e.js";const s={},o=u(`<h1 id="接口调用说明" tabindex="-1"><a class="header-anchor" href="#接口调用说明" aria-hidden="true">#</a> 接口调用说明</h1><h2 id="接口地址" tabindex="-1"><a class="header-anchor" href="#接口地址" aria-hidden="true">#</a> 接口地址</h2><p><code>http://{host}/server/</code></p><p>注：host 指当前浏览器访问该文档的 URL 域名部分。</p><h2 id="接口鉴权方式" tabindex="-1"><a class="header-anchor" href="#接口鉴权方式" aria-hidden="true">#</a> 接口鉴权方式</h2><p>发起请求时，需要在头部中添加以下格式形式，对应的 value 请看下面获取方式</p><div class="language-json line-numbers-mode" data-ext="json"><pre class="language-json"><code>{
  &quot;Authorization&quot;: &quot;Token 当前user的token&quot;
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>获取 token 位置（个人中心-个人令牌）：</p><p><img src="`+e+`" alt="API的个人令牌"></p><h2 id="获取-org-sid-和-project-team-信息" tabindex="-1"><a class="header-anchor" href="#获取-org-sid-和-project-team-信息" aria-hidden="true">#</a> 获取 org_sid 和 project_team 信息</h2><p>通过平台访问具体代码库扫描情况时，可从 URL 中获取对应 org_sid 和 project_team 字段，查看方式如下例子：</p><p>代码库扫描地址：<code>http://{host}/t/xxx/p/yyy/code-analysis/repos/1/projects?limit=10&amp;offset=0</code></p><p>其中，org_sid 为<code>xxx</code>字段，project_team 为 <code>yyy</code>字段</p><h2 id="example" tabindex="-1"><a class="header-anchor" href="#example" aria-hidden="true">#</a> Example</h2><div class="language-python line-numbers-mode" data-ext="py"><pre class="language-python"><code>import requests
# 假设：
# 当前域名为http://tca.com/，当前org_sid为helloworld
# 获取helloworld团队下的hellotca项目下登记的代码库
url=&quot;http://tca.com/server/main/api/orgs/helloworld/teams/hellotca/repos/?limit=12&amp;offset=0&quot;
headers = {
  &quot;Authorization&quot;: &quot;Token %s&quot; % token,
}

response = requests.get(url, headers=headers)
print(response.json())
# 结果如下：
{
    &quot;data&quot;: {
        &quot;count&quot;: 1,
        &quot;next&quot;: null,
        &quot;previous&quot;: null,
        &quot;results&quot;: [
            {
                &quot;id&quot;: 23,
                &quot;name&quot;: &quot;repo_name&quot;,
                &quot;scm_url&quot;: &quot;http://git.repo.com/group/repo_name&quot;,
                &quot;scm_type&quot;: &quot;git&quot;,
                &quot;branch_count&quot;: 1,
                &quot;scheme_count&quot;: 1,
                &quot;job_count&quot;: 1,
                &quot;created_time&quot;: &quot;2021-05-14 02:34:44.509118+00:00&quot;,
                &quot;recent_active&quot;: {
                    &quot;id&quot;: 27,
                    &quot;branch_name&quot;: &quot;master&quot;,
                    &quot;active_time&quot;: &quot;2021-05-14 02:34:44.509118+00:00&quot;,
                    &quot;total_line_num&quot;: 1,
                    &quot;code_line_num&quot;: 1
                },
                &quot;created_from&quot;: &quot;tca&quot;,
                &quot;creator&quot;: {
                    &quot;username&quot;: &quot;author&quot;,
                    &quot;nickname&quot;: &quot;author&quot;,
                    &quot;status&quot;: 1,
                    &quot;avatar&quot;: &quot;url&quot;,
                    &quot;org&quot;: &quot;org_name&quot;
                },
                &quot;symbol&quot;: null,
                &quot;scm_auth&quot;: {
                    &quot;id&quot;: 1,
                    &quot;scm_account&quot;: null,
                    &quot;scm_oauth&quot;: null,
                    &quot;scm_ssh&quot;: {
                        &quot;id&quot;: 1,
                        &quot;name&quot;: &quot;test&quot;,
                        &quot;scm_platform&quot;: 2,
                        &quot;scm_platform_desc&quot;: null,
                        &quot;user&quot;: {
                            &quot;username&quot;: &quot;username&quot;,
                            &quot;nickname&quot;: &quot;nickname&quot;,
                            &quot;status&quot;: 1,
                            &quot;avatar&quot;: &quot;url&quot;,
                            &quot;org&quot;: &quot;org_name&quot;
                        }
                    },
                    &quot;auth_type&quot;: &quot;ssh_token&quot;,
                    &quot;created_time&quot;: &quot;2021-05-14T10:34:44.552859+08:00&quot;,
                    &quot;modified_time&quot;: &quot;2021-05-14T10:34:44.552887+08:00&quot;
                },
                &quot;project_team&quot;: {
                    &quot;name&quot;: &quot;test&quot;,
                    &quot;display_name&quot;: &quot;测试&quot;,
                    &quot;status&quot;: 1,
                    &quot;org_sid&quot;: &quot;test&quot;
                }
            }
        ]
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="分页方式" tabindex="-1"><a class="header-anchor" href="#分页方式" aria-hidden="true">#</a> 分页方式</h2><p>平台返回的数据分页格式是使用<code>limit</code>和<code>offset</code>参数进行分页处理</p><p>比如：<code>server/main/api/orgs/&lt;org_sid&gt;/teams/?limit=12&amp;offset=12</code>获取得到的数据是从第 13 条开始获取</p><h2 id="响应格式" tabindex="-1"><a class="header-anchor" href="#响应格式" aria-hidden="true">#</a> 响应格式</h2><p>平台返回的响应格式如下：</p><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {...},      # 详细数据
    &quot;code&quot;: 0,          # 请求结果码，为0表示正常
    &quot;msg&quot;: &quot;xxx&quot; ,      # 请求结果信息
    &quot;status_code&quot;: 200  # 请求响应码
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div>`,21),d=[o];function a(l,r){return i(),t("div",null,d)}const q=n(s,[["render",a],["__file","index.html.vue"]]);export{q as default};
