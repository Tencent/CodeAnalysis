# 依赖漏洞扫描规则包

## 概述
该规则包可分析项目依赖组件，以及依赖组件中是否存在漏洞等问题。辅助开发者准确分析到依赖组件的安全性，选用安全可靠的依赖组件。

规则包中将漏洞规则分为“低危漏洞”、“中危漏洞”、“高危漏洞”三个等级，扫描出有漏洞的组件，TCA会提供问题组件名称和版本、漏洞情况介绍，以及可用的修复版本（如获取到）。

已支持语言：C/C++、C#、Go、Java、JavaScript、PHP、Python、Ruby、Scala、TypeScript等。

## 示例

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">

    <parent>
        <groupId>org.javaweb.vuln</groupId>
        <artifactId>javaweb-vuln</artifactId>
        <version>3.0.3</version>
    </parent>

    <dependencies>

        <dependency>
            <groupId>org.apache.struts</groupId>
            <artifactId>struts2-core</artifactId>
            <!-- 触发规则  -->
            <version>2.1.8</version>
            <exclusions>
                <exclusion>
                    <groupId>org.freemarker</groupId>
                    <artifactId>freemarker</artifactId>
                </exclusion>

                <exclusion>
                    <groupId>org.springframework</groupId>
                    <artifactId>spring-test</artifactId>
                </exclusion>

                <exclusion>
                    <groupId>commons-fileupload</groupId>
                    <artifactId>commons-fileupload</artifactId>
                </exclusion>
            </exclusions>
        </dependency>

    </dependencies>

</project>
```

## 快速体验
TCA 现已支持依赖漏洞扫描规则包，可以在 TCA 分析方案中搜索勾选该规则包，快速体验。

### 启用规则包
分析方案 -> 代码检查 ->【Objective-C】代码规范规则包 -> 启用/查看规则。

### 更多

更多场景支持，欢迎提 issue 进行咨询扩展。
