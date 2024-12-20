import{_ as d,a as l}from"./ProcessConfiguration2-c60284cc.js";import{_ as s,r as a,o,c as r,a as e,b as i,d as u,e as n}from"./app-697cd87e.js";const c={},v=n(`<h1 id="源码集成代码分析工具" tabindex="-1"><a class="header-anchor" href="#源码集成代码分析工具" aria-hidden="true">#</a> 源码集成代码分析工具</h1><h2 id="初识tca任务执行机制" tabindex="-1"><a class="header-anchor" href="#初识tca任务执行机制" aria-hidden="true">#</a> 初识TCA任务执行机制</h2><ol><li>TCA server在接收到开启分析的请求后根据所选规则生成对应的task_request，每个task_request对应一个工具的任务</li><li>TCA server将<code>task_request</code>分发到能够执行该工具的机器</li><li>TCA client在收到task_request后提取出本次任务的工具名也就是其中的<code>task_name</code>字段，字段对应于工具的<code>name</code>字段</li><li>TCA client按照<code>task_name</code>在client中的tool目录查找对应python启动脚本</li><li>执行python启动脚本中的内容</li></ol><h2 id="添加分析工具-以-tca-ql-php-为例" tabindex="-1"><a class="header-anchor" href="#添加分析工具-以-tca-ql-php-为例" aria-hidden="true">#</a> 添加分析工具（以 tca_ql_php 为例）</h2><p>根据上述的任务机制添加工具需要做到以下几点</p><ol><li>让server知道存在<code>tca_ql_php</code>工具及其所含的规则</li><li>让server知道哪些客户端可以执行<code>tca_ql_php</code>工具</li><li>client下载/找到工具所在目录及需要的环境</li><li>让client知道<code>tca_ql_php</code>对应的启动脚本是什么</li></ol><h3 id="如何让server知道存在相应工具" tabindex="-1"><a class="header-anchor" href="#如何让server知道存在相应工具" aria-hidden="true">#</a> 如何让Server知道存在相应工具</h3><ol><li><p>找到<code>server/projects/main/apps/scan_conf/management/commands/open_source</code>目录</p></li><li><p>创建工具json文件，json文件名尽量对应工具名称方便查看</p></li><li><p>json文件内容为（以 tca_ql_php 为例)</p></li></ol><div class="language-python line-numbers-mode" data-ext="py"><pre class="language-python"><code>[
    {
        &quot;name&quot;: &quot;tca_ql_php&quot;,
        &quot;display_name&quot;: &quot;Hades_PHP（展示名称用于前端展示使用）&quot;,
        &quot;description&quot;: &quot;工具描述&quot;,
        &quot;license&quot;: &quot;工具license&quot;,
        &quot;libscheme_set&quot;: [], # 暂时不需要
        &quot;task_processes&quot;: [
            &quot;analyze&quot;,
            &quot;datahandle&quot;,
            &quot;compile&quot;
        ],  # 工具进程，包含compile编译, analyze分析, datahandle数据处理
        &quot;scan_app&quot;: &quot;codelint&quot;,  # 代码分析统一为codelint
        &quot;scm_url&quot;: &quot;&quot;, # 暂时为空
        &quot;run_cmd&quot;: &quot;&quot;,
        &quot;envs&quot;: null, # 是否需要特殊环境，这里无需填写
        &quot;build_flag&quot;: false, # 是否需要编译命令才能运行
        &quot;checkrule_set&quot;: [  # 工具包含的规则
            {
                &quot;real_name&quot;: &quot;deser&quot;,  # 规则名
                &quot;display_name&quot;: &quot;反序列化漏洞&quot;,  # 规则前端展示，考虑各工具规则名可能晦涩难懂，设置展示名称方便查找
                &quot;severity&quot;: &quot;error&quot;,  # 规则等级 从上到下分为 fatal, error, warning, info 四个等级
                &quot;category&quot;: &quot;security&quot;,  # 规则类别。correctness 功能 security安全 performance性能 usability可用性 accessibility无障碍化 i18n国际化 convention代码风格 other其他
                &quot;rule_title&quot;: &quot;反序列化漏洞&quot;,  # 一句话概括规则简介
                &quot;rule_params&quot;: null,  # 规则参数
                &quot;languages&quot;: [  # 支持语言
                    &quot;php&quot;
                ],
                &quot;solution&quot;: &quot;&quot;,  # 建议的解决方法
                &quot;owner&quot;: &quot;&quot;,
                &quot;labels&quot;: [],
                &quot;description&quot;: &quot;&quot;,  # 规则详细介绍
            }
        ]
    }
]
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><ol start="4"><li>在<code>server/projects/main/</code>目录执行<code>python manage.py loadcheckers --dir open_source tca_ql_php</code> 加载工具进入数据库</li></ol><h2 id="让server知道哪些客户端可以执行tca-ql-php工具" tabindex="-1"><a class="header-anchor" href="#让server知道哪些客户端可以执行tca-ql-php工具" aria-hidden="true">#</a> 让server知道哪些客户端可以执行<code>tca_ql_php</code>工具</h2><ol><li>进入节点管理页面</li></ol><p><img src="`+d+'" alt="节点管理"></p><ol start="2"><li>选择其中一台机器 工具进程配置，勾选其工具进程</li></ol><p><img src="'+l+'" alt="工具进程"></p><h2 id="client下载-找到工具所在目录及需要的环境" tabindex="-1"><a class="header-anchor" href="#client下载-找到工具所在目录及需要的环境" aria-hidden="true">#</a> client下载/找到工具所在目录及需要的环境</h2>',16),m={href:"https://github.com/TCATools/puppy-tools-config.git",target:"_blank",rel:"noopener noreferrer"},p=e("li",null,"修改其中的 ini 配置文件，每个操作系统对应一个ini",-1),q=e("li",null,"以 tca_ql_php 为例需要做以下修改",-1),b=n(`<div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>; env_path 主要填写存放工具文件所在的相对目录，一般都存放/拉取在tools下，会在工具执行前加载到环境变量中提供使用
[env_path]
ZEUS_HOME   : Zeus
HADES_HOME  : Hades

; toolz_url
[tool_url] 主要填写工具的git仓库，这里因为 tca_ql_php 直接使用tools下的目录所以不用再进行额外拉取也无需再写
CPPCHECK    : \${base_value:git_url}/linux-cppcheck-1.78

; 各工具配置 以 tca_ql_php 为例
; env_path 填写上面需要加载的环境变量
; env_value 通用环境变量，一般无需填写如果有需求需要现在 [env_value] 中定义好再填写
; path 工具所在目录填写上面的定义
; tool_url 工具git仓库，使用本地相对目录故为空
[tca_ql_php]
env_path  : ZEUS_HOME;HADES_HOME
env_value :
path      : \${env_path:ZEUS_HOME};\${env_path:HADES_HOME}
tool_url  : 

</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="让client知道tca-ql-php对应的启动脚本是什么" tabindex="-1"><a class="header-anchor" href="#让client知道tca-ql-php对应的启动脚本是什么" aria-hidden="true">#</a> 让client知道<code>tca_ql_php</code>对应的启动脚本是什么</h2><ol><li><p>以上述步骤在<code>client/tool</code>目录添加脚本<code>tca_ql_php.py</code>作为启动脚本 注：启动脚本必须与工具名称相同</p></li><li><p>编写脚本</p></li></ol><h3 id="脚本编写规范" tabindex="-1"><a class="header-anchor" href="#脚本编写规范" aria-hidden="true">#</a> 脚本编写规范</h3><p>以<code>tca_ql_php</code>为例</p><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>
from task.codelintmodel import CodeLintModel
from util.logutil import LogPrinter
from util.subprocc import SubProcController

logger = LogPrinter()


class TcaQlPHP(CodeLintModel):
    # 代码分析工具集成基类CodeLintModel
    def __init__(self, params):
        logger.info(&quot;找到工具了Q_Q&quot;)
        super().__init__(params)

    def compile(self, params):
        logger.info(&quot;开始编译了Q_Q&quot;)
        build_cmd = params.get(&#39;build_cmd&#39;, None)  # 从params中获取编译命令, params内容可以在最后附录查看
        lang = &quot;php&quot;
        do_some_things()

    def analyze(self, params):
        logger.info(&quot;开始分析了Q_Q&quot;)
        lang = &quot;php&quot;
        HADES_HOME = envs.get(&quot;HADES_HOME&quot;, None)
        output_json = &quot;result.json&quot;
        sp = SubProcController(
            command=[&quot;Hades&quot;, &quot;analyze&quot;, &quot;test.php&quot;, &quot;-o&quot;, output_json],
            cwd=HADES_HOME,
            stdout_line_callback=subprocc_log,
            stderr_line_callback=subprocc_log,
        )
        sp.wait()  # 执行工具分析命令
        issues = []
        # 工具结果输出到output_json，具体工具可能有所不同
        if os.path.exists(output_json):
            with open(output_json, &quot;r&quot;) as result_reader:
                result = json.load(result_reader)
                issues.extend(result)
        return issues

tool = TcaQlPHP  # 必须，必须包含tool变量并且为该工具的类
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><ol><li>脚本必须包含analyze方法，如果有配置编译进程也需要相应的compile方法来做编译相关工作，datahandle函数不用自定义基类方法已经够用了。方法执行顺序为 compile -&gt; analyze -&gt; datahandle</li><li>params参数为<code>task_request</code>中的<code>task_params</code>字段，具体字段将在最后附录进行说明</li><li>anlyze方法必须有返回值，返回值为issue列表，issue格式为</li></ol><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>{
    &quot;path&quot;: &quot;文件相对路径&quot;,
    &quot;line&quot;: &quot;行号，int类型&quot;,
    &quot;column&quot;: &quot;列号, int类型，如果工具没有输出列号信息，可以用0代替&quot;,
    &quot;msg&quot;: &quot;提示信息&quot;,
    &quot;rule&quot;: &quot;规则名称,可以根据需要输出不同的规则名&quot;,
    &quot;refs&quot;: [
        {
            &quot;line&quot;: &quot;回溯行号&quot;, 
            &quot;msg&quot;: &quot;提示信息&quot;, 
            &quot;tag&quot;: &quot;用一个词简要标记该行信息，比如uninit_member,member_decl等，如果没有也可以都写成一样的&quot;, 
            &quot;path&quot;: &quot;回溯行所在文件绝对路径&quot;
        },
        ...
    ]
}
说明：
    refs：可选，记录问题回溯路径信息。比如当前文件的回溯路径其他的3行代码，可以将这三行的路径及提示信息，按顺序添加到refs数组中。
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h1 id="pr" tabindex="-1"><a class="header-anchor" href="#pr" aria-hidden="true">#</a> PR</h1><p>如果有意公开您添加的工具欢迎发起PR</p><p>注：别忘了puppy-tool-config 也需要PR</p><h1 id="附录" tabindex="-1"><a class="header-anchor" href="#附录" aria-hidden="true">#</a> 附录</h1><h2 id="params-表格" tabindex="-1"><a class="header-anchor" href="#params-表格" aria-hidden="true">#</a> params 表格</h2><table><thead><tr><th>字段</th><th>说明</th><th>类型</th></tr></thead><tbody><tr><td>scan_languages</td><td>语言</td><td>字符串列表如 [&quot;python&quot;, &quot;php&quot;]</td></tr><tr><td>pre_cmd</td><td>编译前置命令</td><td>字符串</td></tr><tr><td>build_cmd</td><td>编译命令</td><td>字符串</td></tr><tr><td>envs</td><td>额外环境变量</td><td>字符串</td></tr><tr><td>scm_last_revision</td><td>上次成功分析的代码版本，增量使用</td><td>字符串</td></tr><tr><td>incr_scan</td><td>是否为增量分析</td><td>bool</td></tr><tr><td>rules</td><td>规则名称列表，只有规则名</td><td>字符串列表</td></tr><tr><td>rule_list</td><td>详细的规则列表包含规则名和规则参数等</td><td>字典列表</td></tr><tr><td>checktool</td><td>工具详细信息，执行一般用不到</td><td>字典</td></tr><tr><td>path_filters</td><td>过滤路径</td><td>字典</td></tr><tr><td>scm_url</td><td>代码库url</td><td>字符串</td></tr><tr><td>source_dir</td><td>代码库本地目录</td><td>字符串</td></tr><tr><td>work_dir</td><td>本次任务的work_dir目录</td><td>字符串</td></tr><tr><td>project_id</td><td>分析项目id</td><td>int</td></tr><tr><td>repo_id</td><td>仓库id</td><td>int</td></tr><tr><td>task_id</td><td>任务id</td><td>int</td></tr><tr><td>job_id</td><td>本次分析的id</td><td>int</td></tr></tbody></table>`,14);function _(h,g){const t=a("ExternalLinkIcon");return o(),r("div",null,[v,e("ol",null,[e("li",null,[i("找到puppy-tool-config若没有额外配置则为默认代码库"),e("a",m,[i("https://github.com/TCATools/puppy-tools-config.git"),u(t)])]),p,q]),b])}const y=s(c,[["render",_],["__file","集成代码分析工具.html.vue"]]);export{y as default};
