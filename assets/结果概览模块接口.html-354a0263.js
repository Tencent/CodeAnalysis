import{_ as n,o as i,c as e,e as u}from"./app-697cd87e.js";const d={},l=u(`<h1 id="代码扫描管理" tabindex="-1"><a class="header-anchor" href="#代码扫描管理" aria-hidden="true">#</a> 代码扫描管理</h1><h2 id="查看项目扫描最新结果概览" tabindex="-1"><a class="header-anchor" href="#查看项目扫描最新结果概览" aria-hidden="true">#</a> 查看项目扫描最新结果概览</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/analysis/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/projects/&lt;project_id&gt;/overview/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="返回结果" tabindex="-1"><a class="header-anchor" href="#返回结果" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;lintscan&quot;: {
        &quot;issue_open_num&quot;: 74,
        &quot;issue_fix_num&quot;: 439,
        &quot;issue_detail_num&quot;: 310,
        &quot;scan&quot;: {
            &quot;id&quot;: 1,
            &quot;scan_time&quot;: &quot;2021-03-11T20:46:44.171607+08:00&quot;,
            &quot;execute_time&quot;: &quot;00:02:17.844712&quot;
        },
        &quot;current_scan&quot;: {
            &quot;active_category_detail&quot;: {
                &quot;convention&quot;: 70,
                &quot;other&quot;: 4
            },
            &quot;active_severity_detail&quot;: {
                &quot;error&quot;: 69,
                &quot;warning&quot;: 5
            },
            &quot;issue_open_num&quot;: 74,
            &quot;issue_fix_num&quot;: 439
        },
        &quot;total&quot;: {
            &quot;state_detail&quot;: {
                &quot;active&quot;: 197,
                &quot;resolved&quot;: 13,
                &quot;closed&quot;: 23297
            },
            &quot;category_detail&quot;: {
                &quot;convention&quot;: {
                    &quot;active&quot;: 184,
                    &quot;resolved&quot;: 13,
                    &quot;closed&quot;: 21143
                },
                &quot;other&quot;: {
                    &quot;active&quot;: 13,
                    &quot;closed&quot;: 154
                },
                &quot;correctness&quot;: {
                    &quot;closed&quot;: 1997
                },
                &quot;performance&quot;: {
                    &quot;closed&quot;: 3
                }
            },
            &quot;severity_detail&quot;: {
                &quot;error&quot;: {
                    &quot;active&quot;: 157,
                    &quot;resolved&quot;: 11,
                    &quot;closed&quot;: 20113
                },
                &quot;warning&quot;: {
                    &quot;active&quot;: 40,
                    &quot;resolved&quot;: 2,
                    &quot;closed&quot;: 2930
                },
                &quot;info&quot;: {
                    &quot;closed&quot;: 254
                }
            }
        },
        &quot;status&quot;: 0,
        &quot;text&quot;: &quot;成功&quot;,
        &quot;description&quot;: null,
        &quot;scan_summary&quot;: {
            &quot;convention&quot;: {
                &quot;error&quot;: {
                    &quot;rule_count&quot;: 7,
                    &quot;active&quot;: 65
                },
                &quot;warning&quot;: {
                    &quot;rule_count&quot;: 2,
                    &quot;active&quot;: 5
                }
            },
            &quot;other&quot;: {
                &quot;error&quot;: {
                    &quot;rule_count&quot;: 1,
                    &quot;active&quot;: 4
                }
            }
        },
        &quot;total_summary&quot;: {
            &quot;correctness&quot;: {
                &quot;error&quot;: {
                    &quot;rule_count&quot;: 16,
                    &quot;closed&quot;: 1315
                },
                &quot;warning&quot;: {
                    &quot;rule_count&quot;: 10,
                    &quot;closed&quot;: 629
                },
                &quot;info&quot;: {
                    &quot;rule_count&quot;: 1,
                    &quot;closed&quot;: 53
                }
            },
            &quot;performance&quot;: {
                &quot;warning&quot;: {
                    &quot;rule_count&quot;: 1,
                    &quot;closed&quot;: 3
                }
            },
            &quot;convention&quot;: {
                &quot;error&quot;: {
                    &quot;rule_count&quot;: 42,
                    &quot;active&quot;: 149,
                    &quot;resolved&quot;: 11,
                    &quot;closed&quot;: 18778
                },
                &quot;warning&quot;: {
                    &quot;rule_count&quot;: 17,
                    &quot;active&quot;: 35,
                    &quot;resolved&quot;: 2,
                    &quot;closed&quot;: 2298
                },
                &quot;info&quot;: {
                    &quot;rule_count&quot;: 1,
                    &quot;closed&quot;: 67
                }
            },
            &quot;other&quot;: {
                &quot;error&quot;: {
                    &quot;rule_count&quot;: 2,
                    &quot;active&quot;: 8,
                    &quot;closed&quot;: 20
                },
                &quot;warning&quot;: {
                    &quot;rule_count&quot;: 1,
                    &quot;active&quot;: 5
                },
                &quot;info&quot;: {
                    &quot;rule_count&quot;: 3,
                    &quot;closed&quot;: 134
                }
            }
        }
    },
    &quot;cyclomaticcomplexityscan&quot;: {
        &quot;id&quot;: 1,
        &quot;scan_revision&quot;: &quot;scan_revision&quot;,
        &quot;scan_time&quot;: &quot;2021-03-11T20:46:44.171607+08:00&quot;,
        &quot;default_summary&quot;: {
            &quot;min_ccn&quot;: 20,
            &quot;over_cc_func_count&quot;: 6,
            &quot;under_cc_func_count&quot;: 796,
            &quot;diff_over_cc_func_count&quot;: 0,
            &quot;over_cc_func_average&quot;: 22.333333333333332,
            &quot;cc_func_average&quot;: 2.5099750623441395,
            &quot;over_cc_sum&quot;: 14,
            &quot;cc_average_of_lines&quot;: 1.0422094841063054
        },
        &quot;custom_summary&quot;: null,
        &quot;created_time&quot;: &quot;2021-03-11T20:48:59.976947+08:00&quot;,
        &quot;creator&quot;: null,
        &quot;modified_time&quot;: &quot;2021-03-11T20:49:00.088841+08:00&quot;,
        &quot;modifier&quot;: null,
        &quot;deleted_time&quot;: null,
        &quot;deleter&quot;: null,
        &quot;last_revision&quot;: &quot;last_revision&quot;,
        &quot;diff_cc_num&quot;: 0,
        &quot;cc_open_num&quot;: 6,
        &quot;cc_average_of_lines&quot;: 1.0422094841063054,
        &quot;cc_fix_num&quot;: 0,
        &quot;worse_cc_file_num&quot;: 0,
        &quot;min_ccn&quot;: 20,
        &quot;code_line_num&quot;: 13433,
        &quot;scan&quot;: 1
    },
    &quot;duplicatescan&quot;: {
        &quot;id&quot;: 1,
        &quot;scan_revision&quot;: &quot;scan_revision&quot;,
        &quot;scan_time&quot;: &quot;2021-03-11T20:46:44.171607+08:00&quot;,
        &quot;default_summary&quot;: {
            &quot;exhi_risk&quot;: {
                &quot;range&quot;: [
                    0.2,
                    1
                ],
                &quot;file_count&quot;: 1,
                &quot;diff&quot;: {
                    &quot;diff_file_count&quot;: 0
                }
            },
            &quot;high_risk&quot;: {
                &quot;range&quot;: [
                    0.11,
                    0.2
                ],
                &quot;file_count&quot;: 3,
                &quot;diff&quot;: {
                    &quot;diff_file_count&quot;: 0
                }
            },
            &quot;midd_risk&quot;: {
                &quot;range&quot;: [
                    0.05,
                    0.11
                ],
                &quot;file_count&quot;: 2,
                &quot;diff&quot;: {
                    &quot;diff_file_count&quot;: 0
                }
            },
            &quot;low_risk&quot;: {
                &quot;range&quot;: [
                    0,
                    0.05
                ],
                &quot;file_count&quot;: 2,
                &quot;diff&quot;: {
                    &quot;diff_file_count&quot;: 0
                }
            }
        },
        &quot;custom_summary&quot;: null,
        &quot;last_revision&quot;: &quot;last_revision&quot;,
        &quot;duplicate_file_count&quot;: 8,
        &quot;duplicate_block_count&quot;: 55,
        &quot;duplicate_line_count&quot;: 1177,
        &quot;diff_duplicate_block_count&quot;: 0,
        &quot;diff_duplicate_line_count&quot;: 0,
        &quot;close_issue_count&quot;: 0,
        &quot;new_issue_count&quot;: 0,
        &quot;reopen_issue_count&quot;: 5,
        &quot;ignored_issue_count&quot;: 0,
        &quot;duplicate_rate&quot;: 4.98,
        &quot;unique_duplicate_line_count&quot;: 1083,
        &quot;total_duplicate_line_count&quot;: 1083,
        &quot;total_line_count&quot;: 21745,
        &quot;scan&quot;: 1
    },
    &quot;clocscan&quot;: {
        &quot;id&quot;: 1,
        &quot;scan_revision&quot;: &quot;scan_revision&quot;,
        &quot;scan_time&quot;: &quot;2021-03-11T20:46:44.171607+08:00&quot;,
        &quot;last_revision&quot;: &quot;last_revision&quot;,
        &quot;code_line_num&quot;: 140490,
        &quot;comment_line_num&quot;: 5410,
        &quot;blank_line_num&quot;: 3408,
        &quot;total_line_num&quot;: 149308,
        &quot;add_code_line_num&quot;: 6673,
        &quot;add_comment_line_num&quot;: 2309,
        &quot;add_blank_line_num&quot;: 1289,
        &quot;add_total_line_num&quot;: 10271,
        &quot;mod_code_line_num&quot;: 965,
        &quot;mod_comment_line_num&quot;: 297,
        &quot;mod_blank_line_num&quot;: 0,
        &quot;mod_total_line_num&quot;: 1262,
        &quot;del_code_line_num&quot;: 35844,
        &quot;del_comment_line_num&quot;: 2117,
        &quot;del_blank_line_num&quot;: 1794,
        &quot;del_total_line_num&quot;: 39755,
        &quot;scan&quot;: 1
    }
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="查看项目代码最新扫描结果概览" tabindex="-1"><a class="header-anchor" href="#查看项目代码最新扫描结果概览" aria-hidden="true">#</a> 查看项目代码最新扫描结果概览</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/analysis/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/projects/&lt;project_id&gt;/overview/latestscan/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="参数列表" tabindex="-1"><a class="header-anchor" href="#参数列表" aria-hidden="true">#</a> 参数列表</h4><table><thead><tr><th>参数</th><th>类型</th><th>描述</th></tr></thead><tbody><tr><td>scan_revision</td><td>str</td><td>指定查询的扫描版本号，如不指定则为当前项目最新的一次扫描</td></tr></tbody></table><h4 id="返回结果-1" tabindex="-1"><a class="header-anchor" href="#返回结果-1" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;id&quot;: 1,                            # 扫描编号
        &quot;repo_id&quot;: 1,                       # 代码库编号
        &quot;project_id&quot;: 1,                    # 项目编号
        &quot;job_gid&quot;: 1,                       # 关联任务编号
        &quot;scan_time&quot;: &quot;2021-03-11T20:46:44.171607+08:00&quot;,  # 扫描时间
        &quot;current_revision&quot;: &quot;current_revision&quot;,  # 扫描版本号
        &quot;result_code&quot;: 0,                   # 扫描任务结果码，0表示正常
        &quot;result_code_msg&quot;: &quot;成功&quot;,
        &quot;result_msg&quot;: null,
        &quot;lintscan&quot;: {                         # 代码扫描结果信息
            &quot;current_scan&quot;: {                 # 本次扫描信息
                &quot;active_severity_detail&quot;: {   # 不同严重级别的活跃问题数，包含 fatal（1-致命）, error（2-错误）, warning（3-警告）, info（4-提示）
                    &quot;error&quot;: 69,              
                    &quot;warning&quot;: 5              
                },
                &quot;issue_open_num&quot;: 10,         # 本次扫描新发现问题数
                &quot;issue_fix_num&quot;: 2            # 本次扫描关闭存量问题数
            },
            &quot;total&quot;: {                        # 当前项目整体信息
                &quot;state_detail&quot;: {             # 不同处理状态的问题数，包含 active（1-活跃）、resolved（2-已处理）、closed（3-已关闭）
                    &quot;active&quot;: 197,            
                    &quot;resolved&quot;: 13,
                    &quot;closed&quot;: 23297
                },
                &quot;severity_detail&quot;: {         # 不同严重级别下不同处理状态的问题量
                    &quot;error&quot;: {
                        &quot;active&quot;: 157,
                        &quot;resolved&quot;: 11,
                        &quot;closed&quot;: 20113
                    },
                    &quot;warning&quot;: {
                        &quot;active&quot;: 40,
                        &quot;resolved&quot;: 2,
                        &quot;closed&quot;: 2930
                    },
                    &quot;info&quot;: {
                        &quot;closed&quot;: 254
                    }
                }
            }
        },
        &quot;duplicatescan&quot;: {                    # 重复代码扫描结果信息
            &quot;id&quot;: 1,                          # 扫描任务编号
            &quot;scan_revision&quot;: &quot;scan_revision&quot;, # 扫描版本号
            &quot;scan_time&quot;: &quot;2021-03-11T20:46:44.171607+08:00&quot;,  # 扫描时间
            &quot;default_summary&quot;: {              # 默认概览
                &quot;exhi_risk&quot;: {                # 极高风险
                    &quot;range&quot;: [                # 重复率范围: 0.2-1
                        0.2,
                        1
                    ],
                    &quot;file_count&quot;: 1,          # 文件数量
                    &quot;diff&quot;: {                 # 增量数据
                        &quot;diff_file_count&quot;: 0  # 增量文件数量
                    }
                },
                &quot;high_risk&quot;: {                # 高风险
                    &quot;range&quot;: [                # 重复率范围：0.11-0.2
                        0.11,
                        0.2
                    ],
                    &quot;file_count&quot;: 3,
                    &quot;diff&quot;: {
                        &quot;diff_file_count&quot;: 0
                    }
                },
                &quot;midd_risk&quot;: {                # 中风险
                    &quot;range&quot;: [                # 重复率范围：0.05-0.11
                        0.05,
                        0.11
                    ],
                    &quot;file_count&quot;: 2,
                    &quot;diff&quot;: {
                        &quot;diff_file_count&quot;: 0
                    }
                },
                &quot;low_risk&quot;: {                 # 低风险
                    &quot;range&quot;: [                # 重复率范围：0-0.05
                        0,
                        0.05
                    ],
                    &quot;file_count&quot;: 2,
                    &quot;diff&quot;: {
                        &quot;diff_file_count&quot;: 0
                    }
                }
            },
            &quot;custom_summary&quot;: null,           # 自定义概览数据
            &quot;last_revision&quot;: &quot;2010ef28ff3a26424d4e8f32df022f90cd682eda&quot;,  # 上次扫描版本号
            &quot;duplicate_file_count&quot;: 8,        # 重复文件数量
            &quot;duplicate_block_count&quot;: 55,      # 重复代码块数量
            &quot;duplicate_line_count&quot;: 1177,     # 重复代码行数
            &quot;diff_duplicate_block_count&quot;: 0,  # 增量重复代码块数量
            &quot;diff_duplicate_line_count&quot;: 0,   # 增量重复代码行数
            &quot;close_issue_count&quot;: 0,           # 关闭问题数
            &quot;new_issue_count&quot;: 0,             # 新增问题数
            &quot;reopen_issue_count&quot;: 5,          # 重新打开问题数
            &quot;ignored_issue_count&quot;: 0,         # 忽略问题数
            &quot;duplicate_rate&quot;: 4.98,           # 重复率
            &quot;unique_duplicate_line_count&quot;: 1083,  # 去重后的重复代码行数
            &quot;total_duplicate_line_count&quot;: 1083,   # 项目总的去重后的重复代码行数
            &quot;total_line_count&quot;: 21745,            # 项目总行书
            &quot;scan&quot;: 1                         # 关联扫描任务编号
        },
        &quot;cyclomaticcomplexityscan&quot;: {         # 圈复杂度扫描数据
            &quot;id&quot;: 1,                          # 圈复杂度扫描编号
            &quot;scan_revision&quot;: &quot;scan_revision&quot;, # 扫描版本号
            &quot;scan_time&quot;: &quot;2021-03-11T20:46:44.171607+08:00&quot;,
            &quot;default_summary&quot;: {                      # 默认概览数据
                &quot;min_ccn&quot;: 20,                        # 最小圈复杂度阈值
                &quot;over_cc_func_count&quot;: 6,              # 超标函数数量
                &quot;under_cc_func_count&quot;: 796,           # 未超标函数数量
                &quot;diff_over_cc_func_count&quot;: 0,         # 增量超标函数数据
                &quot;over_cc_func_average&quot;: 22.333333333333332,  # 平均超标圈复杂度
                &quot;cc_func_average&quot;: 2.5099750623441395,  # 平均圈复杂度
                &quot;over_cc_sum&quot;: 14,                      # 文件超标方法圈复杂度超过阈值的差值之和
                &quot;cc_average_of_lines&quot;: 1.0422094841063054 # 千行代码平均圈复杂度
            },
            &quot;custom_summary&quot;: null,                     # 自定义概览数据
            &quot;created_time&quot;: &quot;2021-03-11T20:48:59.976947+08:00&quot;,
            &quot;creator&quot;: null,
            &quot;modified_time&quot;: &quot;2021-03-11T20:49:00.088841+08:00&quot;,
            &quot;modifier&quot;: null,
            &quot;deleted_time&quot;: null,
            &quot;deleter&quot;: null,
            &quot;last_revision&quot;: &quot;last_revision&quot;,           # 上一次扫描版本号
            &quot;diff_cc_num&quot;: 0,                           # 增量超标函数数量
            &quot;cc_open_num&quot;: 6,                           # 超标函数量
            &quot;cc_average_of_lines&quot;: 1.0422094841063054,  # 千行代码平均圈复杂度
            &quot;cc_fix_num&quot;: 0,                            # 修复数量
            &quot;worse_cc_file_num&quot;: 0,                     # 圈复杂度恶化的文件数据
            &quot;min_ccn&quot;: 20,                              # 最小圈复杂度阈值
            &quot;code_line_num&quot;: 13433,                     # 代码行数
            &quot;scan&quot;: 1
        },
        &quot;clocscan&quot;: {
            &quot;id&quot;: 1,
            &quot;scan_revision&quot;: &quot;scan_revision&quot;,           # 扫描版本号
            &quot;scan_time&quot;: &quot;2021-03-11T20:46:44.171607+08:00&quot;,  # 扫描时间
            &quot;last_revision&quot;: &quot;last_revision&quot;,           # 上一次扫描版本号
            &quot;code_line_num&quot;: 140490,                    # 代码行数
            &quot;comment_line_num&quot;: 5410,                   # 注释行数
            &quot;blank_line_num&quot;: 3408,                     # 空白行数
            &quot;total_line_num&quot;: 149308,                   # 总行数
            &quot;add_code_line_num&quot;: 6673,                  # 增加的代码行数
            &quot;add_comment_line_num&quot;: 2309,               # 增加的注释行数
            &quot;add_blank_line_num&quot;: 1289,                 # 增加的空白行数
            &quot;add_total_line_num&quot;: 10271,                # 增加的总行数
            &quot;mod_code_line_num&quot;: 965,                   # 修改的代码行数
            &quot;mod_comment_line_num&quot;: 297,                # 修改的注释行数
            &quot;mod_blank_line_num&quot;: 0,                    # 修改的空白行数
            &quot;mod_total_line_num&quot;: 1262,                 # 修改的总行数
            &quot;del_code_line_num&quot;: 35844,                 # 删除的代码行数
            &quot;del_comment_line_num&quot;: 2117,               # 删除的注释行数
            &quot;del_blank_line_num&quot;: 1794,                 # 删除的空白行数
            &quot;del_total_line_num&quot;: 39755,                # 删除的总行数
            &quot;scan&quot;: 1
        }
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="查看项目代码扫描结果概览" tabindex="-1"><a class="header-anchor" href="#查看项目代码扫描结果概览" aria-hidden="true">#</a> 查看项目代码扫描结果概览</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/analysis/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/projects/&lt;project_id&gt;/overview/lintscans/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="参数列表-1" tabindex="-1"><a class="header-anchor" href="#参数列表-1" aria-hidden="true">#</a> 参数列表</h4><table><thead><tr><th>参数</th><th>类型</th><th>描述</th></tr></thead><tbody><tr><td>scan_time_before</td><td>str</td><td>扫描任务起始时间，格式: 2021-01-01 00:00:00</td></tr><tr><td>scan_time_after</td><td>str</td><td>扫描任务结束时间</td></tr></tbody></table><h4 id="返回结果-2" tabindex="-1"><a class="header-anchor" href="#返回结果-2" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;count&quot;: 1,
        &quot;next&quot;: null,
        &quot;previous&quot;: null,
        &quot;results&quot;: [
            {
                &quot;issue_open_num&quot;: 10,             # 本次扫描新发现问题数
                &quot;issue_fix_num&quot;: 2,               # 本次扫描关闭存量问题数
                &quot;issue_detail_num&quot;: 310,          # 本次扫描上报原始问题数（问题展示会进行聚合）
                &quot;scan&quot;: {                         # 扫描信息
                    &quot;id&quot;: 1,                      # 扫描任务编号
                    &quot;scan_time&quot;: &quot;2021-03-11T20:46:44.171607+08:00&quot;,  # 扫描开始时间
                    &quot;execute_time&quot;: &quot;00:02:17.844712&quot;                 # 扫描执行耗时
                },
                &quot;current_scan&quot;: {                 # 本次扫描信息
                    &quot;active_category_detail&quot;: {   # 活跃问题分类，包含 CORRECTNESS（1-功能）、SECURITY（2-安全）、PERFORMANCE（3-性能）、USABILITY（4-可用性）、ACCESSIBILITY（5-无障碍化）、I18N（6-国际化）、CONVENTION（7-代码风格）、OTHER（8-其他）
                        &quot;convention&quot;: 70,         # 代码风格类型问题
                        &quot;other&quot;: 4                # 其他类型问题
                    },
                    &quot;active_severity_detail&quot;: {   # 不同严重级别的活跃问题数，包含 fatal（1-致命）, error（2-错误）, warning（3-警告）, info（4-提示）
                        &quot;error&quot;: 69,              
                        &quot;warning&quot;: 5              
                    },
                    &quot;issue_open_num&quot;: 10,         # 本次扫描新发现问题数
                    &quot;issue_fix_num&quot;: 2            # 本次扫描关闭存量问题数
                },
                &quot;total&quot;: {                        # 当前项目整体信息
                    &quot;state_detail&quot;: {             # 不同处理状态的问题数，包含 active（1-活跃）、resolved（2-已处理）、closed（3-已关闭）
                        &quot;active&quot;: 197,            
                        &quot;resolved&quot;: 13,
                        &quot;closed&quot;: 23297
                    },
                    &quot;category_detail&quot;: {          # 不同分类下不同处理状态的问题量
                        &quot;convention&quot;: {           
                            &quot;active&quot;: 184,
                            &quot;resolved&quot;: 13,
                            &quot;closed&quot;: 21143
                        },
                        &quot;other&quot;: {                
                            &quot;active&quot;: 13,
                            &quot;closed&quot;: 154
                        },
                        &quot;correctness&quot;: {
                            &quot;closed&quot;: 1997
                        },
                        &quot;performance&quot;: {
                            &quot;closed&quot;: 3
                        }
                    },
                    &quot;severity_detail&quot;: {         # 不同严重级别下不同处理状态的问题量
                        &quot;error&quot;: {
                            &quot;active&quot;: 157,
                            &quot;resolved&quot;: 11,
                            &quot;closed&quot;: 20113
                        },
                        &quot;warning&quot;: {
                            &quot;active&quot;: 40,
                            &quot;resolved&quot;: 2,
                            &quot;closed&quot;: 2930
                        },
                        &quot;info&quot;: {
                            &quot;closed&quot;: 254
                        }
                    }
                },
                &quot;status&quot;: 0,                     # 扫描状态，0表示成功
                &quot;text&quot;: &quot;成功&quot;,
                &quot;description&quot;: null,
                &quot;scan_summary&quot;: {                # 扫描概览
                    &quot;convention&quot;: {              
                        &quot;error&quot;: {               
                            &quot;rule_count&quot;: 7,     # 规则数
                            &quot;active&quot;: 65         # 活跃问题数
                        },
                        &quot;warning&quot;: {
                            &quot;rule_count&quot;: 2,
                            &quot;active&quot;: 5
                        }
                    },
                    &quot;other&quot;: {
                        &quot;error&quot;: {
                            &quot;rule_count&quot;: 1,
                            &quot;active&quot;: 4
                        }
                    }
                },
                &quot;total_summary&quot;: {
                    &quot;correctness&quot;: {
                        &quot;error&quot;: {
                            &quot;rule_count&quot;: 16,
                            &quot;closed&quot;: 1315
                        },
                        &quot;warning&quot;: {
                            &quot;rule_count&quot;: 10,
                            &quot;closed&quot;: 629
                        },
                        &quot;info&quot;: {
                            &quot;rule_count&quot;: 1,
                            &quot;closed&quot;: 53
                        }
                    },
                    &quot;performance&quot;: {
                        &quot;warning&quot;: {
                            &quot;rule_count&quot;: 1,
                            &quot;closed&quot;: 3
                        }
                    },
                    &quot;convention&quot;: {
                        &quot;error&quot;: {
                            &quot;rule_count&quot;: 42,
                            &quot;active&quot;: 149,
                            &quot;resolved&quot;: 11,
                            &quot;closed&quot;: 18778
                        },
                        &quot;warning&quot;: {
                            &quot;rule_count&quot;: 17,
                            &quot;active&quot;: 35,
                            &quot;resolved&quot;: 2,
                            &quot;closed&quot;: 2298
                        },
                        &quot;info&quot;: {
                            &quot;rule_count&quot;: 1,
                            &quot;closed&quot;: 67
                        }
                    },
                    &quot;other&quot;: {
                        &quot;error&quot;: {
                            &quot;rule_count&quot;: 2,
                            &quot;active&quot;: 8,
                            &quot;closed&quot;: 20
                        },
                        &quot;warning&quot;: {
                            &quot;rule_count&quot;: 1,
                            &quot;active&quot;: 5
                        },
                        &quot;info&quot;: {
                            &quot;rule_count&quot;: 3,
                            &quot;closed&quot;: 134
                        }
                    }
                }
            }
        ]
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="查看项目代码度量圈复杂度结果概览" tabindex="-1"><a class="header-anchor" href="#查看项目代码度量圈复杂度结果概览" aria-hidden="true">#</a> 查看项目代码度量圈复杂度结果概览</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/analysis/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/projects/&lt;project_id&gt;/overview/cycscans/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="参数列表-2" tabindex="-1"><a class="header-anchor" href="#参数列表-2" aria-hidden="true">#</a> 参数列表</h4><table><thead><tr><th>参数</th><th>类型</th><th>描述</th></tr></thead><tbody><tr><td>scan_time_before</td><td>str</td><td>扫描任务起始时间，格式: 2021-01-01 00:00:00</td></tr><tr><td>scan_time_after</td><td>str</td><td>扫描任务结束时间</td></tr></tbody></table><h4 id="返回结果-3" tabindex="-1"><a class="header-anchor" href="#返回结果-3" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;count&quot;: 1,
        &quot;next&quot;: null,
        &quot;previous&quot;: null,
        &quot;results&quot;: [
            {
                &quot;id&quot;: 1,
                &quot;scan_revision&quot;: &quot;scan_revision&quot;,
                &quot;scan_time&quot;: &quot;2021-03-11T20:46:44.171607+08:00&quot;,
                &quot;default_summary&quot;: {
                    &quot;min_ccn&quot;: 20,
                    &quot;over_cc_func_count&quot;: 6,
                    &quot;under_cc_func_count&quot;: 796,
                    &quot;diff_over_cc_func_count&quot;: 0,
                    &quot;over_cc_func_average&quot;: 22.333333333333332,
                    &quot;cc_func_average&quot;: 2.5099750623441395,
                    &quot;over_cc_sum&quot;: 14,
                    &quot;cc_average_of_lines&quot;: 1.0422094841063054
                },
                &quot;custom_summary&quot;: null,
                &quot;created_time&quot;: &quot;2021-03-11T20:48:59.976947+08:00&quot;,
                &quot;creator&quot;: null,
                &quot;modified_time&quot;: &quot;2021-03-11T20:49:00.088841+08:00&quot;,
                &quot;modifier&quot;: null,
                &quot;deleted_time&quot;: null,
                &quot;deleter&quot;: null,
                &quot;last_revision&quot;: &quot;last_revision&quot;,
                &quot;diff_cc_num&quot;: 0,
                &quot;cc_open_num&quot;: 6,
                &quot;cc_average_of_lines&quot;: 1.0422094841063054,
                &quot;cc_fix_num&quot;: 0,
                &quot;worse_cc_file_num&quot;: 0,
                &quot;min_ccn&quot;: 20,
                &quot;code_line_num&quot;: 13433,
                &quot;scan&quot;: 1
            }
        ]
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="查看项目代码度量重复代码结果概览" tabindex="-1"><a class="header-anchor" href="#查看项目代码度量重复代码结果概览" aria-hidden="true">#</a> 查看项目代码度量重复代码结果概览</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/analysis/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/projects/&lt;project_id&gt;/overview/dupscans/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="参数列表-3" tabindex="-1"><a class="header-anchor" href="#参数列表-3" aria-hidden="true">#</a> 参数列表</h4><table><thead><tr><th>参数</th><th>类型</th><th>描述</th></tr></thead><tbody><tr><td>scan_time_before</td><td>str</td><td>扫描任务起始时间，格式: 2021-01-01 00:00:00</td></tr><tr><td>scan_time_after</td><td>str</td><td>扫描任务结束时间</td></tr></tbody></table><h4 id="返回结果-4" tabindex="-1"><a class="header-anchor" href="#返回结果-4" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;count&quot;: 1,
        &quot;next&quot;: null,
        &quot;previous&quot;: null,
        &quot;results&quot;: [
            {
                &quot;id&quot;: 1,
                &quot;scan_revision&quot;: &quot;scan_revision&quot;,
                &quot;scan_time&quot;: &quot;2021-03-11T20:46:44.171607+08:00&quot;,
                &quot;default_summary&quot;: {
                    &quot;exhi_risk&quot;: {
                        &quot;range&quot;: [
                            0.2,
                            1
                        ],
                        &quot;file_count&quot;: 1,
                        &quot;diff&quot;: {
                            &quot;diff_file_count&quot;: 0
                        }
                    },
                    &quot;high_risk&quot;: {
                        &quot;range&quot;: [
                            0.11,
                            0.2
                        ],
                        &quot;file_count&quot;: 3,
                        &quot;diff&quot;: {
                            &quot;diff_file_count&quot;: 0
                        }
                    },
                    &quot;midd_risk&quot;: {
                        &quot;range&quot;: [
                            0.05,
                            0.11
                        ],
                        &quot;file_count&quot;: 2,
                        &quot;diff&quot;: {
                            &quot;diff_file_count&quot;: 0
                        }
                    },
                    &quot;low_risk&quot;: {
                        &quot;range&quot;: [
                            0,
                            0.05
                        ],
                        &quot;file_count&quot;: 2,
                        &quot;diff&quot;: {
                            &quot;diff_file_count&quot;: 0
                        }
                    }
                },
                &quot;custom_summary&quot;: null,
                &quot;last_revision&quot;: &quot;last_revision&quot;,
                &quot;duplicate_file_count&quot;: 8,
                &quot;duplicate_block_count&quot;: 55,
                &quot;duplicate_line_count&quot;: 1177,
                &quot;diff_duplicate_block_count&quot;: 0,
                &quot;diff_duplicate_line_count&quot;: 0,
                &quot;close_issue_count&quot;: 0,
                &quot;new_issue_count&quot;: 0,
                &quot;reopen_issue_count&quot;: 5,
                &quot;ignored_issue_count&quot;: 0,
                &quot;duplicate_rate&quot;: 4.98,
                &quot;unique_duplicate_line_count&quot;: 1083,
                &quot;total_duplicate_line_count&quot;: 1083,
                &quot;total_line_count&quot;: 21745,
                &quot;scan&quot;: 1
            }
        ]
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="查看项目代码度量代码统计结果概览" tabindex="-1"><a class="header-anchor" href="#查看项目代码度量代码统计结果概览" aria-hidden="true">#</a> 查看项目代码度量代码统计结果概览</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>GET /server/analysis/api/orgs/&lt;org_sid&gt;/teams/&lt;team_name&gt;/repos/&lt;repo_id&gt;/projects/&lt;project_id&gt;/overview/clocscans/
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div></div></div><h4 id="参数列表-4" tabindex="-1"><a class="header-anchor" href="#参数列表-4" aria-hidden="true">#</a> 参数列表</h4><table><thead><tr><th>参数</th><th>类型</th><th>描述</th></tr></thead><tbody><tr><td>scan_time_before</td><td>str</td><td>扫描任务起始时间，格式: 2021-01-01 00:00:00</td></tr><tr><td>scan_time_after</td><td>str</td><td>扫描任务结束时间</td></tr></tbody></table><h4 id="返回结果-5" tabindex="-1"><a class="header-anchor" href="#返回结果-5" aria-hidden="true">#</a> 返回结果</h4><div class="language-JSON line-numbers-mode" data-ext="JSON"><pre class="language-JSON"><code>{
    &quot;data&quot;: {
        &quot;count&quot;: 1,
        &quot;next&quot;: null,
        &quot;previous&quot;: null,
        &quot;results&quot;: [
            {
                &quot;id&quot;: 1,
                &quot;scan_revision&quot;: &quot;scan_revision&quot;,
                &quot;scan_time&quot;: &quot;2021-03-11T20:46:44.171607+08:00&quot;,
                &quot;last_revision&quot;: &quot;last_revision&quot;,
                &quot;code_line_num&quot;: 140490,
                &quot;comment_line_num&quot;: 5410,
                &quot;blank_line_num&quot;: 3408,
                &quot;total_line_num&quot;: 149308,
                &quot;add_code_line_num&quot;: 6673,
                &quot;add_comment_line_num&quot;: 2309,
                &quot;add_blank_line_num&quot;: 1289,
                &quot;add_total_line_num&quot;: 10271,
                &quot;mod_code_line_num&quot;: 965,
                &quot;mod_comment_line_num&quot;: 297,
                &quot;mod_blank_line_num&quot;: 0,
                &quot;mod_total_line_num&quot;: 1262,
                &quot;del_code_line_num&quot;: 35844,
                &quot;del_comment_line_num&quot;: 2117,
                &quot;del_blank_line_num&quot;: 1794,
                &quot;del_total_line_num&quot;: 39755,
                &quot;scan&quot;: 1
            }
        ]
    },
    &quot;code&quot;: 0,
    &quot;msg&quot;: &quot;请求成功&quot;,
    &quot;status_code&quot;: 200
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div>`,35),s=[l];function t(o,v){return i(),e("div",null,s)}const c=n(d,[["render",t],["__file","结果概览模块接口.html.vue"]]);export{c as default};
