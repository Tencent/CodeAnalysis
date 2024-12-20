import{_ as e,o as i,c as n,e as l}from"./app-697cd87e.js";const d={},a=l(`<ul><li><a href="#tca-armory-q1%E5%B7%A5%E5%85%B7%E4%BB%8B%E7%BB%8D">TCA-Armory-Q1工具介绍</a></li><li><a href="#%E8%A7%84%E5%88%99%E8%AF%A6%E6%83%85">规则详情</a><ul><li><a href="#%E7%BA%BF%E7%A8%8B%E9%94%81%E6%A3%80%E6%9F%A5">线程锁检查</a><ul><li><a href="#missing_lock">missing_lock</a><ul><li><a href="#%E4%BB%A3%E7%A0%81%E7%A4%BA%E4%BE%8B">代码示例</a></li></ul></li><li><a href="#dead_lock">dead_lock</a><ul><li><a href="#%E8%A7%84%E5%88%99%E5%8F%82%E6%95%B0">规则参数</a></li><li><a href="#%E4%BB%A3%E7%A0%81%E7%A4%BA%E4%BE%8B-1">代码示例</a></li></ul></li></ul></li><li><a href="#%E8%B5%84%E6%BA%90%E6%B3%84%E6%BC%8F%E6%A3%80%E6%9F%A5">资源泄漏检查</a><ul><li><a href="#resource_leak">resource_leak</a><ul><li><a href="#%E4%BB%A3%E7%A0%81%E7%A4%BA%E4%BE%8B-2">代码示例</a></li><li><a href="#todo">TODO</a></li></ul></li></ul></li><li><a href="#%E6%97%A0%E6%95%88%E5%80%BC%E6%A3%80%E6%9F%A5">无效值检查</a><ul><li><a href="#unused_value">unused_value</a><ul><li><a href="#%E4%BB%A3%E7%A0%81%E7%A4%BA%E4%BE%8B-3">代码示例</a></li></ul></li></ul></li><li><a href="#%E6%95%B0%E7%BB%84%E6%BA%A2%E5%87%BA%E6%A3%80%E6%9F%A5">数组溢出检查</a><ul><li><a href="#array_overflow">array_overflow</a><ul><li><a href="#%E4%BB%A3%E7%A0%81%E7%A4%BA%E4%BE%8B-4">代码示例</a></li><li><a href="#todo-1">TODO</a></li></ul></li><li><a href="#buff_overflow">buff_overflow</a><ul><li><a href="#%E4%BB%A3%E7%A0%81%E7%A4%BA%E4%BE%8B-5">代码示例</a></li></ul></li></ul></li><li><a href="#%E6%8C%87%E9%92%88%E6%A3%80%E6%9F%A5">指针检查</a><ul><li><a href="#func_ret_null">func_ret_null</a></li><li><a href="#%E4%BB%A3%E7%A0%81%E7%A4%BA%E4%BE%8B-6">代码示例</a></li><li><a href="#use_after_free">use_after_free</a><ul><li><a href="#%E4%BB%A3%E7%A0%81%E7%A4%BA%E4%BE%8B-7">代码示例</a></li></ul></li><li><a href="#forward_null">forward_null</a><ul><li><a href="#%E8%A7%84%E5%88%99%E5%8F%82%E6%95%B0-1">规则参数</a></li><li><a href="#%E4%BB%A3%E7%A0%81%E7%A4%BA%E4%BE%8B-8">代码示例</a></li></ul></li><li><a href="#reverse_null">reverse_null</a><ul><li><a href="#%E4%BB%A3%E7%A0%81%E7%A4%BA%E4%BE%8B-9">代码示例</a></li></ul></li><li><a href="#glob_null_pointer">glob_null_pointer</a><ul><li><a href="#%E4%BB%A3%E7%A0%81%E7%A4%BA%E4%BE%8B-10">代码示例</a></li></ul></li></ul></li><li><a href="#%E5%87%BD%E6%95%B0%E9%87%8D%E5%86%99">函数重写</a><ul><li><a href="#function_override">function_override</a><ul><li><a href="#%E4%BB%A3%E7%A0%81%E7%A4%BA%E4%BE%8B-11">代码示例</a></li></ul></li></ul></li></ul></li></ul><h1 id="tca-armory-q1工具介绍" tabindex="-1"><a class="header-anchor" href="#tca-armory-q1工具介绍" aria-hidden="true">#</a> TCA-Armory-Q1工具介绍</h1><p>TCA-Armory-Q1, 又名 tca_ql_cpp 主要用于分析Cpp质量问题。</p><h1 id="规则详情" tabindex="-1"><a class="header-anchor" href="#规则详情" aria-hidden="true">#</a> 规则详情</h1><h2 id="线程锁检查" tabindex="-1"><a class="header-anchor" href="#线程锁检查" aria-hidden="true">#</a> 线程锁检查</h2><p>包含规则:</p><ul><li>missing_lock</li><li>dead_lock</li></ul><p>在使用多线程对文件全局变量或类成员在进行读写时，工具会对未正确的进行上锁操作和上锁异常而引发死锁的情况进行检查。</p><p>支持的多线程标准库库包括（若有其他库需求可提issue）:</p><ul><li>pthread</li><li>thread</li></ul><h4 id="missing-lock" tabindex="-1"><a class="header-anchor" href="#missing-lock" aria-hidden="true">#</a> missing_lock</h4><p>missing_lock 如果发现多线程中某个全局变量在未持有锁便更新时，则会上报错误。</p><h5 id="代码示例" tabindex="-1"><a class="header-anchor" href="#代码示例" aria-hidden="true">#</a> 代码示例</h5><p>以下提供一个或多个 missing_loc 案例 在下面代码中，函数 increase1, increase2 皆以将 counter 加到 1000 为目的。如果使用 increase1 函数则有可能多个线程皆在 1000 时进入循环导致最后 counter结果大于 1000</p><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>int counter = 0;
std::mutex mtx;  // 保护counter
void increase1() {
    while (1) {
        if (counter &lt;= 1000)
            counter++;  // defect: missing_lock
        else
            break;
    }
}
void increase2() {
    while (1) {
        mtx.lock();  // example_lock
        if (counter &lt;= 1000)
            counter++;
        else
            break;
        mtx.unlock();  // example_release
    }
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h4 id="dead-lock" tabindex="-1"><a class="header-anchor" href="#dead-lock" aria-hidden="true">#</a> dead_lock</h4><p>dead_lock 如果发现文件内存在 mtx1 -&gt; mtx2 的上锁顺序时，另存在mtx2 -&gt; mtx1 的上锁顺序，视为死锁或存在死锁的可能，则会上报错误。 死锁发生时程序将会卡死无法正常执行。</p><h5 id="规则参数" tabindex="-1"><a class="header-anchor" href="#规则参数" aria-hidden="true">#</a> 规则参数</h5><ul><li>better-lock: True or False 默认为 False</li></ul><h5 id="代码示例-1" tabindex="-1"><a class="header-anchor" href="#代码示例-1" aria-hidden="true">#</a> 代码示例</h5><p>以下提供一个或多个 dead_lock 案例</p><p>在下面代码中，函数 increase 以将 counter 加到 1000 为目的。但在线程 1 中第一次释放 mtx 后，线程 2 的 mtx 上锁，此时线程1等待线程2释放mtx，线程2等待线程1释放mtx2，形成死锁，程序卡死。</p><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>int counter = 0;
std::mutex mtx;
std::mutex mtx2;
void increase() {
    while (1) {
        mtx.lock();
        mtx2.lock();
        mtx.unlock();
        mtx.lock();  // defect: dead_lock
        if (counter &lt;= 1000)
            counter++;
        else
            break;
        mtx2.unlock();
        mtx.unlock()
    }
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>在下面代码中 线程函数increase1存在mtx -&gt; mtx2 的顺序，increase2顺序为 mtx2 -&gt; mtx；视为出现死锁。</p><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>void increase1() {
    while (1) {
        mtx.lock();
        mtx2.lock();
        if (counter &lt;= 1000)
            counter++;
        else
            break;
        mtx2.unlock();
        mtx.unlock()
    }
}
void increase2() {
    while (1) {
        mtx2.lock();
        mtx.lock();  // defect: dead_lock; 
        if (counter &lt;= 1000)
            counter++;
        else
            break;
        mtx2.unlock();
        mtx.unlock()
    }
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>以下案例在<code>better-lock</code>参数为<code>True</code>时将会生效 使用<code>better-lock</code>规则会检查在上锁期间若调用其他函数时将视为可能会出现预期之外的异常，且上锁期间应只做对全局变量操作以提升性能</p><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>void increase1() {
    while (1) {
        mtx.lock();
        if (counter &lt;= 1000)
            counter++;
        else
            break;
        read_counter(counter);  // defect: dead_lock
        mtx.unlock()
    }
}
void read_counter(counter){
    std::cout &lt;&lt; counter &lt;&lt; std::endl;
    do_something_more();
}
void increase1() {
    while (1) {
        std::lock_guard&lt;std::mutex&gt; lk(mtx);  // good: 使用lock_guard会自动上锁解锁将不会检查dead_lock
        if (counter &lt;= 1000)
            counter++;
        else
            break;
        read_counter(counter);
    }
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="资源泄漏检查" tabindex="-1"><a class="header-anchor" href="#资源泄漏检查" aria-hidden="true">#</a> 资源泄漏检查</h2><p>包含规则</p><ul><li>resource_leak</li></ul><h4 id="resource-leak" tabindex="-1"><a class="header-anchor" href="#resource-leak" aria-hidden="true">#</a> resource_leak</h4><p>resource_leak 在程序申请了资源但并未按时释放时上报错误 目前场景包括：句柄打开时未关闭，指针分配内存后没有及时释放</p><h5 id="代码示例-2" tabindex="-1"><a class="header-anchor" href="#代码示例-2" aria-hidden="true">#</a> 代码示例</h5><p>以下将提供一个或多个resource_leak案例</p><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>int leak_example1(int c) {
    void *p = malloc(10); 
    if(c)
        return -1; // defect: if c &quot;p&quot; is leaked
    free(p);
    return 0;
}

int leak_example2() {
    void *p = malloc(10);
    void *q = malloc(20);
    if(!p || !q)
        return -1; // defect: &quot;p&quot; or &quot;q&quot; may be leaked if the other is NULL 
    /*...*/
    free(q);
    free(p);
    return 0;
}

void leak_example3(int c) {
    FILE *p = fopen(&quot;starwar.anakin&quot;, &quot;rb&quot;);
    if(c)
        return;       // defect: leaking file pointer &quot;p&quot;
    fclose(p);
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h5 id="todo" tabindex="-1"><a class="header-anchor" href="#todo" aria-hidden="true">#</a> TODO</h5><p>指针为返回值目前不会进行上报与检查，需要后期增加对返回值是否释放的检查</p><h2 id="无效值检查" tabindex="-1"><a class="header-anchor" href="#无效值检查" aria-hidden="true">#</a> 无效值检查</h2><p>包含规则</p><ul><li>unused_value</li></ul><h4 id="unused-value" tabindex="-1"><a class="header-anchor" href="#unused-value" aria-hidden="true">#</a> unused_value</h4><p>unused_value 检查那些赋予给变量的值是否正确被使用，存在连续两次赋予变量值的情况，视为第一次赋予的值未被正确使用，报出错误。 两次连续赋值可能存在条件控制语句出现错误、变量名拼写错误等情况。</p><h5 id="代码示例-3" tabindex="-1"><a class="header-anchor" href="#代码示例-3" aria-hidden="true">#</a> 代码示例</h5><p>以下提供一个或多个unused_value案例</p><p>以下函数会因为key的不同去不一样的神明，但实际上 Zeus Hades却永远不会使用到。</p><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>const char* key_value(const int key) {
    const char * value = 0;
    if (key != 0) {
        value = &quot;Zeus&quot;;
    } else if (key != 1) {
        value = &quot;Hades&quot;;
    } 
    if (key != 2) { // Should be &#39;else if&#39; here.
        value = &quot;Poseidon&quot;;  // defect: unused_value Zeus Hades  never used
    }
    else {
        value = &quot;Unknow
    }
    return result;
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>以下继续提供几个unused_value代码</p><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>const char* key_value1(const int key) {
    const char * value = 0;
    value = &quot;Zeus&quot;;  // defect: Zeus never used
    if (key == 1) {
        value = &quot;Hades;
    } else if (key == 2) {
        value = &quot;Poseidon&quot;;
    } else {  // May else need not be here
        value = &quot;Unknow&quot;;
    }
    return value
}

const char* key_value2(const int key) {
    const char * value = 0;
    value = &quot;Zeus&quot;;  // better Zeus used
    if (key == 1) {
        value = &quot;Hades;
    } else if (key == 2) {
        value = &quot;Poseidon&quot;;
    }
    return value
}

const char* key_value3(const int key) {
    const char * value = 0;
    if (key == 1) {
        value = &quot;Hades;
    } else {
        value = &quot;Poseidon&quot;;
    }
    value = &quot;Zeus&quot;;  // defect: Hades Poseidon never used
    return value
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="数组溢出检查" tabindex="-1"><a class="header-anchor" href="#数组溢出检查" aria-hidden="true">#</a> 数组溢出检查</h2><p>包含规则</p><ul><li>array_overflow</li><li>buff_overflow</li></ul><h4 id="array-overflow" tabindex="-1"><a class="header-anchor" href="#array-overflow" aria-hidden="true">#</a> array_overflow</h4><p>array_overflow 检查数组越界的情况。不正确的缓存区访问可能损坏内存，导致程序崩溃或读取到权限外的内存。</p><h5 id="代码示例-4" tabindex="-1"><a class="header-anchor" href="#代码示例-4" aria-hidden="true">#</a> 代码示例</h5><p>以下提供一个或多个array_overflow案例</p><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>void foo() {
    int array[10];
    int i = get();
    // i = 9;
    if (i &gt; 8 &amp;&amp; i &lt;= length(array)) {  // Shoud be i &lt; length(array)
        array[i] = 1;  // defect: array[10] overflow
    }
    array[i] = 1;  // defect: array[10] overflow
}


void test(int i) {
    int n= 10;
    char *p = malloc(sizeof(int) * 10);
    int y = n;
    p[y] = &#39;a&#39;; // defect: writing to buffer[y] overflow
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h5 id="todo-1" tabindex="-1"><a class="header-anchor" href="#todo-1" aria-hidden="true">#</a> TODO</h5><ul><li>提供规则参数支持函数参数作为数组或索引的情况检查</li></ul><h4 id="buff-overflow" tabindex="-1"><a class="header-anchor" href="#buff-overflow" aria-hidden="true">#</a> buff_overflow</h4><p>buff_overflow 检查<code>strcpy</code>,<code>strcat</code>字符串复制/拼接过程中长度不当导致的溢出， 同样<code>gets</code> <code>scanf</code>函数也视为不安全</p><h5 id="代码示例-5" tabindex="-1"><a class="header-anchor" href="#代码示例-5" aria-hidden="true">#</a> 代码示例</h5><p>以下提供一个或多个buff_overflow案例</p><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>void overflow1() {

    char a[4]={0};
        strcpy(a, &quot;Poseidon&quot;);  // defect: len(&quot;Poseidon&quot;) &gt; 4 strncpy is better
    return;
}

void overflow2() {
    char s1[10] = &quot;1&quot;;
    char s2[] = &quot;1234567890&quot;;
    strcat(s1, s2);  // defect: len(s1 + s2) &gt; 10
    // strncat(s1, s2, 6)  // strncat is better
    return 0;
}

</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="指针检查" tabindex="-1"><a class="header-anchor" href="#指针检查" aria-hidden="true">#</a> 指针检查</h2><p>包含规则</p><ul><li>func_ret_null</li><li>func_ret_null_full</li><li>use_after_free</li><li>forward_null</li><li>reverse_null</li><li>glob_null_pointer</li></ul><h4 id="func-ret-null" tabindex="-1"><a class="header-anchor" href="#func-ret-null" aria-hidden="true">#</a> func_ret_null</h4><p>func_ret_null 函数返回值可能为nullpointer，但是调用该函数时指针未经判空便进行使用<br> 在选用func_ret_null_full 时, 检查器会在项目内全局搜索空指针函数的调用情况，否则只会在相关文件内进行检查。</p><h4 id="代码示例-6" tabindex="-1"><a class="header-anchor" href="#代码示例-6" aria-hidden="true">#</a> 代码示例</h4><p>以下提供一个或多个func_ret_null代码案例</p><p>在下面代码中<code>test</code>函数中调用<code>get_name</code>可能返回空指针，在后续使用<code>name</code>指针前应该判断是否为空指针</p><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>// name.hpp

char* get_name(int id) {
    char* name = 0;
    if (id == 1) {
        name = &quot;Zeus&quot;;
    } else if (id == 2) {
        name = &quot;Hades&quot;
    } else {
        return nullpointer;
    }
    return name;
}

void test(int i) {
    char* name = get_name(i);
    dosomething(name);  // defect: name may nullpointer should check it
    if (name != nullpointer) {
        dosomething(name);  // good
    }
}

</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>在选用full_ret_null_full时，将会全局分析函数<code>get_name</code>调用情况</p><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>// third.cpp
# include &quot;name.h&quot;

void name_test(int i) {
    char* name = get_name(i);
    dosomething(name); // defect
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h4 id="use-after-free" tabindex="-1"><a class="header-anchor" href="#use-after-free" aria-hidden="true">#</a> use_after_free</h4><p>use_after_free 检查当指针已经被释放但在后续仍然使用该指针的情况。</p><h5 id="代码示例-7" tabindex="-1"><a class="header-anchor" href="#代码示例-7" aria-hidden="true">#</a> 代码示例</h5><p>以下提供一个或多个use_after_free代码案例</p><p>通常情况下已经释放的指针只允许置空或重新指向新的值，不允许存在读取或作为函数参数使用。</p><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>
void UAR() {
    int* p = new int[];
    p = get_array();
    dosomething(p);
    delete p;
    p = NULL;  // allow
    p = get_array();  // allow: get array again
    delete p;
    dosomething(p);  // defect: use as param
    std::cout &lt;&lt; &quot;p[0] = &quot; &lt;&lt; p[0] &lt;&lt; std::endl;  // defect: read p
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h4 id="forward-null" tabindex="-1"><a class="header-anchor" href="#forward-null" aria-hidden="true">#</a> forward_null</h4><p>forward_null 检查可能导致程序终止或运行时异常的错误。它查找指针或引用被检查是否为 null 或被赋值为 null，且之后被解引用的很多情况。</p><h5 id="规则参数-1" tabindex="-1"><a class="header-anchor" href="#规则参数-1" aria-hidden="true">#</a> 规则参数</h5><ul><li>trust_param True or False 默认为 True</li></ul><h5 id="代码示例-8" tabindex="-1"><a class="header-anchor" href="#代码示例-8" aria-hidden="true">#</a> 代码示例</h5><p>以下提供一个或多个forward_null代码案例</p><p>指针曾经有过检查null的操作则会视为有可能为空指针，之后在未被确认为非空指针情况下直接使用。将会视为<code>forward_null</code>错误</p><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>void forward_null_1() {
    int * p;
    p = get_int_pointer();
    dosomething(p);
    if (p == NULL) {
        std::cout &lt;&lt; &quot;Null Pointer Find&quot; &lt;&lt; srd::endl;
        // return;      // prefer: if return here
    } else {
        dosomething(p);     // good: p is not NULL
    }
    dosomething(p);     // defect forward_null: p may NULL
}


void forward_null_2(int *p) {
    dosomething(p);
    if (p == NULL) {
        return;
    } else {
        dosomething(p);     // good: p is not NULL
    }
    dosomething(p);     // good
    ...
    if (p != NULL) {    // means p may nullpointer here
        dosomething(p);
    }
    dosomething(p);     // defect forward_null:p may NULL
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>以下案例在设置<code>trust_param</code>为<code>False</code>时将会生效，其将会默认认为函数参数存在空指针可能，必须确认无空指针可能时方可使用</p><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>void forward_null_2(int *p) {
    dosomething(p);     // defect: param p may NULL
    if (p != NULL) {    // means p may nullpointer here
        dosomething(p);
    }
    dosomething(p);     // defect forward_null:p may NULL
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h4 id="reverse-null" tabindex="-1"><a class="header-anchor" href="#reverse-null" aria-hidden="true">#</a> reverse_null</h4><p>reverse_null 检查已经使用过指针，但在后续又对指针进行了判空操作；会被认为之前使用指针也有可能是空指针。</p><h5 id="代码示例-9" tabindex="-1"><a class="header-anchor" href="#代码示例-9" aria-hidden="true">#</a> 代码示例</h5><p>以下将提供一个或多个reverse_null案例</p><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>void reverse_null(int *p) {
    dosomething(p);      // use p
    if (p != NULL) {    // defect reverse_null: It means p may NULL
        dosomething(p);
    }
    ...
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h4 id="glob-null-pointer" tabindex="-1"><a class="header-anchor" href="#glob-null-pointer" aria-hidden="true">#</a> glob_null_pointer</h4><p>glob_null_pointer 检查文件内全局指针是否为空，指针赋值将会被认为不为空指针，但检测到空指针判断则视为指针此时可能为空，如果在可能为空时使用则会报错</p><h5 id="代码示例-10" tabindex="-1"><a class="header-anchor" href="#代码示例-10" aria-hidden="true">#</a> 代码示例</h5><p>以下将提供一个或多个glob_null_pointer案例</p><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>int *p;


void thread1() {
    p = get_int_pointer();      // p is not NULL
    dosomething(p);     // good
    if (p != NULL) {
        something(p);   // good
    }
    something(p);  // defect: p may NULL, because check p before
}


void thread2() {
    *p = 6;     // defect: p may NULL
    if (p != NULL) {
        something(p);   // good
    }
    something(p);  // defect: p may NULL
}
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="函数重写" tabindex="-1"><a class="header-anchor" href="#函数重写" aria-hidden="true">#</a> 函数重写</h2><p>包含规则</p><ul><li>function_override</li></ul><p>仅类虚拟函数允许重写。</p><h4 id="function-override" tabindex="-1"><a class="header-anchor" href="#function-override" aria-hidden="true">#</a> function_override</h4><p>function_override 检查非虚拟函数重写的情况。</p><h5 id="代码示例-11" tabindex="-1"><a class="header-anchor" href="#代码示例-11" aria-hidden="true">#</a> 代码示例</h5><p>以下提供一个或多个function_override代码案例</p><div class="language-text line-numbers-mode" data-ext="text"><pre class="language-text"><code>

class father{
    public:
        father(){};
        ~father(){};
    
    private:
        virtual void test(){};
        void test2(){ std::cout&lt;&lt;&quot;hello&quot;;};
};

class man{};


class son: public father, public man{
    public:
        son(){};
        ~son(){};
    private:
        void test(){ std::cout&lt;&lt;&quot;hello&quot;;};  // allow: virtual function override
        void test2(){ std::cout&lt;&lt;&quot;hello&quot;;};  // defect: bad override
};
</code></pre><div class="line-numbers" aria-hidden="true"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div>`,109),s=[a];function r(u,v){return i(),n("div",null,s)}const t=e(d,[["render",r],["__file","TCA-Armory-Q1.html.vue"]]);export{t as default};
