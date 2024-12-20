import{_ as t,o as e,c as i,e as n}from"./app-697cd87e.js";const d={},u=n(`<h1 id="代码度量数据管理" tabindex="-1"><a class="header-anchor" href="#代码度量数据管理" aria-hidden="true">#</a> 代码度量数据管理</h1><h2 id="查看指定项目的圈复杂度文件列表" tabindex="-1"><a class="header-anchor" href="#查看指定项目的圈复杂度文件列表" aria-hidden="true">#</a> 查看指定项目的圈复杂度文件列表</h2><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>GET /server/analysis/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/projects/&lt;project_id&gt;/codemetric/ccfiles/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="参数列表" tabindex="-1"><a class="header-anchor" href="#参数列表" aria-hidden="true">#</a> 参数列表</h4><table><thead><tr><th>参数</th><th>类型</th><th>描述</th></tr></thead><tbody><tr><td>state</td><td>str</td><td>选填，问题状态, 1为未处理，2为已处理，3为关闭，可多选，格式为1,2,3</td></tr><tr><td>change_type</td><td>str</td><td>选填，圈复杂度变化情况，0为无，1为新增，2为删除，3为无变化，可多选，格式为1,2,3</td></tr><tr><td>author</td><td>str</td><td>选填，问题责任人</td></tr><tr><td>last_modifier</td><td>str</td><td>选填，最近修改人</td></tr><tr><td>file_path</td><td>str</td><td>选填，文件路径</td></tr><tr><td>scan_open</td><td>int</td><td>选填，发现问题的扫描编号</td></tr><tr><td>scan_close</td><td>int</td><td>选填，修复问题的扫描编号</td></tr><tr><td>worse</td><td>boolean</td><td>选填，圈复杂度是否恶化</td></tr><tr><td>over_cc_sum_gte</td><td>int</td><td>选填， 圈复杂度总和最小值</td></tr><tr><td>over_cc_sum_lte</td><td>int</td><td>选填，圈复杂度总和最大值</td></tr><tr><td>over_cc_avg_gte</td><td>int</td><td>选填，平均圈复杂度最小值</td></tr><tr><td>over_cc_avg_lte</td><td>int</td><td>选填，平均圈复杂度总和最大值</td></tr><tr><td>over_cc_func_count_gte</td><td>int</td><td>选填，超标圈复杂度函数个数最小值</td></tr><tr><td>over_cc_func_count_lte</td><td>int</td><td>选填，超标圈复杂度函数个数最大值</td></tr></tbody></table><h4 id="返回参数" tabindex="-1"><a class="header-anchor" href="#返回参数" aria-hidden="true">#</a> 返回参数</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;count&quot;: 1,
        &quot;next&quot;: null,
        &quot;previous&quot;: null,
        &quot;results&quot;: [
            {
                &quot;id&quot;: 1,
                &quot;repo&quot;: 1,
                &quot;created_time&quot;: &quot;2021-02-19T15:30:20.968525+08:00&quot;,
                &quot;creator&quot;: null,
                &quot;modified_time&quot;: &quot;2021-02-19T15:30:20.968532+08:00&quot;,
                &quot;modifier&quot;: null,
                &quot;deleted_time&quot;: null,
                &quot;deleter&quot;: null,
                &quot;ccn&quot;: 22,
                &quot;g_cc_hash&quot;: null,
                &quot;cc_hash&quot;: null,
                &quot;file_path&quot;: &quot;test/demo.py&quot;,
                &quot;func_name&quot;: &quot;test_func&quot;,
                &quot;func_param_num&quot;: 4,
                &quot;long_name&quot;: &quot;test_func( project , result_data , scan , task_params )&quot;,
                &quot;change_type&quot;: 0,
                &quot;status&quot;: 1,
                &quot;last_modifier&quot;: &quot;author&quot;,
                &quot;author&quot;: null,
                &quot;related_modifiers&quot;: &quot;author,author2&quot;,
                &quot;is_tapdbug&quot;: false,
                &quot;ignore_time&quot;: null,
                &quot;is_latest&quot;: true,
                &quot;language&quot;: &quot;python&quot;,
                &quot;revision&quot;: &quot;revision&quot;,
                &quot;ci_time&quot;: &quot;2020-03-18T19:46:48+08:00&quot;,
                &quot;diff_ccn&quot;: null,
                &quot;project&quot;: 1,
                &quot;scan_open&quot;: 1,
                &quot;scan_close&quot;: null
            }
        ]
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="查看指定项目的圈复杂度文件问题列表" tabindex="-1"><a class="header-anchor" href="#查看指定项目的圈复杂度文件问题列表" aria-hidden="true">#</a> 查看指定项目的圈复杂度文件问题列表</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/analysis/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/projects/&lt;project_id&gt;/codemetric/ccfiles/&lt;file_id&gt;/ccissues/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="参数列表-1" tabindex="-1"><a class="header-anchor" href="#参数列表-1" aria-hidden="true">#</a> 参数列表</h4><table><thead><tr><th>参数</th><th>类型</th><th>描述</th></tr></thead><tbody><tr><td>status</td><td>str</td><td>选填，问题状态，1为需要关注，2为无需关注，可多选，格式为1,2,3</td></tr><tr><td>change_type</td><td>str</td><td>选填，圈复杂度变化情况，0为无，1为新增，2为删除，3为无变化，可多选，格式为1,2,3</td></tr><tr><td>author</td><td>str</td><td>选填，问题责任人</td></tr><tr><td>last_modifier</td><td>str</td><td>选填，最近修改人</td></tr><tr><td>file_path</td><td>str</td><td>选填，文件路径</td></tr><tr><td>ccn_gte</td><td>str</td><td>选填，圈复杂度最小值</td></tr><tr><td>ccn_lte</td><td>str</td><td>选填，圈复杂度最大值</td></tr></tbody></table><h4 id="返回结果" tabindex="-1"><a class="header-anchor" href="#返回结果" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;count&quot;: 1,
        &quot;next&quot;: null,
        &quot;previous&quot;: null,
        &quot;results&quot;: [
            {
                &quot;id&quot;: 1,
                &quot;repo&quot;: 1,
                &quot;created_time&quot;: &quot;2021-02-19T15:30:20.968525+08:00&quot;,
                &quot;creator&quot;: null,
                &quot;modified_time&quot;: &quot;2021-02-19T15:30:20.968532+08:00&quot;,
                &quot;modifier&quot;: null,
                &quot;deleted_time&quot;: null,
                &quot;deleter&quot;: null,
                &quot;ccn&quot;: 22,
                &quot;g_cc_hash&quot;: null,
                &quot;cc_hash&quot;: null,
                &quot;file_path&quot;: &quot;test/demo.py&quot;,
                &quot;func_name&quot;: &quot;test_func&quot;,
                &quot;func_param_num&quot;: 4,
                &quot;long_name&quot;: &quot;test_func( project , result_data , scan , task_params )&quot;,
                &quot;change_type&quot;: 0,
                &quot;status&quot;: 1,
                &quot;last_modifier&quot;: &quot;author&quot;,
                &quot;author&quot;: null,
                &quot;related_modifiers&quot;: &quot;author,author2&quot;,
                &quot;is_tapdbug&quot;: false,
                &quot;ignore_time&quot;: null,
                &quot;is_latest&quot;: true,
                &quot;language&quot;: &quot;python&quot;,
                &quot;revision&quot;: &quot;revision&quot;,
                &quot;ci_time&quot;: &quot;2020-03-18T19:46:48+08:00&quot;,
                &quot;diff_ccn&quot;: null,
                &quot;project&quot;: 1,
                &quot;scan_open&quot;: 1,
                &quot;scan_close&quot;: null
            }
        ]
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="查看指定项目的圈复杂度问题列表" tabindex="-1"><a class="header-anchor" href="#查看指定项目的圈复杂度问题列表" aria-hidden="true">#</a> 查看指定项目的圈复杂度问题列表</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/analysis/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/projects/&lt;project_id&gt;/codemetric/ccissues/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="参数列表-2" tabindex="-1"><a class="header-anchor" href="#参数列表-2" aria-hidden="true">#</a> 参数列表</h4><table><thead><tr><th>参数</th><th>类型</th><th>描述</th></tr></thead><tbody><tr><td>status</td><td>str</td><td>选填，问题状态，1为需要关注，2为无需关注，可多选，格式为1,2,3</td></tr><tr><td>change_type</td><td>str</td><td>选填，圈复杂度变化情况，0为无，1为新增，2为删除，3为无变化，可多选，格式为1,2,3</td></tr><tr><td>author</td><td>str</td><td>选填，问题责任人</td></tr><tr><td>last_modifier</td><td>str</td><td>选填，最近修改人</td></tr><tr><td>file_path</td><td>str</td><td>选填，文件路径</td></tr><tr><td>ccn_gte</td><td>str</td><td>选填，圈复杂度最小值</td></tr><tr><td>ccn_lte</td><td>str</td><td>选填，圈复杂度最大值</td></tr></tbody></table><h4 id="返回结果-1" tabindex="-1"><a class="header-anchor" href="#返回结果-1" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;count&quot;: 1,
        &quot;next&quot;: null,
        &quot;previous&quot;: null,
        &quot;results&quot;: [
            {
                &quot;id&quot;: 1,
                &quot;repo&quot;: 1,
                &quot;created_time&quot;: &quot;2021-02-19T15:30:20.968525+08:00&quot;,
                &quot;creator&quot;: null,
                &quot;modified_time&quot;: &quot;2021-02-19T15:30:20.968532+08:00&quot;,
                &quot;modifier&quot;: null,
                &quot;deleted_time&quot;: null,
                &quot;deleter&quot;: null,
                &quot;ccn&quot;: 22,
                &quot;g_cc_hash&quot;: null,
                &quot;cc_hash&quot;: null,
                &quot;file_path&quot;: &quot;test/demo.py&quot;,
                &quot;func_name&quot;: &quot;test_func&quot;,
                &quot;func_param_num&quot;: 4,
                &quot;long_name&quot;: &quot;test_func( project , result_data , scan , task_params )&quot;,
                &quot;change_type&quot;: 0,
                &quot;status&quot;: 1,
                &quot;last_modifier&quot;: &quot;author&quot;,
                &quot;author&quot;: null,
                &quot;related_modifiers&quot;: &quot;author,author2&quot;,
                &quot;is_tapdbug&quot;: false,
                &quot;ignore_time&quot;: null,
                &quot;is_latest&quot;: true,
                &quot;language&quot;: &quot;python&quot;,
                &quot;revision&quot;: &quot;revision&quot;,
                &quot;ci_time&quot;: &quot;2020-03-18T19:46:48+08:00&quot;,
                &quot;diff_ccn&quot;: null,
                &quot;project&quot;: 1,
                &quot;scan_open&quot;: 1,
                &quot;scan_close&quot;: null
            }
        ]
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="查看指定项目指定扫描的圈复杂度文件列表" tabindex="-1"><a class="header-anchor" href="#查看指定项目指定扫描的圈复杂度文件列表" aria-hidden="true">#</a> 查看指定项目指定扫描的圈复杂度文件列表</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/analysis/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/projects/&lt;project_id&gt;/codemetric/scans/&lt;scan_id&gt;/ccfiles/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="参数列表-3" tabindex="-1"><a class="header-anchor" href="#参数列表-3" aria-hidden="true">#</a> 参数列表</h4><table><thead><tr><th>参数</th><th>类型</th><th>描述</th></tr></thead><tbody><tr><td>state</td><td>str</td><td>选填，问题状态, 1为未处理，2为已处理，3为关闭，可多选，格式为1,2,3</td></tr><tr><td>change_type</td><td>str</td><td>选填，圈复杂度变化情况，0为无，1为新增，2为删除，3为无变化，可多选，格式为1,2,3</td></tr><tr><td>author</td><td>str</td><td>选填，问题责任人</td></tr><tr><td>last_modifier</td><td>str</td><td>选填，最近修改人</td></tr><tr><td>file_path</td><td>str</td><td>选填，文件路径</td></tr><tr><td>scan_open_id</td><td>int</td><td>选填，发现问题的扫描编号</td></tr><tr><td>scan_close_id</td><td>int</td><td>选填，修复问题的扫描编号</td></tr><tr><td>worse</td><td>boolean</td><td>选填，圈复杂度是否恶化</td></tr><tr><td>over_cc_sum_gte</td><td>int</td><td>选填，圈复杂度总和最小值</td></tr><tr><td>over_cc_sum_lte</td><td>int</td><td>选填，圈复杂度总和最大值</td></tr><tr><td>over_cc_avg_gte</td><td>int</td><td>选填，平均圈复杂度最小值</td></tr><tr><td>over_cc_avg_lte</td><td>int</td><td>选填，平均圈复杂度总和最大值</td></tr><tr><td>over_cc_func_count_gte</td><td>int</td><td>选填，超标圈复杂度函数个数最小值</td></tr><tr><td>over_cc_func_count_lte</td><td>int</td><td>选填，超标圈复杂度函数个数最大值</td></tr></tbody></table><h4 id="返回结果-2" tabindex="-1"><a class="header-anchor" href="#返回结果-2" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;count&quot;: 32,
        &quot;next&quot;: null,
        &quot;previous&quot;: null,
        &quot;results&quot;: [
            {
                &quot;id&quot;: 1,
                &quot;repo&quot;: 1,
                &quot;tapd_url&quot;: null,
                &quot;created_time&quot;: &quot;2020-06-02T10:59:09.418250+08:00&quot;,
                &quot;creator&quot;: null,
                &quot;modified_time&quot;: &quot;2020-06-03T16:17:40.892224+08:00&quot;,
                &quot;modifier&quot;: null,
                &quot;deleted_time&quot;: null,
                &quot;deleter&quot;: null,
                &quot;over_func_cc&quot;: 0,
                &quot;over_cc_sum&quot;: 0,
                &quot;over_cc_avg&quot;: 0,
                &quot;over_cc_func_count&quot;: 0,
                &quot;diff_over_func_cc&quot;: 0,
                &quot;diff_over_cc_sum&quot;: 0,
                &quot;diff_over_cc_avg&quot;: 0,
                &quot;diff_over_cc_func_count&quot;: 0,
                &quot;worse&quot;: false,
                &quot;file_path&quot;: &quot;test/demo.py&quot;,
                &quot;state&quot;: 3,
                &quot;change_type&quot;: 0,
                &quot;last_modifier&quot;: &quot;author1&quot;,
                &quot;author&quot;: null,
                &quot;related_modifiers&quot;: &quot;author1;author2&quot;,
                &quot;file_owners&quot;: null,
                &quot;language&quot;: &quot;python&quot;,
                &quot;tapd_ws_id&quot;: null,
                &quot;tapd_bug_id&quot;: null,
                &quot;revision&quot;: null,
                &quot;ci_time&quot;: null,
                &quot;project&quot;: 1,
                &quot;scan_open&quot;: 1,
                &quot;scan_close&quot;: 2
            }
        ]
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="查看指定项目指定扫描的圈复杂度文件问题列表" tabindex="-1"><a class="header-anchor" href="#查看指定项目指定扫描的圈复杂度文件问题列表" aria-hidden="true">#</a> 查看指定项目指定扫描的圈复杂度文件问题列表</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/analysis/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/projects/&lt;project_id&gt;/codemetric/scans/&lt;scan_id&gt;/ccfiles/&lt;file_id&gt;/ccissues/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="参数列表-4" tabindex="-1"><a class="header-anchor" href="#参数列表-4" aria-hidden="true">#</a> 参数列表</h4><table><thead><tr><th>参数</th><th>类型</th><th>描述</th></tr></thead><tbody><tr><td>status</td><td>str</td><td>选填，问题状态，1为需要关注，2为无需关注，可多选，格式为1,2,3</td></tr><tr><td>change_type</td><td>str</td><td>选填，圈复杂度变化情况，0为无，1为新增，2为删除，3为无变化，可多选，格式为1,2,3</td></tr><tr><td>author</td><td>str</td><td>选填，问题责任人</td></tr><tr><td>last_modifier</td><td>str</td><td>选填，最近修改人</td></tr><tr><td>file_path</td><td>str</td><td>选填，文件路径</td></tr><tr><td>ccn_gte</td><td>str</td><td>选填，圈复杂度最小值</td></tr><tr><td>ccn_lte</td><td>str</td><td>选填，圈复杂度最大值</td></tr></tbody></table><h4 id="返回结果-3" tabindex="-1"><a class="header-anchor" href="#返回结果-3" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;count&quot;: 1,
        &quot;next&quot;: null,
        &quot;previous&quot;: null,
        &quot;results&quot;: [
            {
                &quot;id&quot;: 1,
                &quot;repo&quot;: 1,
                &quot;created_time&quot;: &quot;2021-02-19T15:30:20.968525+08:00&quot;,
                &quot;creator&quot;: null,
                &quot;modified_time&quot;: &quot;2021-02-19T15:30:20.968532+08:00&quot;,
                &quot;modifier&quot;: null,
                &quot;deleted_time&quot;: null,
                &quot;deleter&quot;: null,
                &quot;ccn&quot;: 22,
                &quot;g_cc_hash&quot;: null,
                &quot;cc_hash&quot;: null,
                &quot;file_path&quot;: &quot;test/demo.py&quot;,
                &quot;func_name&quot;: &quot;test_func&quot;,
                &quot;func_param_num&quot;: 4,
                &quot;long_name&quot;: &quot;test_func( project , result_data , scan , task_params )&quot;,
                &quot;change_type&quot;: 0,
                &quot;status&quot;: 1,
                &quot;last_modifier&quot;: &quot;author&quot;,
                &quot;author&quot;: null,
                &quot;related_modifiers&quot;: &quot;author,author2&quot;,
                &quot;is_tapdbug&quot;: false,
                &quot;ignore_time&quot;: null,
                &quot;is_latest&quot;: true,
                &quot;language&quot;: &quot;python&quot;,
                &quot;revision&quot;: &quot;revision&quot;,
                &quot;ci_time&quot;: &quot;2020-03-18T19:46:48+08:00&quot;,
                &quot;diff_ccn&quot;: null,
                &quot;project&quot;: 1,
                &quot;scan_open&quot;: 1,
                &quot;scan_close&quot;: null
            }
        ]
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="查看指定项目指定扫描的圈复杂度问题列表" tabindex="-1"><a class="header-anchor" href="#查看指定项目指定扫描的圈复杂度问题列表" aria-hidden="true">#</a> 查看指定项目指定扫描的圈复杂度问题列表</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/analysis/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/projects/&lt;project_id&gt;/codemetric/scans/&lt;scan_id&gt;/ccissues/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="参数列表-5" tabindex="-1"><a class="header-anchor" href="#参数列表-5" aria-hidden="true">#</a> 参数列表</h4><table><thead><tr><th>参数</th><th>类型</th><th>描述</th></tr></thead><tbody><tr><td>status</td><td>str</td><td>选填，问题状态，1为需要关注，2为无需关注，可多选，格式为1,2,3</td></tr><tr><td>change_type</td><td>str</td><td>选填，圈复杂度变化情况，0为无，1为新增，2为删除，3为无变化，可多选，格式为1,2,3</td></tr><tr><td>author</td><td>str</td><td>选填，问题责任人</td></tr><tr><td>last_modifier</td><td>str</td><td>选填，最近修改人</td></tr><tr><td>file_path</td><td>str</td><td>选填，文件路径</td></tr><tr><td>ccn_gte</td><td>str</td><td>选填，圈复杂度最小值</td></tr><tr><td>ccn_lte</td><td>str</td><td>选填，圈复杂度最大值</td></tr></tbody></table><h4 id="返回结果-4" tabindex="-1"><a class="header-anchor" href="#返回结果-4" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;count&quot;: 1,
        &quot;next&quot;: null,
        &quot;previous&quot;: null,
        &quot;results&quot;: [
            {
                &quot;id&quot;: 1,
                &quot;repo&quot;: 1,
                &quot;created_time&quot;: &quot;2021-02-19T15:30:20.968525+08:00&quot;,
                &quot;creator&quot;: null,
                &quot;modified_time&quot;: &quot;2021-02-19T15:30:20.968532+08:00&quot;,
                &quot;modifier&quot;: null,
                &quot;deleted_time&quot;: null,
                &quot;deleter&quot;: null,
                &quot;ccn&quot;: 22,
                &quot;g_cc_hash&quot;: null,
                &quot;cc_hash&quot;: null,
                &quot;file_path&quot;: &quot;test/demo.py&quot;,
                &quot;func_name&quot;: &quot;test_func&quot;,
                &quot;func_param_num&quot;: 4,
                &quot;long_name&quot;: &quot;test_func( project , result_data , scan , task_params )&quot;,
                &quot;change_type&quot;: 0,
                &quot;status&quot;: 1,
                &quot;last_modifier&quot;: &quot;author&quot;,
                &quot;author&quot;: null,
                &quot;related_modifiers&quot;: &quot;author,author2&quot;,
                &quot;is_tapdbug&quot;: false,
                &quot;ignore_time&quot;: null,
                &quot;is_latest&quot;: true,
                &quot;language&quot;: &quot;python&quot;,
                &quot;revision&quot;: &quot;revision&quot;,
                &quot;ci_time&quot;: &quot;2020-03-18T19:46:48+08:00&quot;,
                &quot;diff_ccn&quot;: null,
                &quot;project&quot;: 1,
                &quot;scan_open&quot;: 1,
                &quot;scan_close&quot;: null
            }
        ]
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="查看指定项目的重复文件列表" tabindex="-1"><a class="header-anchor" href="#查看指定项目的重复文件列表" aria-hidden="true">#</a> 查看指定项目的重复文件列表</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/analysis/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/projects/&lt;project_id&gt;/codemetric/dupfiles/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="参数列表-6" tabindex="-1"><a class="header-anchor" href="#参数列表-6" aria-hidden="true">#</a> 参数列表</h4><table><thead><tr><th>参数</th><th>类型</th><th>描述</th></tr></thead><tbody><tr><td>issue__state</td><td>str</td><td>选填，问题状态, 1为未处理，2为可忽略，3为关闭，可多选，格式为1,2,3</td></tr><tr><td>change_type</td><td>str</td><td>选填，重复文件更改类型，add为新增，del为删除，mod为删除，可多选，格式为add,del,mod</td></tr><tr><td>issue__owner</td><td>str</td><td>选填，问题责任人</td></tr><tr><td>last_modifier</td><td>str</td><td>选填，最近修改人</td></tr><tr><td>file_path</td><td>str</td><td>选填，文件路径</td></tr><tr><td>duplicate_rate_gte</td><td>int</td><td>选填，重复率最小值</td></tr><tr><td>duplicate_rate_lte</td><td>int</td><td>选填，重复率最大值</td></tr></tbody></table><h4 id="返回结果-5" tabindex="-1"><a class="header-anchor" href="#返回结果-5" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;count&quot;: 1,
        &quot;next&quot;: null,
        &quot;previous&quot;: null,
        &quot;results&quot;: [
            {
                &quot;id&quot;: 1,
                &quot;repo&quot;: 1,
                &quot;issue&quot;: {
                    &quot;id&quot;: 1,
                    &quot;state&quot;: 1,
                    &quot;owner&quot;: &quot;author&quot;
                },
                &quot;project_id&quot;: 1,
                &quot;scan_id&quot;: 1,
                &quot;issue_id&quot;: 1,
                &quot;issue_state&quot;: 1,
                &quot;issue_owner&quot;: &quot;author&quot;,
                &quot;dir_path&quot;: &quot;test&quot;,
                &quot;file_name&quot;: &quot;demo.py&quot;,
                &quot;file_path&quot;: &quot;test/demo.py&quot;,
                &quot;duplicate_rate&quot;: 4.63,
                &quot;total_line_count&quot;: 259,
                &quot;total_duplicate_line_count&quot;: 12,
                &quot;distinct_hash_num&quot;: 1,
                &quot;block_num&quot;: 1,
                &quot;last_modifier&quot;: &quot;author&quot;,
                &quot;change_type&quot;: null,
                &quot;scm_revision&quot;: &quot;12345678abc&quot;,
                &quot;is_latest&quot;: true
            }
        ]
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
} 
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="查看指定项目的指定重复文件" tabindex="-1"><a class="header-anchor" href="#查看指定项目的指定重复文件" aria-hidden="true">#</a> 查看指定项目的指定重复文件</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/analysis/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/projects/&lt;project_id&gt;/codemetric/dupfiles/&lt;file_id&gt;/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="返回结果-6" tabindex="-1"><a class="header-anchor" href="#返回结果-6" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;id&quot;: 1,
        &quot;repo&quot;: 1,
        &quot;issue&quot;: {
            &quot;id&quot;: 1,
            &quot;state&quot;: 1,
            &quot;owner&quot;: &quot;author&quot;
        },
        &quot;blocks&quot;: [
            {
                &quot;id&quot;: 1,
                &quot;duplicate_file&quot;: 1,
                &quot;project_id&quot;: 1,
                &quot;scan_id&quot;: 1,
                &quot;duplicate_file_id&quot;: 1,
                &quot;token_num&quot;: 120,
                &quot;duplicate_times&quot;: 2,
                &quot;duplicate_rate&quot;: 4.63,
                &quot;start_line_num&quot;: 216,
                &quot;end_line_num&quot;: 227,
                &quot;duplicate_line_count&quot;: 12,
                &quot;last_modifier&quot;: &quot;author&quot;,
                &quot;change_type&quot;: null,
                &quot;related_modifiers&quot;: &quot;author&quot;
            }
        ],
        &quot;duplicate_rate_trend&quot;: 0.0,
        &quot;project_id&quot;: 1815,
        &quot;scan_id&quot;: 488,
        &quot;issue_id&quot;: 3,
        &quot;issue_state&quot;: 1,
        &quot;issue_owner&quot;: &quot;author&quot;,
        &quot;dir_path&quot;: &quot;test&quot;,
        &quot;file_name&quot;: &quot;demo.py&quot;,
        &quot;file_path&quot;: &quot;test/demo.py&quot;,
        &quot;duplicate_rate&quot;: 4.63,
        &quot;total_line_count&quot;: 259,
        &quot;total_duplicate_line_count&quot;: 12,
        &quot;distinct_hash_num&quot;: 1,
        &quot;block_num&quot;: 1,
        &quot;last_modifier&quot;: &quot;author&quot;,
        &quot;change_type&quot;: null,
        &quot;scm_revision&quot;: &quot;xxx&quot;,
        &quot;is_latest&quot;: true
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="查看指定项目的指定文件的重复块列表" tabindex="-1"><a class="header-anchor" href="#查看指定项目的指定文件的重复块列表" aria-hidden="true">#</a> 查看指定项目的指定文件的重复块列表</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/analysis/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/projects/&lt;project_id&gt;/codemetric/dupfiles/&lt;file_id&gt;/blocks/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="返回结果-7" tabindex="-1"><a class="header-anchor" href="#返回结果-7" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;count&quot;: 1,
        &quot;next&quot;: null,
        &quot;previous&quot;: null,
        &quot;results&quot;: [
            {
                &quot;id&quot;: 1,
                &quot;duplicate_file&quot;: 1,
                &quot;project_id&quot;: 1,
                &quot;scan_id&quot;: 1,
                &quot;duplicate_file_id&quot;: 1,
                &quot;token_num&quot;: 120,
                &quot;duplicate_times&quot;: 2,
                &quot;duplicate_rate&quot;: 4.63,
                &quot;start_line_num&quot;: 216,
                &quot;end_line_num&quot;: 227,
                &quot;duplicate_line_count&quot;: 12,
                &quot;last_modifier&quot;: &quot;author&quot;,
                &quot;change_type&quot;: null,
                &quot;related_modifiers&quot;: &quot;author&quot;
            }
        ]
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="查看指定项目的文件行数列表" tabindex="-1"><a class="header-anchor" href="#查看指定项目的文件行数列表" aria-hidden="true">#</a> 查看指定项目的文件行数列表</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/analysis/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/projects/&lt;project_id&gt;/codemetric/clocfiles/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="参数列表-7" tabindex="-1"><a class="header-anchor" href="#参数列表-7" aria-hidden="true">#</a> 参数列表</h4><table><thead><tr><th>参数</th><th>类型</th><th>描述</th></tr></thead><tbody><tr><td>change_type</td><td>str</td><td>选填，改变类型（add、mod、del），支持多值，使用英文逗号&#39;,&#39;分隔</td></tr><tr><td>file_path</td><td>str</td><td>选填，文件路径</td></tr></tbody></table><h4 id="返回结果-8" tabindex="-1"><a class="header-anchor" href="#返回结果-8" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;count&quot;: 1,
        &quot;next&quot;: &quot;&quot;,
        &quot;previous&quot;: null,
        &quot;results&quot;: [
            {
                &quot;id&quot;: 1,
                &quot;code_line_num&quot;: 108587,
                &quot;comment_line_num&quot;: 0,
                &quot;blank_line_num&quot;: 0,
                &quot;total_line_num&quot;: 108587,
                &quot;add_code_line_num&quot;: 108587,
                &quot;add_comment_line_num&quot;: 0,
                &quot;add_blank_line_num&quot;: 0,
                &quot;add_total_line_num&quot;: 108587,
                &quot;mod_code_line_num&quot;: 0,
                &quot;mod_comment_line_num&quot;: 0,
                &quot;mod_blank_line_num&quot;: 0,
                &quot;mod_total_line_num&quot;: 0,
                &quot;del_code_line_num&quot;: 0,
                &quot;del_comment_line_num&quot;: 0,
                &quot;del_blank_line_num&quot;: 0,
                &quot;del_total_line_num&quot;: 0,
                &quot;project_id&quot;: 1,
                &quot;scan_id&quot;: 1,
                &quot;is_latest&quot;: true,
                &quot;dir_path&quot;: &quot;test&quot;,
                &quot;file_name&quot;: &quot;test.json&quot;,
                &quot;language&quot;: &quot;JSON&quot;,
                &quot;change_type&quot;: &quot;add&quot;
            }
        ]
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}    
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="查看指定项目的语言列表" tabindex="-1"><a class="header-anchor" href="#查看指定项目的语言列表" aria-hidden="true">#</a> 查看指定项目的语言列表</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET server/analysis/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/projects/&lt;project_id&gt;/codemetric/cloclangs/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="返回结果-9" tabindex="-1"><a class="header-anchor" href="#返回结果-9" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;count&quot;: 2,
        &quot;next&quot;: null,
        &quot;previous&quot;: null,
        &quot;results&quot;: [
            {
                &quot;id&quot;: 1,
                &quot;code_line_num&quot;: 9753,
                &quot;comment_line_num&quot;: 4220,
                &quot;blank_line_num&quot;: 2454,
                &quot;total_line_num&quot;: 16427,
                &quot;add_code_line_num&quot;: 9753,
                &quot;add_comment_line_num&quot;: 4220,
                &quot;add_blank_line_num&quot;: 2454,
                &quot;add_total_line_num&quot;: 16427,
                &quot;mod_code_line_num&quot;: 0,
                &quot;mod_comment_line_num&quot;: 0,
                &quot;mod_blank_line_num&quot;: 0,
                &quot;mod_total_line_num&quot;: 0,
                &quot;del_code_line_num&quot;: 0,
                &quot;del_comment_line_num&quot;: 0,
                &quot;del_blank_line_num&quot;: 0,
                &quot;del_total_line_num&quot;: 0,
                &quot;project_id&quot;: 1815,
                &quot;scan_id&quot;: 695,
                &quot;is_latest&quot;: true,
                &quot;name&quot;: &quot;Python&quot;,
                &quot;file_num&quot;: 165
            },
            {
                &quot;id&quot;: 2,
                &quot;code_line_num&quot;: 379,
                &quot;comment_line_num&quot;: 0,
                &quot;blank_line_num&quot;: 153,
                &quot;total_line_num&quot;: 532,
                &quot;add_code_line_num&quot;: 379,
                &quot;add_comment_line_num&quot;: 0,
                &quot;add_blank_line_num&quot;: 153,
                &quot;add_total_line_num&quot;: 532,
                &quot;mod_code_line_num&quot;: 0,
                &quot;mod_comment_line_num&quot;: 0,
                &quot;mod_blank_line_num&quot;: 0,
                &quot;mod_total_line_num&quot;: 0,
                &quot;del_code_line_num&quot;: 0,
                &quot;del_comment_line_num&quot;: 0,
                &quot;del_blank_line_num&quot;: 0,
                &quot;del_total_line_num&quot;: 0,
                &quot;project_id&quot;: 1815,
                &quot;scan_id&quot;: 695,
                &quot;is_latest&quot;: true,
                &quot;name&quot;: &quot;Markdown&quot;,
                &quot;file_num&quot;: 7
            }
        ]
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div>`,61),l=[u];function s(o,a){return e(),i("div",null,l)}const v=t(d,[["render",s],["__file","代码度量数据模块接口.html.vue"]]);export{v as default};
