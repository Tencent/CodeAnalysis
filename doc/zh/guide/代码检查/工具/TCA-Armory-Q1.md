

# TCA-Armory-Q1工具介绍
TCA-Armory-Q1, 又名 tca_ql_cpp 主要用于分析Cpp质量问题。


# 规则详情

## 线程锁检查

包含规则:
- missing_lock
- dead_lock

在使用多线程对文件全局变量或类成员在进行读写时，工具会对未正确的进行上锁操作和上锁异常而引发死锁的情况进行检查。

支持的多线程标准库库包括（若有其他库需求可提issue）:
- pthread
- thread
#### missing_lock
missing_lock  如果发现多线程中某个全局变量在未持有锁便更新时，则会上报错误。

##### 代码示例
以下提供一个或多个 missing_loc 案例
在下面代码中，函数 increase1, increase2 皆以将 counter 加到 1000 为目的。如果使用 increase1 函数则有可能多个线程皆在 1000 时进入循环导致最后 counter结果大于 1000

```
int counter = 0;
std::mutex mtx;  // 保护counter
void increase1() {
    while (1) {
        if (counter <= 1000)
            counter++;  // defect: missing_lock
        else
            break;
    }
}
void increase2() {
    while (1) {
        mtx.lock();  // example_lock
        if (counter <= 1000)
            counter++;
        else
            break;
        mtx.unlock();  // example_release
    }
}
```

#### dead_lock
dead_lock 如果发现文件内存在 mtx1 -> mtx2 的上锁顺序时，另存在mtx2 -> mtx1 的上锁顺序，视为死锁或存在死锁的可能，则会上报错误。
死锁发生时程序将会卡死无法正常执行。

##### 规则参数
- better-lock: True or False 默认为 False

##### 代码示例
以下提供一个或多个 dead_lock 案例

在下面代码中，函数 increase 以将 counter 加到 1000 为目的。但在线程 1 中第一次释放 mtx 后，线程 2 的 mtx 上锁，此时线程1等待线程2释放mtx，线程2等待线程1释放mtx2，形成死锁，程序卡死。
```
int counter = 0;
std::mutex mtx;
std::mutex mtx2;
void increase() {
    while (1) {
        mtx.lock();
        mtx2.lock();
        mtx.unlock();
        mtx.lock();  // defect: dead_lock
        if (counter <= 1000)
            counter++;
        else
            break;
        mtx2.unlock();
        mtx.unlock()
    }
}
```

在下面代码中 线程函数increase1存在mtx -> mtx2 的顺序，increase2顺序为 mtx2 -> mtx；视为出现死锁。
```
void increase1() {
    while (1) {
        mtx.lock();
        mtx2.lock();
        if (counter <= 1000)
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
        if (counter <= 1000)
            counter++;
        else
            break;
        mtx2.unlock();
        mtx.unlock()
    }
}
```

以下案例在`better-lock`参数为`True`时将会生效
使用`better-lock`规则会检查在上锁期间若调用其他函数时将视为可能会出现预期之外的异常，且上锁期间应只做对全局变量操作以提升性能
```
void increase1() {
    while (1) {
        mtx.lock();
        if (counter <= 1000)
            counter++;
        else
            break;
        read_counter(counter);  // defect: dead_lock
        mtx.unlock()
    }
}
void read_counter(counter){
    std::cout << counter << std::endl;
    do_something_more();
}
void increase1() {
    while (1) {
        std::lock_guard<std::mutex> lk(mtx);  // good: 使用lock_guard会自动上锁解锁将不会检查dead_lock
        if (counter <= 1000)
            counter++;
        else
            break;
        read_counter(counter);
    }
}
```

## 资源泄漏检查
包含规则
- resource_leak

#### resource_leak
resource_leak 在程序申请了资源但并未按时释放时上报错误
目前场景包括：句柄打开时未关闭，指针分配内存后没有及时释放

##### 代码示例
以下将提供一个或多个resource_leak案例

```
int leak_example1(int c) {
    void *p = malloc(10); 
    if(c)
        return -1; // defect: if c "p" is leaked
    free(p);
    return 0;
}

int leak_example2() {
    void *p = malloc(10);
    void *q = malloc(20);
    if(!p || !q)
        return -1; // defect: "p" or "q" may be leaked if the other is NULL 
    /*...*/
    free(q);
    free(p);
    return 0;
}

void leak_example3(int c) {
    FILE *p = fopen("starwar.anakin", "rb");
    if(c)
        return;       // defect: leaking file pointer "p"
    fclose(p);
}
```


## 无效值检查
包含规则
- unused_value

