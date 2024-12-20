import{_ as t,o as e,c as i,e as u}from"./app-697cd87e.js";const n={},d=u(`<h1 id="代码扫描数据管理" tabindex="-1"><a class="header-anchor" href="#代码扫描数据管理" aria-hidden="true">#</a> 代码扫描数据管理</h1><h2 id="查看扫描问题列表" tabindex="-1"><a class="header-anchor" href="#查看扫描问题列表" aria-hidden="true">#</a> 查看扫描问题列表</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/analysis/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/projects/&lt;project_id&gt;/codelint/issues/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="参数" tabindex="-1"><a class="header-anchor" href="#参数" aria-hidden="true">#</a> 参数</h4><table><thead><tr><th>参数</th><th>类型</th><th>描述</th></tr></thead><tbody><tr><td>state</td><td>str</td><td>选填，问题状态, 1为未处理，2为已处理，3为关闭，可多选，格式为1,2,3</td></tr><tr><td>severity</td><td>str</td><td>选填，严重程度, 1为致命，2为错误，3为警告，4为提示，可多选，格式为1,2,3,4</td></tr><tr><td>resolution</td><td>str</td><td>选填，解决方式, 0为无，1为修复，2为无需修复，3为误报，4为重复单过滤，5为路径过滤，6为规则移除</td></tr><tr><td>author</td><td>str</td><td>选填，问题责任人</td></tr><tr><td>scan_open</td><td>int</td><td>选填，发现问题的扫描编号</td></tr><tr><td>scan_fix</td><td>int</td><td>选填，修复问题的扫描编号</td></tr><tr><td>ci_time_gte</td><td>str</td><td>选填，修复问题的起始时间，格式为&quot;2021-01-01 00:00:00&quot;</td></tr><tr><td>ci_time_lte</td><td>str</td><td>选填，修复问题的结束时间</td></tr><tr><td>file_path</td><td>str</td><td>选填，文件路径</td></tr><tr><td>checkrule_display_name</td><td>str</td><td>选填，检查规则名</td></tr><tr><td>checkpackage</td><td>int</td><td>选填，问题所属的规则包</td></tr></tbody></table><h4 id="返回结果" tabindex="-1"><a class="header-anchor" href="#返回结果" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;count&quot;: 1,
        &quot;next&quot;: null,
        &quot;previous&quot;: null,
        &quot;results&quot;: [
            {
                &quot;id&quot;: 1,
                &quot;file_path&quot;: &quot;test/demo.py&quot;,
                &quot;project&quot;: 1,
                &quot;repo&quot;: 1,
                &quot;checkrule_real_name&quot;: &quot;xxx&quot;,
                &quot;checkrule_display_name&quot;: &quot;xxx&quot;,
                &quot;checktool_name&quot;: &quot;xxx&quot;,
                &quot;msg&quot;: &quot;xxx&quot;,
                &quot;state&quot;: 3,
                &quot;resolution&quot;: 1,
                &quot;author&quot;: &quot;author&quot;,
                &quot;author_email&quot;: null,
                &quot;severity&quot;: 2,
                &quot;revision&quot;: &quot;revision&quot;,
                &quot;ci_time&quot;: &quot;2021-02-02T13:31:38+08:00&quot;,
                &quot;file_owners&quot;: null,
                &quot;is_external&quot;: false,
                &quot;scm_url&quot;: &quot;&quot;,
                &quot;real_file_path&quot;: &quot;&quot;,
                &quot;scan_open&quot;: 1,
                &quot;scan_fix&quot;: 2,
                &quot;fixed_time&quot;: &quot;2021-02-19T15:25:15.152350+08:00&quot;
            }
        ]
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="查看问题详情" tabindex="-1"><a class="header-anchor" href="#查看问题详情" aria-hidden="true">#</a> 查看问题详情</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/analysis/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/projects/&lt;project_id&gt;/codelint/issues/&lt;issue_id&gt;/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="返回结果-1" tabindex="-1"><a class="header-anchor" href="#返回结果-1" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;id&quot;: 1,
        &quot;issue_details&quot;: [
            {
                &quot;id&quot;: 1,
                &quot;issue_refers&quot;: [],
                &quot;creator&quot;: null,
                &quot;modifier&quot;: null,
                &quot;deleted_time&quot;: null,
                &quot;deleter&quot;: null,
                &quot;issuedetail_uuid&quot;: &quot;0fcc376e-7283-11eb-bd53-5254005e71ca&quot;,
                &quot;checkrule_real_name&quot;: &quot;xxx&quot;,
                &quot;checktool_name&quot;: &quot;xxx&quot;,
                &quot;author&quot;: &quot;author&quot;,
                &quot;author_email&quot;: null,
                &quot;line&quot;: 1809,
                &quot;column&quot;: 15,
                &quot;scan_revision&quot;: &quot;scan_revision&quot;,
                &quot;revision&quot;: &quot;revision&quot;,
                &quot;ci_time&quot;: &quot;2021-02-02T13:31:38+08:00&quot;,
                &quot;real_revision&quot;: &quot;&quot;,
                &quot;created_time&quot;: &quot;2021-02-19T15:21:19.625658+08:00&quot;,
                &quot;modified_time&quot;: &quot;2021-02-19T15:21:19.625662+08:00&quot;,
                &quot;issue&quot;: null,
                &quot;project&quot;: 1
            }
        ],
        &quot;is_external&quot;: false,
        &quot;repo&quot;: 1,
        &quot;author&quot;: &quot;author&quot;,
        &quot;created_time&quot;: &quot;2021-02-19T15:21:19.625685+08:00&quot;,
        &quot;creator&quot;: null,
        &quot;modifier&quot;: null,
        &quot;deleted_time&quot;: null,
        &quot;deleter&quot;: null,
        &quot;file_path&quot;: &quot;test/demo.py&quot;,
        &quot;file_hash&quot;: &quot;xxx&quot;,
        &quot;scm_url&quot;: &quot;&quot;,
        &quot;real_file_path&quot;: &quot;&quot;,
        &quot;checkrule_gid&quot;: 1,
        &quot;checkrule_real_name&quot;: &quot;xxx&quot;,
        &quot;checkrule_display_name&quot;: &quot;xxx&quot;,
        &quot;checkrule_rule_title&quot;: &quot;xxx&quot;,
        &quot;checktool_name&quot;: &quot;xxx&quot;,
        &quot;category&quot;: 7,
        &quot;state&quot;: 3,
        &quot;resolution&quot;: 1,
        &quot;scan_revision&quot;: null,
        &quot;severity&quot;: 2,
        &quot;language&quot;: &quot;python&quot;,
        &quot;revision&quot;: &quot;revision&quot;,
        &quot;ci_time&quot;: &quot;2021-02-02T13:31:38+08:00&quot;,
        &quot;file_owners&quot;: null,
        &quot;fixed_time&quot;: &quot;2021-02-19T15:25:15.152350+08:00&quot;,
        &quot;tapd_ws_id&quot;: null,
        &quot;tapd_bug_id&quot;: null,
        &quot;modified_time&quot;: &quot;2021-02-19T15:25:17.807478+08:00&quot;,
        &quot;project&quot;: 1,
        &quot;scan_open&quot;: 1,
        &quot;scan_fix&quot;: 2
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;xxx&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="查看每次扫描的问题列表" tabindex="-1"><a class="header-anchor" href="#查看每次扫描的问题列表" aria-hidden="true">#</a> 查看每次扫描的问题列表</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/analysis/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/projects/&lt;project_id&gt;/codelint/scans/&lt;scan_id&gt;/issues/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="参数-1" tabindex="-1"><a class="header-anchor" href="#参数-1" aria-hidden="true">#</a> 参数</h4><table><thead><tr><th>参数</th><th>类型</th><th>描述</th></tr></thead><tbody><tr><td>state</td><td>str</td><td>选填，问题状态, 1为未处理，2为已处理，3为关闭，可多选，格式为1,2,3</td></tr><tr><td>severity</td><td>str</td><td>选填，严重程度, 1为致命，2为错误，3为警告，4为提示，可多选，格式为1,2,3,4</td></tr><tr><td>resolution</td><td>str</td><td>选填，解决方式, 0为无，1为修复，2为无需修复，3为误报，4为重复单过滤，5为路径过滤，6为规则移除</td></tr><tr><td>author</td><td>str</td><td>选填，问题责任人</td></tr><tr><td>scan_open_id</td><td>int</td><td>选填，发现问题的扫描编号</td></tr><tr><td>scan_fix_id</td><td>int</td><td>选填，修复问题的扫描编号</td></tr><tr><td>ci_time_gte</td><td>str</td><td>选填，修复问题的起始时间</td></tr><tr><td>ci_time_lte</td><td>str</td><td>选填，修复问题的结束时间</td></tr><tr><td>file_path</td><td>str</td><td>选填，文件路径</td></tr><tr><td>checkrule_display_name</td><td>str</td><td>选填，检查规则名</td></tr><tr><td>checkpackage</td><td>int</td><td>选填，问题所属的规则包</td></tr></tbody></table><h4 id="返回结果-2" tabindex="-1"><a class="header-anchor" href="#返回结果-2" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;count&quot;: 1,
        &quot;next&quot;: null,
        &quot;previous&quot;: null,
        &quot;results&quot;: [
            {
                &quot;id&quot;: 1,
                &quot;repo_id&quot;: 1,
                &quot;project_id&quot;: 1,
                &quot;scan_time&quot;: &quot;2021-03-11T20:46:44.171607+08:00&quot;,
                &quot;file_path&quot;: &quot;test/demo.py&quot;,
                &quot;scm_url&quot;: &quot;&quot;,
                &quot;real_file_path&quot;: &quot;&quot;,
                &quot;line&quot;: 21,
                &quot;column&quot;: 68,
                &quot;checkrule_gid&quot;: 1,
                &quot;checkrule_real_name&quot;: &quot;xxx&quot;,
                &quot;checkrule_display_name&quot;: &quot;xxx&quot;,
                &quot;checkrule_rule_title&quot;: &quot;xxx&quot;,
                &quot;checktool_name&quot;: &quot;xxx&quot;,
                &quot;category&quot;: 7,
                &quot;msg&quot;: &quot;xxx&quot;,
                &quot;state&quot;: 1,
                &quot;resolution&quot;: null,
                &quot;author&quot;: &quot;author&quot;,
                &quot;scan_open_id&quot;: 1,
                &quot;scan_fix_id&quot;: null,
                &quot;issuedetail_uuid&quot;: &quot;26d7ba88-8268-11eb-a304-5254005e71ca&quot;,
                &quot;scan_revision&quot;: &quot;scan_revision&quot;,
                &quot;real_revision&quot;: &quot;&quot;,
                &quot;severity&quot;: 2,
                &quot;language&quot;: &quot;python&quot;,
                &quot;revision&quot;: &quot;revision&quot;,
                &quot;ci_time&quot;: &quot;2019-07-01T10:28:19+08:00&quot;,
                &quot;file_owners&quot;: null,
                &quot;created_time&quot;: &quot;2021-03-11T20:49:00.539537+08:00&quot;,
                &quot;fixed_time&quot;: null
            }
        ]
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;xxx&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="查看指定cr扫描的问题列表" tabindex="-1"><a class="header-anchor" href="#查看指定cr扫描的问题列表" aria-hidden="true">#</a> 查看指定CR扫描的问题列表</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/analysis/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/projects/&lt;project_id&gt;/codelint/crscans/&lt;scan_id&gt;/issues/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="参数-2" tabindex="-1"><a class="header-anchor" href="#参数-2" aria-hidden="true">#</a> 参数</h4><table><thead><tr><th>参数</th><th>类型</th><th>描述</th></tr></thead><tbody><tr><td>state</td><td>str</td><td>选填，问题状态, 1为未处理，2为已处理，3为关闭，可多选，格式为1,2,3</td></tr><tr><td>severity</td><td>str</td><td>选填，严重程度, 1为致命，2为错误，3为警告，4为提示，可多选，格式为1,2,3,4</td></tr><tr><td>resolution</td><td>str</td><td>选填，解决方式, 0为无，1为修复，2为无需修复，3为误报，4为重复单过滤，5为路径过滤，6为规则移除</td></tr><tr><td>author</td><td>str</td><td>选填，问题责任人</td></tr><tr><td>scan_open_id</td><td>int</td><td>选填，发现问题的扫描编号</td></tr><tr><td>scan_fix_id</td><td>int</td><td>选填，修复问题的扫描编号</td></tr><tr><td>ci_time_gte</td><td>str</td><td>选填，修复问题的起始时间</td></tr><tr><td>ci_time_lte</td><td>str</td><td>选填，修复问题的结束时间</td></tr><tr><td>file_path</td><td>str</td><td>选填，文件路径</td></tr><tr><td>checkrule_display_name</td><td>str</td><td>选填，检查规则名</td></tr><tr><td>checkpackage</td><td>int</td><td>选填，问题所属的规则包</td></tr></tbody></table><h4 id="返回结果-3" tabindex="-1"><a class="header-anchor" href="#返回结果-3" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;count&quot;: 1,
        &quot;next&quot;: null,
        &quot;previous&quot;: null,
        &quot;results&quot;: [
            {
                &quot;id&quot;: 1,
                &quot;repo_id&quot;: 1,
                &quot;project_id&quot;: 1,
                &quot;scan_time&quot;: &quot;2021-03-11T20:46:44.171607+08:00&quot;,
                &quot;file_path&quot;: &quot;test/demo.py&quot;,
                &quot;scm_url&quot;: &quot;&quot;,
                &quot;real_file_path&quot;: &quot;&quot;,
                &quot;line&quot;: 21,
                &quot;column&quot;: 68,
                &quot;checkrule_gid&quot;: 1,
                &quot;checkrule_real_name&quot;: &quot;xxx&quot;,
                &quot;checkrule_display_name&quot;: &quot;xxx&quot;,
                &quot;checkrule_rule_title&quot;: &quot;xxx&quot;,
                &quot;checktool_name&quot;: &quot;xxx&quot;,
                &quot;category&quot;: 7,
                &quot;msg&quot;: &quot;xxx&quot;,
                &quot;state&quot;: 1,
                &quot;resolution&quot;: null,
                &quot;author&quot;: &quot;author&quot;,
                &quot;scan_open_id&quot;: 1,
                &quot;scan_fix_id&quot;: null,
                &quot;issuedetail_uuid&quot;: &quot;26d7ba88-8268-11eb-a304-5254005e71ca&quot;,
                &quot;scan_revision&quot;: &quot;scan_revision&quot;,
                &quot;real_revision&quot;: &quot;&quot;,
                &quot;severity&quot;: 2,
                &quot;language&quot;: &quot;python&quot;,
                &quot;revision&quot;: &quot;revision&quot;,
                &quot;ci_time&quot;: &quot;2019-07-01T10:28:19+08:00&quot;,
                &quot;file_owners&quot;: null,
                &quot;created_time&quot;: &quot;2021-03-11T20:49:00.539537+08:00&quot;,
                &quot;fixed_time&quot;: null
            }
        ]
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;xxx&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div>`,23),s=[d];function o(l,a){return e(),i("div",null,s)}const q=t(n,[["render",o],["__file","代码扫描数据模块接口.html.vue"]]);export{q as default};
