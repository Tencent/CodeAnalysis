# 【Java】强化安全规则包-使用手册
针对 Java 语言的强化代码安全规则包，属于 TCA 增强分析模块的能力之一，请参考[增强分析模块部署](https://tencent.github.io/CodeAnalysis/zh/quickStarted/enhanceDeploy.html)文档进行部署。


## CmdInject
### 概述
支持的语言：Java

CmdInject 规则用于检查代码中是否存在[`命令行注入漏洞`](https://owasp.org/www-community/attacks/Command_Injection)。
当使用childprocess等模块执行命令时，拼接了用户可控的输入，会导致命令执行漏洞。攻击者利用漏洞可以控制目标主机或者容器。

### 示例
```java
void bad(HttpServletRequest req, HttpServletResponse resp){
    String cmd = req.getParameter("cmd");
    Runtime rt = Runtime.getRuntime();
    rt.exec(cmd); // 触发规则
}
```

### 修复建议
需要评估childprocess等模块执行命令的使用，应限定或校验命令和参数的内容。

## PathTraversal

### 概述
支持的语言：Java

PathTraversal 规则用于检查代码中是否存在[`路径穿越漏洞`](https://owasp.org/www-community/attacks/Path_Traversal)。
操作文件时，应该限定文件的路径范围，如果拼接用户输入到文件路径，可能导致路径穿越漏洞。攻击者利用漏洞可以访问到文件系统上的任意文件，这可能导致信息泄漏等问题。

### 示例
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

### 修复建议
按业务需求，使用白名单限定后缀范围，校验并限定文件路径范围。

## SQLInject

### 概述
支持的语言：Java

SQLInject 规则用于检查代码中是否存在[`SQL注入漏洞`](https://en.wikipedia.org/wiki/SQL_injection)。
错误的拼接用户可控的值到 sql 语句，可能导致 sql 注入漏洞。攻击者可以修改 sql 语法来更改查询的目标或结果，泄露数据库敏感信息，也可以使用SQL文件操作攻击底层Web服务器。如果使用该 sql 查询进行授权认证，攻击者还可以用于提权。

### 示例
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

### 修复建议
SQL语句默认使用预编译并绑定变量，使用安全的ORM操作。

## SSRF

### 概述
支持的语言：Java

SSRF 规则用于检查代码中是否存在[`服务端请求伪造漏洞 SSRF(Server-side request forgery)`](https://en.wikipedia.org/wiki/Server-side_request_forgery)。
攻击者在未能取得服务器所有权限时，利用服务器漏洞以服务器的身份发送一条构造好的请求给服务器所在内网。

### 示例
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
        // 触发规则
        csrf.disable() 
      );
  }
}
```

### 修复建议
限定访问网络资源地址范围，请求网络资源应加密传输。

## XSS

### 概述
支持的语言：Java

XSS 规则用于检查代码中是否存在[`跨站脚本攻击漏洞 XSS(Cross-site scripting)`](https://en.wikipedia.org/wiki/Cross-site_scripting)。
如果 web 页面在动态展示数据时使用了用户的输入内容，没有对输入的内容过滤或者进行转义，黑客可以通过参数传入恶意代码，当用户浏览该页面时恶意代码会被执行。

### 示例
```java
void bad(HttpServletRequest req, HttpServletResponse resp){
    String id = request.getParameter("id") != null ? request.getParameter("id") : "0";
    Doc doc = getdetailsById(id);    
    byte b[] = doc.getUploaded();        
    try {
        response.setContentType("APPLICATION/OCTET-STREAM");
        String disHeader = "Attachment;Filename=" + doc.getName();
        response.setHeader("Content-Disposition", disHeader);
        ServletOutputStream out = response.getOutputStream();
        out.print(b);
    }
}
```

### 修复建议

在输出所有用户可控的数据时, 对数据做转义或者编码。
