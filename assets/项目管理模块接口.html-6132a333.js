import{_ as e,o as t,c as i,e as n}from"./app-697cd87e.js";const d={},u=n(`<h1 id="项目管理模块" tabindex="-1"><a class="header-anchor" href="#项目管理模块" aria-hidden="true">#</a> 项目管理模块</h1><h2 id="查看指定代码库的指定分析项目列表" tabindex="-1"><a class="header-anchor" href="#查看指定代码库的指定分析项目列表" aria-hidden="true">#</a> 查看指定代码库的指定分析项目列表</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/main/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="参数列表" tabindex="-1"><a class="header-anchor" href="#参数列表" aria-hidden="true">#</a> 参数列表</h4><table><thead><tr><th>参数</th><th>类型</th><th>描述</th></tr></thead><tbody><tr><td>scm_url_or_name</td><td>str</td><td>选填，代码库地址或者名称，支持模糊匹配</td></tr><tr><td>scm_url</td><td>str</td><td>选填，代码库仓库匹配</td></tr><tr><td>scope</td><td>str</td><td>选填，过滤范围（my/subscribed/related_me），my表示我创建的，subscribed表示我关注的，related_me表示我有权限的</td></tr></tbody></table><h4 id="返回结果" tabindex="-1"><a class="header-anchor" href="#返回结果" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;count&quot;: 1,
    &quot;next&quot;: null,
    &quot;previous&quot;: null,
    &quot;results&quot;: [
        {
            &quot;id&quot;: 1,
            &quot;name&quot;: &quot;test_repo.git&quot;,
            &quot;scm_url&quot;: &quot;http://git.com/xxx/test_repo&quot;,
            &quot;scm_type&quot;: &quot;git&quot;,
            &quot;branch_count&quot;: 1,
            &quot;scheme_count&quot;: 1,
            &quot;job_count&quot;: 1,
            &quot;created_time&quot;: &quot;2021-03-15 02:26:31.423674+00:00&quot;,
            &quot;recent_active&quot;: {
                &quot;id&quot;: 1,
                &quot;branch_name&quot;: &quot;master&quot;,
                &quot;active_time&quot;: &quot;2021-03-15T03:14:56.760427Z&quot;,
                &quot;total_line_num&quot;: null,
                &quot;code_line_num&quot;: null
            },
            &quot;created_from&quot;: &quot;codedog_web&quot;,
            &quot;creator&quot;: {
                &quot;username&quot;: &quot;username&quot;,
                &quot;nickname&quot;: &quot;nickname&quot;,
                &quot;status&quot;: 1,
                &quot;avatar&quot;: null,
                &quot;org&quot;: 1
            },
            &quot;symbol&quot;: null
        }
    ]
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="查看已创建的授权信息" tabindex="-1"><a class="header-anchor" href="#查看已创建的授权信息" aria-hidden="true">#</a> 查看已创建的授权信息</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/main/api/authen/scmallaccounts/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="返回结果-1" tabindex="-1"><a class="header-anchor" href="#返回结果-1" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;ssh&quot;: [
            {
                &quot;id&quot;: 1,
                &quot;user&quot;: {
                    &quot;username&quot;: &quot;CodeDog&quot;,
                    &quot;nickname&quot;: &quot;CodeDog&quot;,
                    &quot;status&quot;: 1,
                    &quot;avatar&quot;: null,
                    &quot;latest_login_time&quot;: &quot;2022-10-22T15:30:30+08:00&quot;,
                    &quot;org&quot;: null
                },
                &quot;auth_origin&quot;: &quot;CodeDog&quot;,
                &quot;indentity&quot;: &quot;xxx&quot;,
                &quot;display_scm_platform&quot;: &quot;tgit&quot;,
                &quot;name&quot;: &quot;gerrit&quot;,
                &quot;scm_platform&quot;: 1,
                &quot;scm_platform_desc&quot;: null
            }
        ],
        &quot;account&quot;: [
            {
                &quot;id&quot;: 1,
                &quot;user&quot;: {
                    &quot;username&quot;: &quot;CodeDog&quot;,
                    &quot;nickname&quot;: &quot;CodeDog&quot;,
                    &quot;status&quot;: 1,
                    &quot;avatar&quot;: null,
                    &quot;latest_login_time&quot;: &quot;2022-10-22T15:30:30+08:00&quot;,
                    &quot;org&quot;: null
                },
                &quot;auth_origin&quot;: &quot;CodeDog&quot;,
                &quot;display_scm_platform&quot;: &quot;tgit&quot;,
                &quot;scm_username&quot;: &quot;CodeDog&quot;,
                &quot;scm_platform&quot;: 1,
                &quot;scm_platform_desc&quot;: null
            }
        ],
        &quot;oauth&quot;: [
            {
                &quot;id&quot;: 1,
                &quot;user&quot;: {
                    &quot;username&quot;: &quot;CodeDog&quot;,
                    &quot;nickname&quot;: &quot;CodeDog&quot;,
                    &quot;status&quot;: 1,
                    &quot;avatar&quot;: null,
                    &quot;latest_login_time&quot;: &quot;2022-10-22T15:30:30+08:00&quot;,
                    &quot;org&quot;: null
                },
                &quot;auth_origin&quot;: &quot;CodeDog&quot;,
                &quot;scm_platform_name&quot;: &quot;tgit&quot;
            }
        ],
    }
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="登记代码库" tabindex="-1"><a class="header-anchor" href="#登记代码库" aria-hidden="true">#</a> 登记代码库</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>POST /server/main/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="参数列表-1" tabindex="-1"><a class="header-anchor" href="#参数列表-1" aria-hidden="true">#</a> 参数列表</h4><table><thead><tr><th>参数</th><th>类型</th><th>描述</th></tr></thead><tbody><tr><td>scm_url</td><td>str</td><td>必填，代码库地址</td></tr><tr><td>scm_type</td><td>str</td><td>必填，git或svn</td></tr><tr><td>ssh_url</td><td>str</td><td>选填，代码库SSH地址</td></tr><tr><td>name</td><td>str</td><td>选填， 代码库名称</td></tr><tr><td>scm_auth</td><td>dict</td><td>选填，代码库授权</td></tr></tbody></table><p>例子:</p><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;scm_url&quot;: &quot;https://github.com/Tencent/CodeAnalysis&quot;,
    &quot;scm_type&quot;: &quot;git&quot;,
    &quot;name&quot;: &quot;CodeAnalysis&quot;,
    &quot;scm_auth&quot;: {
        # 通过 查看已创建的授权信息 接口获取到对应的凭证id，scm_account、scm_oauth、scm_ssh 只需填一个
        &quot;scm_account&quot;: account_id,
        &quot;scm_ssh&quot;: ssh_id,
        &quot;scm_oauth&quot;: oauth_id
    }
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h4 id="返回结果-2" tabindex="-1"><a class="header-anchor" href="#返回结果-2" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;:{
        &quot;id&quot;: 1,
        &quot;name&quot;: &quot;CodeAnalysis&quot;,
        &quot;scm_url&quot;: &quot;http://github.com/Tencent/CodeAnalysis&quot;,
        &quot;scm_type&quot;: &quot;git&quot;,
        &quot;branch_count&quot;: 0,
        &quot;scheme_count&quot;: 0,
        &quot;job_count&quot;: 0,
        &quot;created_time&quot;: &quot;2022-10-22T16:30:30+08:00&quot;,
        &quot;recent_active&quot;: {
        },
        &quot;created_from&quot;: &quot;codedog_web&quot;,
        &quot;creator&quot;: {
            &quot;username&quot;: &quot;username&quot;,
            &quot;nickname&quot;: &quot;nickname&quot;,
            &quot;status&quot;: 1,
            &quot;avatar&quot;: null,
            &quot;org&quot;: 1
        },
        &quot;symbol&quot;: null
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="查看指定代码库详情" tabindex="-1"><a class="header-anchor" href="#查看指定代码库详情" aria-hidden="true">#</a> 查看指定代码库详情</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/main/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="返回结果-3" tabindex="-1"><a class="header-anchor" href="#返回结果-3" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;:{
        &quot;id&quot;: 1,
        &quot;name&quot;: &quot;test_repo.git&quot;,
        &quot;scm_url&quot;: &quot;http://git.com/xxx/test_repo&quot;,
        &quot;scm_type&quot;: &quot;git&quot;,
        &quot;branch_count&quot;: 1,
        &quot;scheme_count&quot;: 1,
        &quot;job_count&quot;: 1,
        &quot;created_time&quot;: &quot;2021-03-15 02:26:31.423674+00:00&quot;,
        &quot;recent_active&quot;: {
            &quot;id&quot;: 1,
            &quot;branch_name&quot;: &quot;master&quot;,
            &quot;active_time&quot;: &quot;2021-03-15T03:14:56.760427Z&quot;,
            &quot;total_line_num&quot;: null,
            &quot;code_line_num&quot;: null
        },
        &quot;created_from&quot;: &quot;codedog_web&quot;,
        &quot;creator&quot;: {
            &quot;username&quot;: &quot;username&quot;,
            &quot;nickname&quot;: &quot;nickname&quot;,
            &quot;status&quot;: 1,
            &quot;avatar&quot;: null,
            &quot;org&quot;: 1
        },
        &quot;symbol&quot;: null
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="查看指定代码库的不同分支的列表接口" tabindex="-1"><a class="header-anchor" href="#查看指定代码库的不同分支的列表接口" aria-hidden="true">#</a> 查看指定代码库的不同分支的列表接口</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/main/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/branches/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="返回结果-4" tabindex="-1"><a class="header-anchor" href="#返回结果-4" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;count&quot;: 1,
        &quot;next&quot;: null,
        &quot;previous&quot;: null,
        &quot;results&quot;: [
            {
                &quot;branch&quot;: &quot;master&quot;,
                &quot;schemes&quot;: [
                    {
                        &quot;project_id&quot;: 1,
                        &quot;scan_scheme_id&quot;: 1,
                        &quot;scan_scheme_name&quot;: &quot;默认&quot;
                    }
                ]
            }
        ]
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="查看指定代码库的分析项目列表" tabindex="-1"><a class="header-anchor" href="#查看指定代码库的分析项目列表" aria-hidden="true">#</a> 查看指定代码库的分析项目列表</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/main/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/projects/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="参数列表-2" tabindex="-1"><a class="header-anchor" href="#参数列表-2" aria-hidden="true">#</a> 参数列表</h4><table><thead><tr><th>参数</th><th>类型</th><th>描述</th></tr></thead><tbody><tr><td>branch</td><td>str</td><td>选填，分支名称</td></tr><tr><td>scan_scheme</td><td>int</td><td>选填，扫描方案名称</td></tr><tr><td>scan_scheme__status</td><td>int</td><td>选填，扫描方案状态，1为活跃，2为废弃</td></tr><tr><td>branch_or_scheme</td><td>str</td><td>选填，分支名称/扫描方案名称</td></tr><tr><td>status</td><td>int</td><td>选填，项目状态筛选，1表示活跃，2表示失活，3表示关闭</td></tr></tbody></table><h4 id="返回结果-5" tabindex="-1"><a class="header-anchor" href="#返回结果-5" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;count&quot;: 1,
        &quot;next&quot;: null,
        &quot;previous&quot;: null,
        &quot;results&quot;: [
            {
                &quot;id&quot;: 1,
                &quot;creator&quot;: {
                    &quot;username&quot;: &quot;username&quot;,
                    &quot;nickname&quot;: &quot;nickname&quot;,
                    &quot;status&quot;: 1,
                    &quot;avatar&quot;: null,
                    &quot;org&quot;: 1
                },
                &quot;created_time&quot;: &quot;2021-01-28 02:27:26.256015+00:00&quot;,
                &quot;modifier&quot;: null,
                &quot;modified_time&quot;: &quot;2021-01-28 02:27:26.256284+00:00&quot;,
                &quot;deleter&quot;: null,
                &quot;deleted_time&quot;: null,
                &quot;scan_scheme&quot;: {
                    &quot;id&quot;: 1,
                    &quot;creator&quot;: {
                        &quot;username&quot;: &quot;username&quot;,
                        &quot;nickname&quot;: &quot;nickname&quot;,
                        &quot;status&quot;: 1,
                        &quot;avatar&quot;: null,
                        &quot;org&quot;: 1
                    },
                    &quot;created_time&quot;: &quot;2021-01-28 02:27:26.209661+00:00&quot;,
                    &quot;modifier&quot;: null,
                    &quot;modified_time&quot;: &quot;2021-01-28 02:27:26.255023+00:00&quot;,
                    &quot;deleter&quot;: null,
                    &quot;deleted_time&quot;: null,
                    &quot;languages&quot;: [
                        &quot;python&quot;
                    ],
                    &quot;tag&quot;: &quot;TCA_Linux&quot;,
                    &quot;refer_scheme_info&quot;: null,
                    &quot;name&quot;: &quot;默认&quot;,
                    &quot;description&quot;: null,
                    &quot;default_flag&quot;: true,
                    &quot;created_from&quot;: &quot;web&quot;,
                    &quot;job_runtime_limit&quot;: 600,
                    &quot;ignore_merged_issue&quot;: false,
                    &quot;ignore_branch_issue&quot;: null,
                    &quot;ignore_submodule_clone&quot;: false,
                    &quot;ignore_submodule_issue&quot;: true,
                    &quot;issue_global_ignore&quot;: false,
                    &quot;daily_save&quot;: false,
                    &quot;lfs_flag&quot;: null,
                    &quot;webhook_flag&quot;: false,
                    &quot;issue_revision_merge_flag&quot;: false,
                    &quot;status&quot;: 1,
                    &quot;scheme_key&quot;: null,
                    &quot;repo&quot;: 1
                },
                &quot;branch&quot;: &quot;master&quot;,
                &quot;status&quot;: 1,
                &quot;created_from&quot;: &quot;codedog_web&quot;,
                &quot;repo&quot;: 1
            }
        ]
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="创建指定代码库的指定分析项目" tabindex="-1"><a class="header-anchor" href="#创建指定代码库的指定分析项目" aria-hidden="true">#</a> 创建指定代码库的指定分析项目</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>POST /server/main/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/projects/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="参数列表-3" tabindex="-1"><a class="header-anchor" href="#参数列表-3" aria-hidden="true">#</a> 参数列表</h4><table><thead><tr><th>参数</th><th>类型</th><th>描述</th></tr></thead><tbody><tr><td>scan_scheme_id</td><td>int</td><td>和global_scheme_id二选一进行填写，当前代码库的扫描方案编号</td></tr><tr><td>global_scheme_id</td><td>int</td><td>和scan_scheme_id二选一进行填写，扫描方案模板编号</td></tr><tr><td>custom_scheme_name</td><td>str</td><td>选填，自定义方案名称</td></tr><tr><td>branch</td><td>str</td><td>必填，分支</td></tr><tr><td>created_from</td><td>str</td><td>选填，创建渠道，用于区分不同运行场景</td></tr></tbody></table><h4 id="返回结果-6" tabindex="-1"><a class="header-anchor" href="#返回结果-6" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;id&quot;:1,
        &quot;creator&quot;: {
            &quot;username&quot;: &quot;username&quot;,
            &quot;nickname&quot;: &quot;nickname&quot;,
            &quot;status&quot;: 1,
            &quot;avatar&quot;: null,
            &quot;org&quot;: 1
        },
        &quot;created_time&quot;: &quot;2021-01-28 02:27:26.256015+00:00&quot;,
        &quot;modifier&quot;: null,
        &quot;modified_time&quot;: &quot;2021-01-28 02:27:26.256284+00:00&quot;,
        &quot;deleter&quot;: null,
        &quot;deleted_time&quot;: null,
        &quot;repo&quot;: {
            &quot;id&quot;: 1,
            &quot;name&quot;: &quot;test_demo.git&quot;,
            &quot;scm_url&quot;: &quot;http://github.com/xxxx/test_demo.git&quot;,
            &quot;scm_type&quot;: &quot;git&quot;,
            &quot;scm_auth&quot;: {
                &quot;id&quot;: 1,
                &quot;scm_account&quot;: null,
                &quot;scm_oauth&quot;: null,
                &quot;scm_ssh&quot;: {
                    &quot;id&quot;: 1,
                    &quot;name&quot;: &quot;1&quot;,
                    &quot;scm_platform&quot;: 1,
                    &quot;scm_platform_desc&quot;: null,
                    &quot;user&quot;: {
                        &quot;username&quot;: &quot;username&quot;,
                        &quot;nickname&quot;: &quot;nickname&quot;,
                        &quot;status&quot;: 1,
                        &quot;avatar&quot;: null,
                        &quot;org&quot;: 1
                    }
                },
                &quot;auth_type&quot;: &quot;ssh_token&quot;,
                &quot;created_time&quot;: &quot;2021-01-28T10:26:31.453389+08:00&quot;,
                &quot;modified_time&quot;: &quot;2021-01-28T10:26:31.453417+08:00&quot;
            },
            &quot;symbol&quot;: null
        },
        &quot;scan_scheme&quot;: {
            &quot;id&quot;: 1,
            &quot;creator&quot;: {
                &quot;username&quot;: &quot;username&quot;,
                &quot;nickname&quot;: &quot;nickname&quot;,
                &quot;status&quot;: 1,
                &quot;avatar&quot;: null,
                &quot;org&quot;: 1
            },
            &quot;created_time&quot;: &quot;2021-01-28 02:27:26.209661+00:00&quot;,
            &quot;modifier&quot;: null,
            &quot;modified_time&quot;: &quot;2021-01-28 02:27:26.255023+00:00&quot;,
            &quot;deleter&quot;: null,
            &quot;deleted_time&quot;: null,
            &quot;languages&quot;: [
                &quot;python&quot;
            ],
            &quot;tag&quot;: &quot;TCA_Linux&quot;,
            &quot;refer_scheme_info&quot;: null,
            &quot;name&quot;: &quot;默认&quot;,
            &quot;description&quot;: null,
            &quot;default_flag&quot;: true,
            &quot;created_from&quot;: &quot;web&quot;,
            &quot;job_runtime_limit&quot;: 600,
            &quot;ignore_merged_issue&quot;: false,
            &quot;ignore_branch_issue&quot;: null,
            &quot;ignore_submodule_clone&quot;: false,
            &quot;ignore_submodule_issue&quot;: true,
            &quot;issue_global_ignore&quot;: false,
            &quot;daily_save&quot;: false,
            &quot;lfs_flag&quot;: null,
            &quot;webhook_flag&quot;: false,
            &quot;issue_revision_merge_flag&quot;: false,
            &quot;status&quot;: 1,
            &quot;scheme_key&quot;: null,
            &quot;repo&quot;: 1
        },
        &quot;branch&quot;: &quot;master&quot;,
        &quot;status&quot;: 1,
        &quot;created_from&quot;: &quot;tca_web&quot;
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="查看指定代码库的指定分析项目" tabindex="-1"><a class="header-anchor" href="#查看指定代码库的指定分析项目" aria-hidden="true">#</a> 查看指定代码库的指定分析项目</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/main/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/projects/&lt;project_id&gt;/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="返回结果-7" tabindex="-1"><a class="header-anchor" href="#返回结果-7" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;id&quot;:1,
        &quot;creator&quot;: {
            &quot;username&quot;: &quot;username&quot;,
            &quot;nickname&quot;: &quot;nickname&quot;,
            &quot;status&quot;: 1,
            &quot;avatar&quot;: null,
            &quot;org&quot;: 1
        },
        &quot;created_time&quot;: &quot;2021-01-28 02:27:26.256015+00:00&quot;,
        &quot;modifier&quot;: null,
        &quot;modified_time&quot;: &quot;2021-01-28 02:27:26.256284+00:00&quot;,
        &quot;deleter&quot;: null,
        &quot;deleted_time&quot;: null,
        &quot;repo&quot;: {
            &quot;id&quot;: 1,
            &quot;name&quot;: &quot;test_demo.git&quot;,
            &quot;scm_url&quot;: &quot;http://github.com/xxxx/test_demo.git&quot;,
            &quot;scm_type&quot;: &quot;git&quot;,
            &quot;scm_auth&quot;: {
                &quot;id&quot;: 1,
                &quot;scm_account&quot;: null,
                &quot;scm_oauth&quot;: null,
                &quot;scm_ssh&quot;: {
                    &quot;id&quot;: 1,
                    &quot;name&quot;: &quot;1&quot;,
                    &quot;scm_platform&quot;: 1,
                    &quot;scm_platform_desc&quot;: null,
                    &quot;user&quot;: {
                        &quot;username&quot;: &quot;username&quot;,
                        &quot;nickname&quot;: &quot;nickname&quot;,
                        &quot;status&quot;: 1,
                        &quot;avatar&quot;: null,
                        &quot;org&quot;: 1
                    }
                },
                &quot;auth_type&quot;: &quot;ssh_token&quot;,
                &quot;created_time&quot;: &quot;2021-01-28T10:26:31.453389+08:00&quot;,
                &quot;modified_time&quot;: &quot;2021-01-28T10:26:31.453417+08:00&quot;
            },
            &quot;symbol&quot;: null
        },
        &quot;scan_scheme&quot;: {
            &quot;id&quot;: 1,
            &quot;creator&quot;: {
                &quot;username&quot;: &quot;username&quot;,
                &quot;nickname&quot;: &quot;nickname&quot;,
                &quot;status&quot;: 1,
                &quot;avatar&quot;: null,
                &quot;org&quot;: 1
            },
            &quot;created_time&quot;: &quot;2021-01-28 02:27:26.209661+00:00&quot;,
            &quot;modifier&quot;: null,
            &quot;modified_time&quot;: &quot;2021-01-28 02:27:26.255023+00:00&quot;,
            &quot;deleter&quot;: null,
            &quot;deleted_time&quot;: null,
            &quot;languages&quot;: [
                &quot;python&quot;
            ],
            &quot;tag&quot;: &quot;TCA_Linux&quot;,
            &quot;refer_scheme_info&quot;: null,
            &quot;name&quot;: &quot;默认&quot;,
            &quot;description&quot;: null,
            &quot;default_flag&quot;: true,
            &quot;created_from&quot;: &quot;web&quot;,
            &quot;job_runtime_limit&quot;: 600,
            &quot;ignore_merged_issue&quot;: false,
            &quot;ignore_branch_issue&quot;: null,
            &quot;ignore_submodule_clone&quot;: false,
            &quot;ignore_submodule_issue&quot;: true,
            &quot;issue_global_ignore&quot;: false,
            &quot;daily_save&quot;: false,
            &quot;lfs_flag&quot;: null,
            &quot;webhook_flag&quot;: false,
            &quot;issue_revision_merge_flag&quot;: false,
            &quot;status&quot;: 1,
            &quot;scheme_key&quot;: null,
            &quot;repo&quot;: 1
        },
        &quot;branch&quot;: &quot;master&quot;,
        &quot;status&quot;: 1,
        &quot;created_from&quot;: &quot;tca_web&quot;
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="查看指定代码库的扫描方案列表" tabindex="-1"><a class="header-anchor" href="#查看指定代码库的扫描方案列表" aria-hidden="true">#</a> 查看指定代码库的扫描方案列表</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/main/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/schemes/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="参数列表-4" tabindex="-1"><a class="header-anchor" href="#参数列表-4" aria-hidden="true">#</a> 参数列表</h4><table><thead><tr><th>参数</th><th>类型</th><th>描述</th></tr></thead><tbody><tr><td>name</td><td>str</td><td>选填，扫描方案名称</td></tr><tr><td>status</td><td>int</td><td>选填，扫描方案状态，1为活跃，2为废弃</td></tr></tbody></table><h4 id="返回结果-8" tabindex="-1"><a class="header-anchor" href="#返回结果-8" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;count&quot;: 1,
        &quot;next&quot;: null,
        &quot;previous&quot;: null,
        &quot;results&quot;: [
            {
                &quot;id&quot;: 1,
                &quot;creator&quot;: {
                    &quot;username&quot;: &quot;username&quot;,
                    &quot;nickname&quot;: &quot;nickname&quot;,
                    &quot;status&quot;: 1,
                    &quot;avatar&quot;: null,
                    &quot;org&quot;: 1
                },
                &quot;created_time&quot;: &quot;2021-01-28 02:27:26.209661+00:00&quot;,
                &quot;modifier&quot;: null,
                &quot;modified_time&quot;: &quot;2021-01-28 02:27:26.255023+00:00&quot;,
                &quot;deleter&quot;: null,
                &quot;deleted_time&quot;: null,
                &quot;languages&quot;: [
                    &quot;python&quot;
                ],
                &quot;tag&quot;: &quot;TCA_Linux&quot;,
                &quot;refer_scheme&quot;: null,
                &quot;name&quot;: &quot;默认&quot;,
                &quot;description&quot;: null,
                &quot;default_flag&quot;: true,
                &quot;created_from&quot;: &quot;web&quot;,
                &quot;job_runtime_limit&quot;: 600,
                &quot;ignore_merged_issue&quot;: false,
                &quot;ignore_branch_issue&quot;: null,
                &quot;ignore_submodule_clone&quot;: false,
                &quot;ignore_submodule_issue&quot;: true,
                &quot;issue_global_ignore&quot;: false,
                &quot;daily_save&quot;: false,
                &quot;lfs_flag&quot;: null,
                &quot;issue_revision_merge_flag&quot;: false,
                &quot;status&quot;: 1,
                &quot;repo&quot;: 1
            }
        ]
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="查看指定代码库的指定扫描方案" tabindex="-1"><a class="header-anchor" href="#查看指定代码库的指定扫描方案" aria-hidden="true">#</a> 查看指定代码库的指定扫描方案</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/main/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/schemes/&lt;scheme_id&gt;/basicconf/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="返回结果-9" tabindex="-1"><a class="header-anchor" href="#返回结果-9" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;id&quot;: 1,
        &quot;creator&quot;: {
            &quot;username&quot;: &quot;username&quot;,
            &quot;nickname&quot;: &quot;nickname&quot;,
            &quot;status&quot;: 1,
            &quot;avatar&quot;: null,
            &quot;org&quot;: 1
        },
        &quot;created_time&quot;: &quot;2021-01-28 02:27:26.209661+00:00&quot;,
        &quot;modifier&quot;: null,
        &quot;modified_time&quot;: &quot;2021-01-28 02:27:26.255023+00:00&quot;,
        &quot;deleter&quot;: null,
        &quot;deleted_time&quot;: null,
        &quot;languages&quot;: [
            &quot;python&quot;
        ],
        &quot;tag&quot;: &quot;TCA_Linux&quot;,
        &quot;refer_scheme&quot;: null,
        &quot;name&quot;: &quot;默认&quot;,
        &quot;description&quot;: null,
        &quot;default_flag&quot;: true,
        &quot;created_from&quot;: &quot;web&quot;,
        &quot;job_runtime_limit&quot;: 600,
        &quot;ignore_merged_issue&quot;: false,
        &quot;ignore_branch_issue&quot;: null,
        &quot;ignore_submodule_clone&quot;: false,
        &quot;ignore_submodule_issue&quot;: true,
        &quot;issue_global_ignore&quot;: false,
        &quot;daily_save&quot;: false,
        &quot;lfs_flag&quot;: null,
        &quot;issue_revision_merge_flag&quot;: false,
        &quot;status&quot;: 1,
        &quot;repo&quot;: 1
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="更新指定代码库的指定方案" tabindex="-1"><a class="header-anchor" href="#更新指定代码库的指定方案" aria-hidden="true">#</a> 更新指定代码库的指定方案</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>PUT /server/main/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/schemes/&lt;scheme_id&gt;/basicconf/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="参数列表-5" tabindex="-1"><a class="header-anchor" href="#参数列表-5" aria-hidden="true">#</a> 参数列表</h4><table><thead><tr><th>参数</th><th>类型</th><th>描述</th></tr></thead><tbody><tr><td>languages</td><td>list</td><td>选填，代码语言</td></tr><tr><td>tag</td><td>str</td><td>选填，执行标签，目前只支持 CodeDog_Linux</td></tr><tr><td>name</td><td>str</td><td>必填，方案名称</td></tr><tr><td>description</td><td>str</td><td>选填，方案描述</td></tr><tr><td>default_flag</td><td>bool</td><td>选填，默认方案标志，一个代码库只能有一个默认方案</td></tr><tr><td>job_runtime_limit</td><td>int</td><td>选填，任务执行超时时间，默认为600分钟</td></tr><tr><td>ignore_merged_issue</td><td>bool</td><td>选填，忽略合入的问题</td></tr><tr><td>ignore_branch_issue</td><td>str</td><td>选填，过滤参考分支引入的问题</td></tr><tr><td>ignore_submodule_clone</td><td>bool</td><td>选填，不拉取子模块扫描，True表示不拉取，False表示拉取</td></tr><tr><td>ignore_submodule_issue</td><td>bool</td><td>选填，忽略子模块引入的问题，True表示忽略，False表示不忽略</td></tr><tr><td>issue_global_ignore</td><td>bool</td><td>选填，问题全局忽略</td></tr><tr><td>daily_save</td><td>bool</td><td>选填，每次扫描原始数据存储，默认存储7天</td></tr><tr><td>lfs_flag</td><td>bool</td><td>选填，拉取lfs模块开关</td></tr><tr><td>issue_revision_merge_flag</td><td>bool</td><td>选填，&quot;是否开启Issue按引入版本号聚合开关</td></tr><tr><td>status</td><td>int</td><td>选填，方案状态，1表示活跃，2表示废弃</td></tr></tbody></table><h4 id="返回结果-10" tabindex="-1"><a class="header-anchor" href="#返回结果-10" aria-hidden="true">#</a> 返回结果</h4><p>同<a href="%E6%9F%A5%E7%9C%8B%E6%8C%87%E5%AE%9A%E4%BB%A3%E7%A0%81%E5%BA%93%E7%9A%84%E6%8C%87%E5%AE%9A%E6%89%AB%E6%8F%8F%E6%96%B9%E6%A1%88">查看指定代码库的指定扫描方案</a>的返回结果一致</p><h2 id="查看指定代码库的扫描方案的代码扫描配置" tabindex="-1"><a class="header-anchor" href="#查看指定代码库的扫描方案的代码扫描配置" aria-hidden="true">#</a> 查看指定代码库的扫描方案的代码扫描配置</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/main/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/schemes/&lt;scheme_id&gt;/lintconf/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="返回结果-11" tabindex="-1"><a class="header-anchor" href="#返回结果-11" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;id&quot;: 1,
        &quot;enabled&quot;: true,
        &quot;checkprofile&quot;: {
            &quot;id&quot;: 1,
            &quot;profile_type&quot;: 1,
            &quot;custom_checkpackage&quot;: 1,
            &quot;checkpackages&quot;: [
                1
            ]
        },
        &quot;scan_scheme&quot;: 1
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="更新指定代码库的指定方案的代码扫描配置" tabindex="-1"><a class="header-anchor" href="#更新指定代码库的指定方案的代码扫描配置" aria-hidden="true">#</a> 更新指定代码库的指定方案的代码扫描配置</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>PUT /server/main/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/schemes/&lt;scheme_id&gt;/lintconf/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="参数列表-6" tabindex="-1"><a class="header-anchor" href="#参数列表-6" aria-hidden="true">#</a> 参数列表</h4><table><thead><tr><th>参数</th><th>类型</th><th>描述</th></tr></thead><tbody><tr><td>enabled</td><td>bool</td><td>必填，是否开启代码扫描</td></tr></tbody></table><h4 id="返回结果-12" tabindex="-1"><a class="header-anchor" href="#返回结果-12" aria-hidden="true">#</a> 返回结果</h4><p>同<a href="%E6%8C%87%E5%AE%9A%E4%BB%A3%E7%A0%81%E5%BA%93%E7%9A%84%E6%8C%87%E5%AE%9A%E6%96%B9%E6%A1%88%E7%9A%84%E4%BB%A3%E7%A0%81%E6%89%AB%E6%8F%8F%E9%85%8D%E7%BD%AE">指定代码库的指定方案的代码扫描配置</a>的返回结果一致</p><h2 id="查看指定代码库的扫描方案的代码度量配置" tabindex="-1"><a class="header-anchor" href="#查看指定代码库的扫描方案的代码度量配置" aria-hidden="true">#</a> 查看指定代码库的扫描方案的代码度量配置</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/main/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/schemes/&lt;scheme_id&gt;/metricconf/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="返回结果-13" tabindex="-1"><a class="header-anchor" href="#返回结果-13" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;id&quot;: 1,
        &quot;cc_scan_enabled&quot;: false,
        &quot;min_ccn&quot;: 20,
        &quot;dup_scan_enabled&quot;: false,
        &quot;dup_block_length_min&quot;: 120,
        &quot;dup_block_length_max&quot;: null,
        &quot;dup_min_dup_times&quot;: 2,
        &quot;dup_max_dup_times&quot;: null,
        &quot;dup_min_midd_rate&quot;: 5,
        &quot;dup_min_high_rate&quot;: 11,
        &quot;dup_min_exhi_rate&quot;: 20,
        &quot;dup_issue_limit&quot;: 1000,
        &quot;cloc_scan_enabled&quot;: false,
        &quot;scan_scheme&quot;: 1
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="更新指定代码库的指定方案的代码度量配置" tabindex="-1"><a class="header-anchor" href="#更新指定代码库的指定方案的代码度量配置" aria-hidden="true">#</a> 更新指定代码库的指定方案的代码度量配置</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>PUT /server/main/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/schemes/&lt;scheme_id&gt;/metricconf/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="参数列表-7" tabindex="-1"><a class="header-anchor" href="#参数列表-7" aria-hidden="true">#</a> 参数列表</h4><table><thead><tr><th>参数</th><th>类型</th><th>描述</th></tr></thead><tbody><tr><td>cc_scan_enabled</td><td>bool</td><td>选填，圈复杂度扫描开关</td></tr><tr><td>min_ccn</td><td>int</td><td>选填，最小圈复杂度</td></tr><tr><td>dup_scan_enabled</td><td>bool</td><td>选填，重复代码扫描开关</td></tr><tr><td>dup_block_length_min</td><td>int</td><td>选填，重复块最小长度</td></tr><tr><td>dup_block_length_max</td><td>int</td><td>选填，重复块最大长度</td></tr><tr><td>dup_max_dup_times</td><td>int</td><td>选填，最大重复次数</td></tr><tr><td>dup_min_midd_rate</td><td>int</td><td>选填，中风险最小重复率</td></tr><tr><td>dup_min_high_rate</td><td>int</td><td>选填，高风险最小重复率</td></tr><tr><td>dup_min_exhi_rate</td><td>int</td><td>选填，极高风险风险最小重复率</td></tr><tr><td>dup_issue_limit</td><td>int</td><td>选填，上报重复代码块数上限</td></tr><tr><td>cloc_scan_enabled</td><td>boolean</td><td>选填，代码统计扫描开关</td></tr></tbody></table><h4 id="返回结果-14" tabindex="-1"><a class="header-anchor" href="#返回结果-14" aria-hidden="true">#</a> 返回结果</h4><p>同<a href="%E6%8C%87%E5%AE%9A%E4%BB%A3%E7%A0%81%E5%BA%93%E7%9A%84%E6%8C%87%E5%AE%9A%E6%96%B9%E6%A1%88%E7%9A%84%E4%BB%A3%E7%A0%81%E5%BA%A6%E9%87%8F%E9%85%8D%E7%BD%AE">指定代码库的指定方案的代码度量配置</a>的返回结果一致</p><h2 id="查看指定代码库的扫描方案的过滤路径列表" tabindex="-1"><a class="header-anchor" href="#查看指定代码库的扫描方案的过滤路径列表" aria-hidden="true">#</a> 查看指定代码库的扫描方案的过滤路径列表</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/main/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/schemes/&lt;scheme_id&gt;/scandirs/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="返回结果-15" tabindex="-1"><a class="header-anchor" href="#返回结果-15" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;count&quot;: 1,
        &quot;next&quot;: null,
        &quot;previous&quot;: null,
        &quot;results&quot;: [
            {
                &quot;id&quot;: 1,
                &quot;dir_path&quot;: &quot;test/*&quot;,
                &quot;path_type&quot;: 1,
                &quot;scan_type&quot;: 1,
                &quot;scan_scheme&quot;: 1
            }
        ]
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="创建指定代码库的指定方案的过滤路径列表" tabindex="-1"><a class="header-anchor" href="#创建指定代码库的指定方案的过滤路径列表" aria-hidden="true">#</a> 创建指定代码库的指定方案的过滤路径列表</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>POST /server/main/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/schemes/&lt;scheme_id&gt;/scandirs/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="参数列表-8" tabindex="-1"><a class="header-anchor" href="#参数列表-8" aria-hidden="true">#</a> 参数列表</h4><table><thead><tr><th>参数</th><th>类型</th><th>描述</th></tr></thead><tbody><tr><td>dir_path</td><td>str</td><td>必填，指定过滤路径</td></tr><tr><td>path_type</td><td>int</td><td>选填，路径格式，1表示通配符，2表示正则表达式，默认为通配符</td></tr><tr><td>scan_type</td><td>int</td><td>选填，扫描类型，1表示包含，2表示排除</td></tr></tbody></table><h4 id="返回结果-16" tabindex="-1"><a class="header-anchor" href="#返回结果-16" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;id&quot;: 13,
        &quot;dir_path&quot;: &quot;test/*.py&quot;,
        &quot;path_type&quot;: 1,
        &quot;scan_type&quot;: 1,
        &quot;scan_scheme&quot;: 36
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 201
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="查看指定代码库的扫描方案的指定过滤路径" tabindex="-1"><a class="header-anchor" href="#查看指定代码库的扫描方案的指定过滤路径" aria-hidden="true">#</a> 查看指定代码库的扫描方案的指定过滤路径</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/main/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/schemes/&lt;scheme_id&gt;/scandirs/&lt;dir_id&gt;/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="返回结果-17" tabindex="-1"><a class="header-anchor" href="#返回结果-17" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;id&quot;: 1,
        &quot;dir_path&quot;: &quot;test/*.py&quot;,
        &quot;path_type&quot;: 1,
        &quot;scan_type&quot;: 1,
        &quot;scan_scheme&quot;: 1
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="更新指定代码库的指定方案的指定过滤路径" tabindex="-1"><a class="header-anchor" href="#更新指定代码库的指定方案的指定过滤路径" aria-hidden="true">#</a> 更新指定代码库的指定方案的指定过滤路径</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>PUT /server/main/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/schemes/&lt;scheme_id&gt;/scandirs/&lt;dir_id&gt;/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="参数列表-9" tabindex="-1"><a class="header-anchor" href="#参数列表-9" aria-hidden="true">#</a> 参数列表</h4><table><thead><tr><th>参数</th><th>类型</th><th>描述</th></tr></thead><tbody><tr><td>dir_path</td><td>str</td><td>必填，指定过滤路径</td></tr><tr><td>path_type</td><td>int</td><td>选填，路径格式，1表示通配符，2表示正则表达式，默认为通配符</td></tr><tr><td>scan_type</td><td>int</td><td>选填，扫描类型，1表示包含，2表示排除</td></tr></tbody></table><h4 id="返回结果-18" tabindex="-1"><a class="header-anchor" href="#返回结果-18" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;id&quot;: 13,
        &quot;dir_path&quot;: &quot;test/*.py&quot;,
        &quot;path_type&quot;: 1,
        &quot;scan_type&quot;: 1,
        &quot;scan_scheme&quot;: 36
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 201
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="删除指定代码库的指定方案的指定过滤路径" tabindex="-1"><a class="header-anchor" href="#删除指定代码库的指定方案的指定过滤路径" aria-hidden="true">#</a> 删除指定代码库的指定方案的指定过滤路径</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>DELETE /server/main/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/schemes/&lt;scheme_id&gt;/scandirs/&lt;dir_id&gt;/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="返回结果-19" tabindex="-1"><a class="header-anchor" href="#返回结果-19" aria-hidden="true">#</a> 返回结果</h4><p>无</p>`,103),s=[u];function a(l,o){return t(),i("div",null,s)}const v=e(d,[["render",a],["__file","项目管理模块接口.html.vue"]]);export{v as default};
