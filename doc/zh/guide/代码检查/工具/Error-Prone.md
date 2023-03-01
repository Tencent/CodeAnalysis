# Error Prone 使用手册

## Error Prone 介绍

> Error Prone是google开源的Java编译时检测工具，将常见的Java错误捕获为编译时错误，增强对java代码的类型分析，从而让开发人员及时发现问题

## TCA使用指引

TCA原有编译时检测工具JavaWarning获取java代码编译时的告警信息，现集成Error Prone规则至JavaWarning工具以增加获取Error Prone的错误告警信息。
- 在规则包中添加JavaWarning工具的Error Prone规则（可通过规则解决方法进行区分）；
- 采用[TCA Client](../../../guide/客户端/本地分析.md)模式，根据客户端环境配置工具和编译命令，详情参考下文；
- 客户端启动分析，在TCA Web页面上查看问题。


## Error Prone 配置

### 通过Bazel构建

- Bazel在构建java项目时，默认打开了Error Prone，所以在本地配置Bazel环境，编写Bazel构建文件，`bazel build :project`构建项目即可。
- 详情请参考[Bazel官方文档](https://bazel.build/?hl=zh-cn)

### Maven 配置 Error Prone

编辑pom.xml文件将设置添加到maven-compiler-plugin，例如：
```xml
<build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.8.0</version>
        <configuration>
          <source>8</source>
          <target>8</target>
          <encoding>UTF-8</encoding>
          <compilerArgs>
            <arg>-XDcompilePolicy=simple</arg>
            <arg>-Xplugin:ErrorProne</arg>
          </compilerArgs>
          <annotationProcessorPaths>
            <path>
              <groupId>com.google.errorprone</groupId>
              <artifactId>error_prone_core</artifactId>
              <version>${error-prone.version}</version>
            </path>
            <!-- Other annotation processors go here.

            If 'annotationProcessorPaths' is set, processors will no longer be
            discovered on the regular -classpath; see also 'Using Error Prone
            together with other annotation processors' below. -->
          </annotationProcessorPaths>
        </configuration>
      </plugin>
    </plugins>
  </build>
```
对于`JDK 16`或更高的版本，需要将以下内容`--add-exports`和`--add-opens`标志添加到`.mvn/jvm.config`文件中：
```html
--add-exports jdk.compiler/com.sun.tools.javac.api=ALL-UNNAMED
--add-exports jdk.compiler/com.sun.tools.javac.file=ALL-UNNAMED
--add-exports jdk.compiler/com.sun.tools.javac.main=ALL-UNNAMED
--add-exports jdk.compiler/com.sun.tools.javac.model=ALL-UNNAMED
--add-exports jdk.compiler/com.sun.tools.javac.parser=ALL-UNNAMED
--add-exports jdk.compiler/com.sun.tools.javac.processing=ALL-UNNAMED
--add-exports jdk.compiler/com.sun.tools.javac.tree=ALL-UNNAMED
--add-exports jdk.compiler/com.sun.tools.javac.util=ALL-UNNAMED
--add-opens jdk.compiler/com.sun.tools.javac.code=ALL-UNNAMED
--add-opens jdk.compiler/com.sun.tools.javac.comp=ALL-UNNAMED
```

###命令行
Error Prone 支持`com.sun.source.util.Plugin`API，并且可以通过将 Error Prone 添加到`-processorpath`并设置`-Xplugin`标志来与`JDK 9`及更高版本一起使用：
```shell
wget https://repo1.maven.org/maven2/com/google/errorprone/error_prone_core/${EP_VERSION?}/error_prone_core-${EP_VERSION?}-with-dependencies.jar
wget https://repo1.maven.org/maven2/org/checkerframework/dataflow-errorprone/3.15.0/dataflow-errorprone-3.15.0.jar
javac \
  -J--add-exports=jdk.compiler/com.sun.tools.javac.api=ALL-UNNAMED \
  -J--add-exports=jdk.compiler/com.sun.tools.javac.file=ALL-UNNAMED \
  -J--add-exports=jdk.compiler/com.sun.tools.javac.main=ALL-UNNAMED \
  -J--add-exports=jdk.compiler/com.sun.tools.javac.model=ALL-UNNAMED \
  -J--add-exports=jdk.compiler/com.sun.tools.javac.parser=ALL-UNNAMED \
  -J--add-exports=jdk.compiler/com.sun.tools.javac.processing=ALL-UNNAMED \
  -J--add-exports=jdk.compiler/com.sun.tools.javac.tree=ALL-UNNAMED \
  -J--add-exports=jdk.compiler/com.sun.tools.javac.util=ALL-UNNAMED \
  -J--add-opens=jdk.compiler/com.sun.tools.javac.code=ALL-UNNAMED \
  -J--add-opens=jdk.compiler/com.sun.tools.javac.comp=ALL-UNNAMED \
  -XDcompilePolicy=simple \
  -processorpath error_prone_core-${EP_VERSION?}-with-dependencies.jar:dataflow-errorprone-3.15.0.jar \
  '-Xplugin:ErrorProne -XepDisableAllChecks -Xep:CollectionIncompatibleType:ERROR' \
  Example.java
```
- 对于`JDK 16`以及更高的版本`--add-exports`和`--add-opens`参数是必须的
- 对于`JDK 8`,请参考[旧版本安装说明](https://github.com/google/error-prone/blob/f8e33bc460be82ab22256a7ef8b979d7a2cacaba/docs/installation.md)

### 其他配置和注意事项
- Error Prone还支持通过Gradle和Ant配置，详情参考[Error Prone官方配置文档](https://errorprone.info/docs/installation)
- 不同JDK版本参数有所不同，详情参考[旧版本安装说明](https://github.com/google/error-prone/blob/f8e33bc460be82ab22256a7ef8b979d7a2cacaba/docs/installation.md)