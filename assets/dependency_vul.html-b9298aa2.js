import{_ as e,o as n,c as i,e as t}from"./app-697cd87e.js";const l={},a=t(`<h1 id="依赖漏洞扫描规则包" tabindex="-1"><a class="header-anchor" href="#依赖漏洞扫描规则包" aria-hidden="true">#</a> 依赖漏洞扫描规则包</h1><h2 id="概述" tabindex="-1"><a class="header-anchor" href="#概述" aria-hidden="true">#</a> 概述</h2><p>该规则包可分析项目依赖组件，以及依赖组件中是否存在漏洞等问题。辅助开发者准确分析到依赖组件的安全性，选用安全可靠的依赖组件。</p><p>规则包中将漏洞规则分为“低危漏洞”、“中危漏洞”、“高危漏洞”三个等级，扫描出有漏洞的组件，TCA会提供问题组件名称和版本、漏洞情况介绍，以及可用的修复版本（如获取到）。</p><p>已支持语言：C/C++、C#、Go、Java、JavaScript、PHP、Python、Ruby、Scala、TypeScript等。</p><h2 id="示例" tabindex="-1"><a class="header-anchor" href="#示例" aria-hidden="true">#</a> 示例</h2><div class="language-xml line-numbers-mode" data-ext="xml"><pre class="language-xml"><code>&lt;?xml version=&quot;1.0&quot; encoding=&quot;UTF-8&quot;?&gt;
&lt;project xmlns=&quot;http://maven.apache.org/POM/4.0.0&quot; xmlns:xsi=&quot;http://www.w3.org/2001/XMLSchema-instance&quot;
         xsi:schemaLocation=&quot;http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd&quot;&gt;

    &lt;parent&gt;
        &lt;groupId&gt;org.javaweb.vuln&lt;/groupId&gt;
        &lt;artifactId&gt;javaweb-vuln&lt;/artifactId&gt;
        &lt;version&gt;3.0.3&lt;/version&gt;
    &lt;/parent&gt;

    &lt;dependencies&gt;

        &lt;dependency&gt;
            &lt;groupId&gt;org.apache.struts&lt;/groupId&gt;
            &lt;artifactId&gt;struts2-core&lt;/artifactId&gt;
            &lt;!-- 触发规则  --&gt;
            &lt;version&gt;2.1.8&lt;/version&gt;
            &lt;exclusions&gt;
                &lt;exclusion&gt;
                    &lt;groupId&gt;org.freemarker&lt;/groupId&gt;
                    &lt;artifactId&gt;freemarker&lt;/artifactId&gt;
                &lt;/exclusion&gt;

                &lt;exclusion&gt;
                    &lt;groupId&gt;org.springframework&lt;/groupId&gt;
                    &lt;artifactId&gt;spring-test&lt;/artifactId&gt;
                &lt;/exclusion&gt;

                &lt;exclusion&gt;
                    &lt;groupId&gt;commons-fileupload&lt;/groupId&gt;
                    &lt;artifactId&gt;commons-fileupload&lt;/artifactId&gt;
                &lt;/exclusion&gt;
            &lt;/exclusions&gt;
        &lt;/dependency&gt;

    &lt;/dependencies&gt;

&lt;/project&gt;
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="快速体验" tabindex="-1"><a class="header-anchor" href="#快速体验" aria-hidden="true">#</a> 快速体验</h2><p>TCA 现已支持依赖漏洞扫描规则包，可以在 TCA 分析方案中搜索勾选该规则包，快速体验。</p><h3 id="启用规则包" tabindex="-1"><a class="header-anchor" href="#启用规则包" aria-hidden="true">#</a> 启用规则包</h3><p>分析方案 -&gt; 代码检查 -&gt;【Objective-C】代码规范规则包 -&gt; 启用/查看规则。</p><h3 id="更多" tabindex="-1"><a class="header-anchor" href="#更多" aria-hidden="true">#</a> 更多</h3><p>更多场景支持，欢迎提 issue 进行咨询扩展。</p>`,13),d=[a];function s(r,c){return n(),i("div",null,d)}const u=e(l,[["render",s],["__file","dependency_vul.html.vue"]]);export{u as default};
