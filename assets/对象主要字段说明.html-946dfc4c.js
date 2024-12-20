import{_ as e,o as i,c as n,e as s}from"./app-697cd87e.js";const a={},d=s(`<h1 id="对象主要字段说明" tabindex="-1"><a class="header-anchor" href="#对象主要字段说明" aria-hidden="true">#</a> 对象主要字段说明</h1><p>注：以下字段用于参考，具体字段格式需要以具体接口返回为准</p><h2 id="团队-org" tabindex="-1"><a class="header-anchor" href="#团队-org" aria-hidden="true">#</a> 团队（org）：</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>org_sid: str，团队编号
name: str，团队名称
description: str，团队描述
certificated: boolean，团队认证标志位
created_time: datetime，团队创建时间
updated_time: datetime，团队更新时间
admins: list，管理员列表
project_count: int，分析任务数量
team_count: int，项目组数量
user_count: int，成员数量
owner: str，负责人名称
tel_number: str，负责人电话
address: str，办公地址
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="项目-team" tabindex="-1"><a class="header-anchor" href="#项目-team" aria-hidden="true">#</a> 项目（team）：</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>name: str，项目组名称
display_name: str，项目组展示名称
description: str，项目组描述信息
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="代码库-repository" tabindex="-1"><a class="header-anchor" href="#代码库-repository" aria-hidden="true">#</a> 代码库（repository）：</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>name: str，代码库名称
scm_url: str，代码库地址
scm_type: int，代码库类型
created_from: str，创建来源
state：str，代码库状态，1表示活跃，2表示失活，3表示暂停使用
labels：list，标签
project_team: 项目
organization: 团队
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="扫描方案-scanscheme" tabindex="-1"><a class="header-anchor" href="#扫描方案-scanscheme" aria-hidden="true">#</a> 扫描方案（scanscheme）：</h2><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>name: str，扫描方案名称
repo：关联的代码库
refer_scheme: 参照的扫描方案
description: str，描述
tag: 执行标签
languages: 包含语言
default_flag: boolean，默认方案标志
created_from: str，创建来源
ignore_merged_issue: boolean，过滤其他分支引入的问题，默认False，不过滤
ignore_branch_issue: str，过滤指定分支引入的问题
ignore_submodule_clone: boolean，不拉取子模块，默认False
ignore_submodule_issue: boolean，忽略子模块问题，默认False
issue_global_ignore: boolean，开启问题全局忽略，默认False
daily_save: boolean，日常扫描记录保存7天开关，默认False
lfs_flag: boolean，自动拉取lfs文件，默认True
status: int，扫描方案状态，1为活跃，2为废弃
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div>`,10),r=[d];function l(t,c){return i(),n("div",null,r)}const u=e(a,[["render",l],["__file","对象主要字段说明.html.vue"]]);export{u as default};