#### unused_value
unused_value 检查那些赋予给变量的值是否正确被使用，存在连续两次赋予变量值的情况，视为第一次赋予的值未被正确使用，报出错误。
两次连续赋值可能存在条件控制语句出现错误、变量名拼写错误等情况。
##### 代码示例
以下提供一个或多个unused_value案例

以下函数会因为key的不同去不一样的神明，但实际上 Zeus Hades却永远不会使用到。
```
const char* key_value(const int key) {
    const char * value = 0;
    if (key != 0) {
        value = "Zeus";
    } else if (key != 1) {
        value = "Hades";
    } 
    if (key != 2) { // Should be 'else if' here.
        value = "Poseidon";  // defect: unused_value Zeus Hades  never used
    }
    else {
        value = "Unknow
    }
    return result;
}
```
以下继续提供几个unused_value代码
```
const char* key_value1(const int key) {
    const char * value = 0;
    value = "Zeus";  // defect: Zeus never used
    if (key == 1) {
        value = "Hades;
    } else if (key == 2) {
        value = "Poseidon";
    } else {  // May else need not be here
        value = "Unknow";
    }
    return value
}

const char* key_value2(const int key) {
    const char * value = 0;
    value = "Zeus";  // better Zeus used
    if (key == 1) {
        value = "Hades;
    } else if (key == 2) {
        value = "Poseidon";
    }
    return value
}

const char* key_value3(const int key) {
    const char * value = 0;
    if (key == 1) {
        value = "Hades;
    } else {
        value = "Poseidon";
    }
    value = "Zeus";  // defect: Hades Poseidon never used
    return value
}
```

## 数组溢出检查
包含规则
- array_overflow
- buff_overflow

#### array_overflow
array_overflow 检查数组越界的情况。不正确的缓存区访问可能损坏内存，导致程序崩溃或读取到权限外的内存。

##### 代码示例
以下提供一个或多个array_overflow案例

```
void foo() {
    int array[10];
    int i = get();
    // i = 9;
    if (i > 8 && i <= length(array)) {  // Shoud be i < length(array)
        array[i] = 1;  // defect: array[10] overflow
    }
    array[i] = 1;  // defect: array[10] overflow
}


void test(int i) {
    int n= 10;
    char *p = malloc(sizeof(int) * 10);
    int y = n;
    p[y] = 'a'; // defect: writing to buffer[y] overflow
}
```


#### buff_overflow
buff_overflow 检查`strcpy`,`strcat`字符串复制/拼接过程中长度不当导致的溢出， 同样`gets` `scanf`函数也视为不安全

##### 代码示例
以下提供一个或多个buff_overflow案例
```
void overflow1() {

    char a[4]={0};
        strcpy(a, "Poseidon");  // defect: len("Poseidon") > 4 strncpy is better
    return;
}

void overflow2() {
    char s1[10] = "1";
    char s2[] = "1234567890";
    strcat(s1, s2);  // defect: len(s1 + s2) > 10
    // strncat(s1, s2, 6)  // strncat is better
    return 0;
}

```

## 指针检查
包含规则
- func_ret_null
- func_ret_null_full
- use_after_free
- forward_null
- reverse_null
- glob_null_pointer

#### func_ret_null
func_ret_null 函数返回值可能为nullpointer，但是调用该函数时指针未经判空便进行使用<br>
在选用func_ret_null_full 时, 检查器会在项目内全局搜索空指针函数的调用情况，否则只会在相关文件内进行检查。

#### 代码示例
以下提供一个或多个func_ret_null代码案例

在下面代码中`test`函数中调用`get_name`可能返回空指针，在后续使用`name`指针前应该判断是否为空指针
```
// name.hpp

char* get_name(int id) {
    char* name = 0;
    if (id == 1) {
        name = "Zeus";
    } else if (id == 2) {
        name = "Hades"
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

```

在选用full_ret_null_full时，将会全局分析函数`get_name`调用情况
```
// third.cpp
# include "name.h"

void name_test(int i) {
    char* name = get_name(i);
    dosomething(name); // defect
}
```

#### use_after_free

use_after_free 检查当指针已经被释放但在后续仍然使用该指针的情况。

##### 代码示例
以下提供一个或多个use_after_free代码案例

通常情况下已经释放的指针只允许置空或重新指向新的值，不允许存在读取或作为函数参数使用。
```

void UAR() {
    int* p = new int[];
    p = get_array();
    dosomething(p);
    delete p;
    p = NULL;  // allow
    p = get_array();  // allow: get array again
    delete p;
    dosomething(p);  // defect: use as param
    std::cout << "p[0] = " << p[0] << std::endl;  // defect: read p
}
```

