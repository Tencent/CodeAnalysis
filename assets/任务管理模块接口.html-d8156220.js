import{_ as t,o as e,c as d,e as i}from"./app-697cd87e.js";const n={},s=i(`<h1 id="任务管理模块" tabindex="-1"><a class="header-anchor" href="#任务管理模块" aria-hidden="true">#</a> 任务管理模块</h1><h2 id="执行指定代码库指定分析项目扫描任务" tabindex="-1"><a class="header-anchor" href="#执行指定代码库指定分析项目扫描任务" aria-hidden="true">#</a> 执行指定代码库指定分析项目扫描任务</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>POST /server/main/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/projects/&lt;project_id&gt;/scans/create/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="参数列表" tabindex="-1"><a class="header-anchor" href="#参数列表" aria-hidden="true">#</a> 参数列表</h4><table><thead><tr><th>参数</th><th>类型</th><th>描述</th></tr></thead><tbody><tr><td>incr_scan</td><td>bool</td><td>选填，增量扫描标志，true表示增量，false表示全量</td></tr><tr><td>async_flag</td><td>bool</td><td>选填，异步启动标志，true表示异步，false表示同步，建议选择异步</td></tr><tr><td>force_create</td><td>bool</td><td>选填，强制启动标志，true表示强制启动，不等待上一个任务结束</td></tr></tbody></table><h4 id="返回结果" tabindex="-1"><a class="header-anchor" href="#返回结果" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;job&quot;: {
        &quot;id&quot;: 7974
    },
    &quot;scan&quot;: {
        &quot;id&quot;: 5528
    }
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="查看指定项目的任务列表" tabindex="-1"><a class="header-anchor" href="#查看指定项目的任务列表" aria-hidden="true">#</a> 查看指定项目的任务列表</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/main/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/projects/&lt;project_id&gt;/jobs/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="参数列表-1" tabindex="-1"><a class="header-anchor" href="#参数列表-1" aria-hidden="true">#</a> 参数列表</h4><table><thead><tr><th>参数</th><th>类型</th><th>描述</th></tr></thead><tbody><tr><td>create_time_gte</td><td>datetime</td><td>选填，最小任务启动时间</td></tr><tr><td>create_time_lte</td><td>datetime</td><td>选填，最大任务启动时间</td></tr><tr><td>result_code_gte</td><td>int</td><td>选填，最小错误码值</td></tr><tr><td>result_code_lte</td><td>int</td><td>选填，最大错误码值</td></tr><tr><td>result_msg</td><td>str</td><td>选填，结果信息</td></tr><tr><td>state</td><td>int</td><td>选填，任务状态, 0为等待中，1为执行中，2为关闭，3为入库中，可多选，格式为1,2,3</td></tr><tr><td>created_from</td><td>str</td><td>选填，创建来源</td></tr><tr><td>creator</td><td>str</td><td>选填，创建用户</td></tr></tbody></table><h4 id="返回结果-1" tabindex="-1"><a class="header-anchor" href="#返回结果-1" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;count&quot;: 1,
        &quot;next&quot;: null,
        &quot;previous&quot;: null,
        &quot;results&quot;: [
            {
                &quot;id&quot;: 1,
                &quot;state&quot;: 2,
                &quot;result_code&quot;: 0,
                &quot;result_msg&quot;: &quot;success&quot;,
                &quot;code_line_num&quot;: 1000,
                &quot;comment_line_num&quot;: 5,
                &quot;blank_line_num&quot;: 305,
                &quot;total_line_num&quot;: 1400
            }
        ]
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="查看指定项目的指定任务详情" tabindex="-1"><a class="header-anchor" href="#查看指定项目的指定任务详情" aria-hidden="true">#</a> 查看指定项目的指定任务详情</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/main/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/projects/&lt;project_id&gt;/jobs/&lt;job_id&gt;/detail/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="返回结果-2" tabindex="-1"><a class="header-anchor" href="#返回结果-2" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;id&quot;: 1,
        &quot;scan_id&quot;: 1,
        &quot;create_time&quot;: &quot;2021-01-28T10:27:26.442961+08:00&quot;,
        &quot;waiting_time&quot;: &quot;1&quot;,
        &quot;start_time&quot;: &quot;2021-01-28T11:14:56.760427+08:00&quot;,
        &quot;execute_time&quot;: &quot;3&quot;,
        &quot;project&quot;: {
            &quot;id&quot;: 1,
            &quot;branch&quot;: &quot;master&quot;,
            &quot;repo_id&quot;: 1,
            &quot;scan_scheme&quot;: 1,
            &quot;repo_scm_url&quot;: &quot;http://github.com/xxx/test_demo.git&quot;
        },
        &quot;end_time&quot;: &quot;2021-01-28T11:14:59.760427+08:00&quot;,
        &quot;expire_time&quot;: &quot;2021-01-28T14:07:52.968932+08:00&quot;,
        &quot;task_num&quot;: 1,
        &quot;task_done&quot;: 1,
        &quot;tasks&quot;: [
            {
                &quot;id&quot;: 1,
                &quot;module&quot;: &quot;codelint&quot;,
                &quot;task_name&quot;: &quot;pylint&quot;,
                &quot;progress_rate&quot;: 1,
                &quot;state&quot;: 2,
                &quot;result_code&quot;: 0,
                &quot;result_msg&quot;: &quot;success&quot;,
                &quot;result_path&quot;: null
            }
        ],
        &quot;co_jobs&quot;: [],
        &quot;state&quot;: 2,
        &quot;result_code&quot;: 0,
        &quot;result_code_msg&quot;: null,
        &quot;result_msg&quot;: &quot;success&quot;,
        &quot;result_path&quot;: null,
        &quot;remarks&quot;: null,
        &quot;remarked_by&quot;: null,
        &quot;code_line_num&quot;: 1000,
        &quot;comment_line_num&quot;: 5,
        &quot;blank_line_num&quot;: 305,
        &quot;total_line_num&quot;: 1400,
        &quot;created_from&quot;: &quot;codedog_web&quot;,
        &quot;creator&quot;: &quot;creator&quot;
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div>`,17),u=[s];function a(l,r){return e(),d("div",null,u)}const c=t(n,[["render",a],["__file","任务管理模块接口.html.vue"]]);export{c as default};
