import{_ as s,r as l,o as d,c as t,a as e,b as r,d as n,w as c,e as a}from"./app-697cd87e.js";const v={},u=a('<h1 id="error-prone-使用手册" tabindex="-1"><a class="header-anchor" href="#error-prone-使用手册" aria-hidden="true">#</a> Error Prone 使用手册</h1><h2 id="error-prone-介绍" tabindex="-1"><a class="header-anchor" href="#error-prone-介绍" aria-hidden="true">#</a> Error Prone 介绍</h2><blockquote><p>Error Prone是google开源的Java编译时检测工具，将常见的Java错误捕获为编译时错误，增强对java代码的类型分析，从而让开发人员及时发现问题</p></blockquote><h2 id="tca使用指引" tabindex="-1"><a class="header-anchor" href="#tca使用指引" aria-hidden="true">#</a> TCA使用指引</h2><p>TCA原有编译时检测工具JavaWarning获取java代码编译时的告警信息，现集成Error Prone规则至JavaWarning工具以增加获取Error Prone的错误告警信息。</p>',5),m=e("li",null,"在规则包中添加JavaWarning工具的Error Prone规则（可通过规则解决方法进行区分）；",-1),p=e("li",null,"客户端启动分析，在TCA Web页面上查看问题。",-1),g=e("h2",{id:"error-prone-配置",tabindex:"-1"},[e("a",{class:"header-anchor",href:"#error-prone-配置","aria-hidden":"true"},"#"),r(" Error Prone 配置")],-1),b=e("h3",{id:"通过bazel构建",tabindex:"-1"},[e("a",{class:"header-anchor",href:"#通过bazel构建","aria-hidden":"true"},"#"),r(" 通过Bazel构建")],-1),h=e("li",null,[r("Bazel在构建java项目时，默认打开了Error Prone，所以在本地配置Bazel环境，编写Bazel构建文件，"),e("code",null,"bazel build :project"),r("构建项目即可。")],-1),_={href:"https://bazel.build/?hl=zh-cn",target:"_blank",rel:"noopener noreferrer"},E=a(`<h3 id="maven-配置-error-prone" tabindex="-1"><a class="header-anchor" href="#maven-配置-error-prone" aria-hidden="true">#</a> Maven 配置 Error Prone</h3><p>编辑pom.xml文件将设置添加到maven-compiler-plugin，例如：</p><div class="language-xml line-numbers-mode" data-ext="xml"><pre class="language-xml"><code>&lt;build&gt;
    &lt;plugins&gt;
      &lt;plugin&gt;
        &lt;groupId&gt;org.apache.maven.plugins&lt;/groupId&gt;
        &lt;artifactId&gt;maven-compiler-plugin&lt;/artifactId&gt;
        &lt;version&gt;3.8.0&lt;/version&gt;
        &lt;configuration&gt;
          &lt;source&gt;8&lt;/source&gt;
          &lt;target&gt;8&lt;/target&gt;
          &lt;encoding&gt;UTF-8&lt;/encoding&gt;
          &lt;compilerArgs&gt;
            &lt;arg&gt;-XDcompilePolicy=simple&lt;/arg&gt;
            &lt;arg&gt;-Xplugin:ErrorProne&lt;/arg&gt;
          &lt;/compilerArgs&gt;
          &lt;annotationProcessorPaths&gt;
            &lt;path&gt;
              &lt;groupId&gt;com.google.errorprone&lt;/groupId&gt;
              &lt;artifactId&gt;error_prone_core&lt;/artifactId&gt;
              &lt;version&gt;\${error-prone.version}&lt;/version&gt;
            &lt;/path&gt;
            &lt;!-- Other annotation processors go here.

            If &#39;annotationProcessorPaths&#39; is set, processors will no longer be
            discovered on the regular -classpath; see also &#39;Using Error Prone
            together with other annotation processors&#39; below. --&gt;
          &lt;/annotationProcessorPaths&gt;
        &lt;/configuration&gt;
      &lt;/plugin&gt;
    &lt;/plugins&gt;
  &lt;/build&gt;
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>对于<code>JDK 16</code>或更高的版本，需要将以下内容<code>--add-exports</code>和<code>--add-opens</code>标志添加到<code>.mvn/jvm.config</code>文件中：</p><div class="language-html line-numbers-mode" data-ext="html"><pre class="language-html"><code>--add-exports jdk.compiler/com.sun.tools.javac.api=ALL-UNNAMED
--add-exports jdk.compiler/com.sun.tools.javac.file=ALL-UNNAMED
--add-exports jdk.compiler/com.sun.tools.javac.main=ALL-UNNAMED
--add-exports jdk.compiler/com.sun.tools.javac.model=ALL-UNNAMED
--add-exports jdk.compiler/com.sun.tools.javac.parser=ALL-UNNAMED
--add-exports jdk.compiler/com.sun.tools.javac.processing=ALL-UNNAMED
--add-exports jdk.compiler/com.sun.tools.javac.tree=ALL-UNNAMED
--add-exports jdk.compiler/com.sun.tools.javac.util=ALL-UNNAMED
--add-opens jdk.compiler/com.sun.tools.javac.code=ALL-UNNAMED
--add-opens jdk.compiler/com.sun.tools.javac.comp=ALL-UNNAMED
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>###命令行 Error Prone 支持<code>com.sun.source.util.Plugin</code>API，并且可以通过将 Error Prone 添加到<code>-processorpath</code>并设置<code>-Xplugin</code>标志来与<code>JDK 9</code>及更高版本一起使用：</p><div class="language-bash line-numbers-mode" data-ext="sh"><pre class="language-bash"><code>wget https://repo1.maven.org/maven2/com/google/errorprone/error_prone_core/\${EP_VERSION?}/error_prone_core-\${EP_VERSION?}-with-dependencies.jar
wget https://repo1.maven.org/maven2/org/checkerframework/dataflow-errorprone/3.15.0/dataflow-errorprone-3.15.0.jar
javac \\
  -J--add-exports=jdk.compiler/com.sun.tools.javac.api=ALL-UNNAMED \\
  -J--add-exports=jdk.compiler/com.sun.tools.javac.file=ALL-UNNAMED \\
  -J--add-exports=jdk.compiler/com.sun.tools.javac.main=ALL-UNNAMED \\
  -J--add-exports=jdk.compiler/com.sun.tools.javac.model=ALL-UNNAMED \\
  -J--add-exports=jdk.compiler/com.sun.tools.javac.parser=ALL-UNNAMED \\
  -J--add-exports=jdk.compiler/com.sun.tools.javac.processing=ALL-UNNAMED \\
  -J--add-exports=jdk.compiler/com.sun.tools.javac.tree=ALL-UNNAMED \\
  -J--add-exports=jdk.compiler/com.sun.tools.javac.util=ALL-UNNAMED \\
  -J--add-opens=jdk.compiler/com.sun.tools.javac.code=ALL-UNNAMED \\
  -J--add-opens=jdk.compiler/com.sun.tools.javac.comp=ALL-UNNAMED \\
  -XDcompilePolicy=simple \\
  -processorpath error_prone_core-\${EP_VERSION?}-with-dependencies.jar:dataflow-errorprone-3.15.0.jar \\
  &#39;-Xplugin:ErrorProne -XepDisableAllChecks -Xep:CollectionIncompatibleType:ERROR&#39; \\
  Example.java
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div>`,7),A=e("li",null,[r("对于"),e("code",null,"JDK 16"),r("以及更高的版本"),e("code",null,"--add-exports"),r("和"),e("code",null,"--add-opens"),r("参数是必须的")],-1),j=e("code",null,"JDK 8",-1),N={href:"https://github.com/google/error-prone/blob/f8e33bc460be82ab22256a7ef8b979d7a2cacaba/docs/installation.md",target:"_blank",rel:"noopener noreferrer"},L=e("h3",{id:"其他配置和注意事项",tabindex:"-1"},[e("a",{class:"header-anchor",href:"#其他配置和注意事项","aria-hidden":"true"},"#"),r(" 其他配置和注意事项")],-1),f={href:"https://errorprone.info/docs/installation",target:"_blank",rel:"noopener noreferrer"},x={href:"https://github.com/google/error-prone/blob/f8e33bc460be82ab22256a7ef8b979d7a2cacaba/docs/installation.md",target:"_blank",rel:"noopener noreferrer"};function k(P,D){const i=l("RouterLink"),o=l("ExternalLinkIcon");return d(),t("div",null,[u,e("ul",null,[m,e("li",null,[r("采用"),n(i,{to:"/en/guide/%E5%AE%A2%E6%88%B7%E7%AB%AF/%E6%9C%AC%E5%9C%B0%E5%88%86%E6%9E%90.html"},{default:c(()=>[r("TCA Client")]),_:1}),r("模式，根据客户端环境配置工具和编译命令，详情参考下文；")]),p]),g,b,e("ul",null,[h,e("li",null,[r("详情请参考"),e("a",_,[r("Bazel官方文档"),n(o)])])]),E,e("ul",null,[A,e("li",null,[r("对于"),j,r(",请参考"),e("a",N,[r("旧版本安装说明"),n(o)])])]),L,e("ul",null,[e("li",null,[r("Error Prone还支持通过Gradle和Ant配置，详情参考"),e("a",f,[r("Error Prone官方配置文档"),n(o)])]),e("li",null,[r("不同JDK版本参数有所不同，详情参考"),e("a",x,[r("旧版本安装说明"),n(o)])])])])}const M=s(v,[["render",k],["__file","Error-Prone.html.vue"]]);export{M as default};