#### forward_null
forward_null 检查可能导致程序终止或运行时异常的错误。它查找指针或引用被检查是否为 null 或被赋值为 null，且之后被解引用的很多情况。


##### 规则参数
- trust_param True or False 默认为 True

##### 代码示例
以下提供一个或多个forward_null代码案例

指针曾经有过检查null的操作则会视为有可能为空指针，之后在未被确认为非空指针情况下直接使用。将会视为`forward_null`错误
```
void forward_null_1() {
    int * p;
    p = get_int_pointer();
    dosomething(p);
    if (p == NULL) {
        std::cout << "Null Pointer Find" << srd::endl;
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
```

以下案例在设置`trust_param`为`False`时将会生效，其将会默认认为函数参数存在空指针可能，必须确认无空指针可能时方可使用
```
void forward_null_2(int *p) {
    dosomething(p);     // defect: param p may NULL
    if (p != NULL) {    // means p may nullpointer here
        dosomething(p);
    }
    dosomething(p);     // defect forward_null:p may NULL
}
```

#### reverse_null
reverse_null 检查已经使用过指针，但在后续又对指针进行了判空操作；会被认为之前使用指针也有可能是空指针。

##### 代码示例
以下将提供一个或多个reverse_null案例

```
void reverse_null(int *p) {
    dosomething(p);      // use p
    if (p != NULL) {    // defect reverse_null: It means p may NULL
        dosomething(p);
    }
    ...
```

#### glob_null_pointer
glob_null_pointer 检查文件内全局指针是否为空，指针赋值将会被认为不为空指针，但检测到空指针判断则视为指针此时可能为空，如果在可能为空时使用则会报错

##### 代码示例
以下将提供一个或多个glob_null_pointer案例

```
int *p;


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
```

## 函数重写
包含规则
- function_override

仅类虚拟函数允许重写。

#### function_override
function_override 检查非虚拟函数重写的情况。

##### 代码示例
以下提供一个或多个function_override代码案例

```


class father{
    public:
        father(){};
        ~father(){};
    
    private:
        virtual void test(){};
        void test2(){ std::cout<<"hello";};
};

class man{};


class son: public father, public man{
    public:
        son(){};
        ~son(){};
    private:
        void test(){ std::cout<<"hello";};  // allow: virtual function override
        void test2(){ std::cout<<"hello";};  // defect: bad override
};
```
## 死代码检查

#### dead_code
dead_code 检查永远不会执行到的代码，主要为在同一作用域内 return, break 后的代码

##### 代码示例
以下提供一个或多个dead_code代码案例

```
// C/Cpp
void dead_code(int t) {
    int sum = 0;
    for (int i = 1; i <= 100; i++) {
        if (i == t) {
            break;
            sum = t;    // Defect: dead_code
        }
        sum += i;
    }
}
```

#### dead_branch
dead_branch 检查永远不会被执行到的分支代码，其原因可能是具有相同效果的控制语句或某些条件在特定情况下永远不会执行。

##### 代码示例

以下提供一个或多个dead_branch代码案例

```

void dead_branch(int i) {
    if (i < 100) {
        if ( i > 100) {     // Defect: dead_branch, i 属于 (-inf, 100) 不存在 (100, inf)的可能
            dosomething() ;
        }
        return;
    } else if (i >= 100) {
        if ( i < 99 ) {     // Defect: dead_branch, i 属于[100, inf) 不存在 (-inf, 99)的可能
            dosomething();
        }
        return;
    } else if (i < 10){     // Defect: dead_branch, 在前面分支中已经包含了所有i的可能，这里已经不存在 (-inf, 10)的可能
        dosomething();
    }
    else {                  // Defect: dead_branch, 在前面分支中已经包含了所有i的可能
        dosomething();
    }
    return;
}

```

## 变量初始化检查
包含规则
- uinit

#### uinit
uinit 检查变量在定义后直接使用，却没有初始化的场景；使用未初始化的变量 可能导致无法预测的行为、崩溃和安全漏洞。

##### 规则参数
- deep_level: true, false 设置为true时将会分析作为函数参数的情况，否则无视作为函数参数的使用。

##### 代码示例

以下提供一个或多个 uinit 代码案例


```

void test(char* t) {
    std::cout<< t << std::endl;     // Defect: p 作为函数参数，此处未初始化。
    return;
}


int uinit(int i) {
    int a;
    char * p;
    test(p);    // deep_level = true
    if (i < 10)
        a = 1;
    else
        i = 1;
    return a;   // Defect: i大于10时，a并未赋值
}
```
