# TCA-Armory-C1 使用手册

TCA-Armory-C1 属于 TCA 的增强分析模块。

## 功能
- Objective-C/C++ 代码规范
- C/C++/Java 代码安全

## 准备
- 需要事先部署好 [CLS 微服务](https://tencent.github.io/CodeAnalysis/zh/quickStarted/enhanceDeploy.html)

## 规则介绍

### CmdInject
#### 概述
支持的语言：Java

CmdInject 规则用于检查代码中是否存在[`命令行注入漏洞`](https://owasp.org/www-community/attacks/Command_Injection)。
当使用 childprocess 等模块执行命令时，拼接了用户可控的输入，会导致命令执行漏洞。攻击者利用漏洞可以控制目标主机或者容器。

#### 参数设置
无

#### 示例
```java
void bad(HttpServletRequest req, HttpServletResponse resp){
    String cmd = req.getParameter("cmd");
    Runtime rt = Runtime.getRuntime();
    rt.exec(cmd); // 触发规则
}
```

#### 修复建议
需要评估 childprocess 等模块执行命令的使用，应限定或校验命令和参数的内容。


### PathTraversal

#### 概述
支持的语言：Java

PathTraversal 规则用于检查代码中是否存在[`路径穿越漏洞`](https://owasp.org/www-community/attacks/Path_Traversal)。
操作文件时，应该限定文件的路径范围，如果拼接用户输入到文件路径，可能导致路径穿越漏洞。攻击者利用漏洞可以访问到文件系统上的任意文件，这可能导致信息泄漏等问题。

#### 参数设置
无

#### 示例
```java
void bad(HttpServletRequest req, HttpServletResponse resp){
    String image = req.getParameter("image");
    File file = new File("resources/images/", image); // 触发规则

    if (!file.exists()) {
        return Response.status(Status.NOT_FOUND).build();
    }

    return Response.ok().entity(new FileInputStream(file)).build();
}
```

#### 修复建议
按业务需求，使用白名单限定后缀范围，校验并限定文件路径范围。


### SQLInject

#### 概述
支持的语言：Java

SQLInject 规则用于检查代码中是否存在[`SQL注入漏洞`](https://en.wikipedia.org/wiki/SQL_injection)。
错误的拼接用户可控的值到 sql 语句，可能导致 sql 注入漏洞。攻击者可以修改 sql 语法来更改查询的目标或结果，泄露数据库敏感信息，也可以使用SQL文件操作攻击底层Web服务器。如果使用该 sql 查询进行授权认证，攻击者还可以用于提权。

#### 参数设置
无
#### 示例
```java
void bad(HttpServletRequest req, HttpServletResponse resp){
    String id = req.getParameter("id");
    Connection conn = null;
    Statement statement = null;
    ResultSet rs = null;

    Class.forName("com.mysql.cj.jdbc.Driver");
    conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/sec_sql", "root", "admin888");
    String sql = "select * from userinfo where id = " + id;
    statement = conn.createStatement();
    statement.executeUpdate(sql); // 触发规则
}
```

#### 修复建议
SQL 语句默认使用预编译并绑定变量，使用安全的ORM操作。

### SSRF

#### 概述
支持的语言：Java

SSRF 规则用于检查代码中是否存在[`服务端请求伪造漏洞 SSRF(Server-side request forgery)`](https://en.wikipedia.org/wiki/Server-side_request_forgery)。
攻击者在未能取得服务器所有权限时，利用服务器漏洞以服务器的身份发送一条构造好的请求给服务器所在内网。

#### 参数设置
无
#### 示例
```java
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;

@EnableWebSecurity
@Configuration
public class WebSecurityConfig extends WebSecurityConfigurerAdapter {
  @Override
  protected void configure(HttpSecurity http) throws Exception {
    http
      .csrf(csrf ->
        csrf.disable() // 触发规则
      );
  }
}
```

#### 修复建议
限定访问网络资源地址范围，请求网络资源应加密传输。

### XSS

#### 概述
支持的语言：Java

XSS 规则用于检查代码中是否存在[`跨站脚本攻击漏洞 XSS(Cross-site scripting)`](https://en.wikipedia.org/wiki/Cross-site_scripting)。
如果 web 页面在动态展示数据时使用了用户的输入内容，没有对输入的内容过滤或者进行转义，黑客可以通过参数传入恶意代码，当用户浏览该页面时恶意代码会被执行。

#### 参数设置
无
#### 示例
```java
void bad(HttpServletRequest req, HttpServletResponse resp){
    String id = request.getParameter("id") != null ? request.getParameter("id") : "0";
    Doc doc = getdetailsById(id);    
    byte[] b = doc.getUploaded();        
    try {
        response.setContentType("APPLICATION/OCTET-STREAM");
        String disHeader = "Attachment;Filename=" + doc.getName();
        response.setHeader("Content-Disposition", disHeader);
        ServletOutputStream out = response.getOutputStream();
        out.print(b); // 触发规则
    }
}
```

#### 修复建议

在输出所有用户可控的数据时, 对数据做转义或者编码。

### ObjectiveC/Copyright

#### 概述
检查 Objective-C/C++ 代码文件的copyright信息。

#### 参数设置
无

#### 示例
```objc
// 触发规则
@interface Test : NSObject
@end

```

#### 修复建议

在代码文件头部添加 Copyright 信息。比如：
```objc
// Copyright (c) xxxx Tencent. All rights reserved.
//

@interface Test : NSObject
@end

```

### ObjectiveC/Indent

#### 概述
检查 Objective-C/C++ 代码文件的缩进。

#### 参数设置

- IndentStyle: 可选 spaces 空格 和 tabs `\t` ，默认是 spaces；
- IndentSize: 缩进长度，默认是4。

参考以下示例：
```ini
IndentStyle=spaces
IndentSize=4
```

#### 示例
```objc
for (int i = 0; i < 10; i++) {
  doThings(); // 触发规则
}
```

#### 修复建议

调整为对应的缩进方式。比如默认是4个空格缩进。

```objc
for (int i = 0; i < 10; i++) {
    doThings(); // 触发规则
}
```

### ObjectiveC/MaxLinesPerFunction

#### 概述
检查 Objective-C/C++ 代码中超出行数长度阈值的函数。

#### 参数设置
- LineThreshold: 方法长度阈值，默认是100。

参考以下示例：
```ini
LineThreshold=100
```

#### 示例
无

#### 修复建议

可以基于单一职责原则拆分函数，缩减函数长度。

### ObjectiveC/MissingDocInterface

#### 概述
检查 Objective-C/C++ 代码中 interface 是否有注释信息。

#### 参数设置
无

#### 示例
无

#### 修复建议
为 inferface 增加注释。

### ObjectiveC/MissingDocProperty

#### 概述
检查 Objective-C/C++ 代码中 Property 是否有注释信息。

#### 参数设置
无

#### 示例
无

#### 修复建议
为 Property 增加注释。

### ObjectiveC/MissingDocProtocol

#### 概述
检查 Objective-C/C++ 代码中 Protocol 是否有注释信息。

#### 参数设置
无

#### 示例
无

#### 修复建议
为 Protocol 增加注释。

### ObjectiveC/ParameterCount

#### 概述
检查 Objective-C/C++ 代码中方法的参数个数是否超过阈值。

#### 参数设置
- Max: 参数个数阈值，默认是6。

参考以下示例：
```ini
Max=6
```

#### 示例

无。

#### 修复建议
参数个数越少越好，多于 6 个参数时建议考虑重构。


### ObjectiveC/ClassNaming

#### 概述
检查 Objective-C/C++ 代码中 class 名称是否符合命名规范。

#### 参数设置
- ClassCase: 命名格式，可选 CamelCase 首字母小写驼峰式、UPPER_CASE 全部大写、LOWER_CASE 全部小写、camelBack 首字母大写驼峰式，默认是 CamelCase。

参考以下示例：
```ini
ClassCase=CamelCase
```

#### 示例

无。

#### 修复建议
修改 class 名称符合命名规范。

### ObjectiveC/FunctionNaming

#### 概述
检查 Objective-C/C++ 代码中 Function 名称是否符合命名规范。

#### 参数设置
- FunctionCase: 命名格式，可选 CamelCase 首字母小写驼峰式、UPPER_CASE 全部大写、LOWER_CASE 全部小写、camelBack 首字母大写驼峰式，默认是 camelBack。

参考以下示例：
```ini
FunctionCase=camelBack
```

#### 示例

无。

#### 修复建议
修改 Function 名称符合命名规范。

### ObjectiveC/GlobalVariableNaming

#### 概述
检查 Objective-C/C++ 代码中 GlobalVariable 名称是否符合命名规范。

#### 参数设置
- GlobalVariablePrefix: 全局变量前缀，默认是 `g` ；
- GlobalVariableCase: 命名格式，可选 CamelCase 首字母小写驼峰式、UPPER_CASE 全部大写、LOWER_CASE 全部小写、camelBack 首字母大写驼峰式，默认是 camelBack。

参考以下示例：
```ini
GlobalVariablePrefix=g
GlobalVariableCase=camelBack
```

#### 示例

无。

#### 修复建议
修改 GlobalVariable 名称符合命名规范。

### ObjectiveC/LocalVariableNaming

#### 概述
检查 Objective-C/C++ 代码中 LocalVariable 名称是否符合命名规范。

#### 参数设置
- LocalVariableCase: 命名格式，可选 CamelCase 首字母小写驼峰式、UPPER_CASE 全部大写、LOWER_CASE 全部小写、camelBack 首字母大写驼峰式，默认是 camelBack。

参考以下示例：
```ini
LocalVariableCase=camelBack
```

#### 示例

无。

#### 修复建议
修改 LocalVariable 名称符合命名规范。


### ObjectiveC/MacroNaming

#### 概述
检查 Objective-C/C++ 代码中 Macro 名称是否符合命名规范。

#### 参数设置
- MacroCase: 命名格式，可选 CamelCase 首字母小写驼峰式、UPPER_CASE 全部大写、LOWER_CASE 全部小写、camelBack 首字母大写驼峰式，默认是 UPPER_CASE。

参考以下示例：
```ini
MacroCase=UPPER_CASE
```

#### 示例

无。

#### 修复建议
修改 Macro 名称符合命名规范。

### ObjectiveC/MethodNaming

#### 概述
检查 Objective-C/C++ 代码中 Method 名称是否符合命名规范。

#### 参数设置
- MethodCase: 命名格式，可选 CamelCase 首字母小写驼峰式、UPPER_CASE 全部大写、LOWER_CASE 全部小写、camelBack 首字母大写驼峰式，默认是 camelBack。

参考以下示例：
```ini
MethodCase=camelBack
```

#### 示例

无。

#### 修复建议
修改 Method 名称符合命名规范。

### ObjectiveC/ParameterNaming

#### 概述
检查 Objective-C/C++ 代码中 Parameter 名称是否符合命名规范。

#### 参数设置
- ParameterCase: 命名格式，可选 CamelCase 首字母小写驼峰式、UPPER_CASE 全部大写、LOWER_CASE 全部小写、camelBack 首字母大写驼峰式，默认是 camelBack。

参考以下示例：
```ini
ParameterCase=camelBack
```

#### 示例

无。

#### 修复建议
修改 Parameter 名称符合命名规范。

### ObjectiveC/MaxLineLength

#### 概述
检查 Objective-C/C++ 代码中一行长度是否超过阈值。

#### 参数设置
- tabWidth: 缩进宽度，默认是4；
- MaxLineLength: 长度阈值，默认是150。

参考以下示例：
```ini
tabWidth=4
MaxLineLength=150
```

#### 示例

无。

#### 修复建议
通过换行、优化逻辑等方式，缩减一行长度。
