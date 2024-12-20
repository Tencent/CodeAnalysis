import{_ as e,o as s,c as i,e as n}from"./app-697cd87e.js";const d={},l=n(`<h1 id="过滤配置" tabindex="-1"><a class="header-anchor" href="#过滤配置" aria-hidden="true">#</a> 过滤配置</h1><h2 id="路径过滤" tabindex="-1"><a class="header-anchor" href="#路径过滤" aria-hidden="true">#</a> 路径过滤</h2><p>用于设定代码分析的范围，设定后，已经开启的代码检查、代码度量各项功能都会在指定的代码范围内生效。</p><p>目前支持<strong>正则表达式</strong>和<strong>通配符</strong>两种类型：</p><ul><li><p><strong>正则表达式</strong></p><div class="language-txt line-numbers-mode" data-ext="txt"><pre class="language-txt"><code>请填写相对路径(基于代码库根目录)，要求匹配到文件
使用正则表达式格式，示例如下：
    代码根目录
    |-src
      |- test
          |- main_test.py
          |- input_test.py
      |- main.py
    |-test
      |- param_test.py
    匹配src/test目录：src/test/.*
    匹配根目录下的test目录：test/.*
    匹配所有_test.py后缀的文件：.*_test\\\\.py
修改后，下次分析生效，需要启动一次全量分析处理历史存量问题。
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><div class="language-txt line-numbers-mode" data-ext="txt"><pre class="language-txt"><code>Include 表示只分析，如只分析 src/ 目录：src/.*
Exclude 表示只屏蔽，如要屏蔽 src/lib/ 目录：src/lib/.*
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div></div></div></li><li><p><strong>通配符</strong></p><div class="language-txt line-numbers-mode" data-ext="txt"><pre class="language-txt"><code>请填写相对路径(基于代码库根目录)，要求匹配到文件
使用Unix通配符格式，示例如下
    代码根目录
    |-src
      |- test
          |- main_test.py
          |- input_test.py
      |- main.py
    |-test
      |- param_test.py
    匹配src/test目录：src/test/*
    匹配根目录下的test目录：test/*
    匹配所有_test.py后缀的文件：*_test.py
修改后，下次分析生效，需要启动一次全量分析处理历史存量问题。
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><div class="language-txt line-numbers-mode" data-ext="txt"><pre class="language-txt"><code>Include 表示只分析，如只分析 src/ 目录：src/*
Exclude 表示只屏蔽，如要屏蔽 src/lib/ 目录：src/lib/*
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div></div></div></li></ul><p>如果几个分析方案希望共享相同的路径过滤方案，可以通过导入导出路径配置的方式进行处理。</p><div class="custom-container tip"><p class="custom-container-title">TIP</p><p>配置更改后，下次启动分析生效</p></div><h2 id="问题过滤" tabindex="-1"><a class="header-anchor" href="#问题过滤" aria-hidden="true">#</a> 问题过滤</h2><ul><li><p><strong>全局 Issue 忽略状态同步</strong></p><p>仅对代码检查生效。开启后，在 Issue 页面进行全局忽略操作时，其他利用该方案分析的分析项目在发现相同 Issue 时，会同步忽略该 Issue。否则不受全局 Issue 忽略状态同步影响。</p></li></ul>`,9),t=[l];function a(r,c){return s(),i("div",null,t)}const u=e(d,[["render",a],["__file","过滤配置.html.vue"]]);export{u as default};
