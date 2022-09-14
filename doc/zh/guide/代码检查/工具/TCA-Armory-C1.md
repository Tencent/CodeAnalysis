# TCA-Armory-C1 使用手册

TCA-Armory-C1 属于 TCA 的增强分析模块。

## 功能
- Objective-C/C++ 代码规范
- C/C++/Java 代码安全

## 准备
- 需要事先部署好 [CLS 微服务](https://tencent.github.io/CodeAnalysis/zh/quickStarted/enhanceDeploy.html)

## 规则
|   规则    |   概览    | 参数 | 参数示例 |
| :-------- | :------- | :------- | :------- |
| ObjectiveC/Copyright | 检查代码文件的copyright信息 | 无 | 无 |
| ObjectiveC/Indent | 检查代码文件的缩进 | IndentStyle: 可选 spaces 空格 和 tabs `\t` ，默认是 spaces <br> IndentSize: 缩进长度，默认是4 | IndentStyle=spaces <br> IndentSize=4 |
| ObjectiveC/MaxLinesPerFunction | 检查超出行数长度阈值的函数 | LineThreshold: 方法长度阈值，默认是100 | LineThreshold=100 |
| ObjectiveC/MissingDocInterface | 检查接口需要注释信息 | 无 | 无 |
| ObjectiveC/MissingDocProperty | 检查属性是否有注释 | 无 | 无 |
| ObjectiveC/MissingDocProtocol | 检查protocol是否有注释 | 无 | 无 |
| ObjectiveC/ParameterCount | 检查方法的参数个数 | Max: 参数个数阈值，默认是6 | Max=6 |
| ObjectiveC/ClassNaming | 检查class命名格式 | ClassCase: 命名格式，可选 CamelCase 首字母小写驼峰式、UPPER_CASE 全部大写、LOWER_CASE 全部小写、camelBack 首字母大写驼峰式，默认是 CamelCase ｜ ClassCase=CamelCase |
| ObjectiveC/FunctionNaming | 检查函数命名格式 | FunctionCase: 命名格式，可选 CamelCase 首字母小写驼峰式、UPPER_CASE 全部大写、LOWER_CASE 全部小写、camelBack 首字母大写驼峰式，默认是 camelBack | FunctionCase=camelBack |
| ObjectiveC/GlobalVariableNaming | 检查全局变量的命名格式 | GlobalVariablePrefix: 全局变量前缀，默认是`g` <br> GlobalVariableCase: 命名格式，可选 CamelCase 首字母小写驼峰式、UPPER_CASE 全部大写、LOWER_CASE 全部小写、camelBack 首字母大写驼峰式，默认是 camelBack | GlobalVariablePrefix=g <br> GlobalVariableCase=camelBack |
| ObjectiveC/LocalVariableNaming | 检查局部变量的命名格式 | LocalVariableCase: 命名格式，可选 CamelCase 首字母小写驼峰式、UPPER_CASE 全部大写、LOWER_CASE 全部小写、camelBack 首字母大写驼峰式，默认是 camelBack | LocalVariableCase=camelBack |
| ObjectiveC/MacroNaming | 检查macro命名格式 | MacroCase: 命名格式，可选 CamelCase 首字母小写驼峰式、UPPER_CASE 全部大写、LOWER_CASE 全部小写、camelBack 首字母大写驼峰式，默认是 UPPER_CASE | MacroCase=UPPER_CASE |
| ObjectiveC/MaxLineLength | 检查文件长度 | tabWidth: 缩进宽度，默认是4 <br> MaxLineLength: 长度阈值，默认是150 |  tabWidth=4 <br> MaxLineLength=150 |
| ObjectiveC/MethodNaming | 检查方法命名格式 | MethodCase: 命名格式，可选 CamelCase 首字母小写驼峰式、UPPER_CASE 全部大写、LOWER_CASE 全部小写、camelBack 首字母大写驼峰式，默认是 camelBack | MethodCase=camelBack |
| ObjectiveC/ParameterNaming | 检查参数命名格式 | ParameterCase: 命名格式，可选 CamelCase 首字母小写驼峰式、UPPER_CASE 全部大写、LOWER_CASE 全部小写、camelBack 首字母大写驼峰式，默认是 camelBack | ParameterCase=camelBack |
| CmdInject | 命令行注入漏洞 | 无 | 无 |
| PathTraversal | 路径穿越漏洞 | 无 | 无 |
| SQLInject | SQL注入 | 无 | 无 |
| SSRF | 服务端请求伪造漏洞 | 无 | 无 |
| XSS | 跨站脚本攻击漏洞 | 无 | 无 |
