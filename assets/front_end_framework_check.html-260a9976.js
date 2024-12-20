import{_ as e,o as a,c as i,e as n}from"./app-697cd87e.js";const d={},r=n(`<h1 id="前端框架检查规则包" tabindex="-1"><a class="header-anchor" href="#前端框架检查规则包" aria-hidden="true">#</a> 前端框架检查规则包</h1><h2 id="背景" tabindex="-1"><a class="header-anchor" href="#背景" aria-hidden="true">#</a> 背景</h2><p>前端项目在长期发展过程中，由于框架开源许可证变更、框架性能外观等不适用等因素，需要对前端框架进行平滑切换，而这就需要腾讯云代码分析 TCA 的介入，方便对企业内所有前端项目进行批量分析统计，方便管理。</p><h2 id="需求" tabindex="-1"><a class="header-anchor" href="#需求" aria-hidden="true">#</a> 需求</h2><ul><li>检查代码仓库中使用到指定前端框架的代码位置。</li></ul><h3 id="示例" tabindex="-1"><a class="header-anchor" href="#示例" aria-hidden="true">#</a> 示例</h3><div class="language-json line-numbers-mode" data-ext="json"><pre class="language-json"><code>{
  &quot;name&quot;: &quot;framework&quot;,
  &quot;version&quot;: &quot;1.0.0&quot;,
  &quot;dependencies&quot;: {
    &quot;react&quot;: &quot;^17.0.2&quot;, // 触发规则
    &quot;react-dom&quot;: &quot;^17.0.2&quot;, // 触发规则
    &quot;react-hotkeys-hook&quot;: &quot;^3.4.3&quot;, // 触发规则
    &quot;react-redux&quot;: &quot;^7.2.5&quot;, // 触发规则
    &quot;single-spa&quot;: &quot;^5.9.3&quot;,
    &quot;universal-cookie&quot;: &quot;^4.0.4&quot;
  },
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="快速体验" tabindex="-1"><a class="header-anchor" href="#快速体验" aria-hidden="true">#</a> 快速体验</h2><p>TCA 现已支持前端框架检查规则包，可以在 TCA 分析方案中搜索勾选以下规则包，快速体验。</p><h3 id="启用规则包" tabindex="-1"><a class="header-anchor" href="#启用规则包" aria-hidden="true">#</a> 启用规则包</h3><p>分析方案 -&gt; 代码检查 -&gt; 前端框架检查规则包 -&gt; 启用/查看规则</p><h3 id="支持框架" tabindex="-1"><a class="header-anchor" href="#支持框架" aria-hidden="true">#</a> 支持框架</h3><ul><li>TDesign</li><li>AntD</li><li>React</li><li>Vue</li></ul><h3 id="更多" tabindex="-1"><a class="header-anchor" href="#更多" aria-hidden="true">#</a> 更多</h3><p>更多框架支持，欢迎提 issue 进行咨询扩展。</p>`,15),t=[r];function o(s,u){return a(),i("div",null,t)}const c=e(d,[["render",o],["__file","front_end_framework_check.html.vue"]]);export{c as default};
