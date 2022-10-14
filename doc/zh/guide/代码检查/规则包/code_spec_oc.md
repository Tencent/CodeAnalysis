
# 【Objective-C】代码规范规则包

该规则包针对 Objective-C/C++ 语言进行代码规范相关检查。

## 规则列表

- [ObjectiveC/Copyright](https://tencent.github.io/CodeAnalysis/zh/guide/代码检查/工具/TCA-Armory-C1.html#ObjectiveC/Copyright)
- [ObjectiveC/Indent](https://tencent.github.io/CodeAnalysis/zh/guide/代码检查/工具/TCA-Armory-C1.html#ObjectiveC/Indent)
- [ObjectiveC/MaxLinesPerFunction](https://tencent.github.io/CodeAnalysis/zh/guide/代码检查/工具/TCA-Armory-C1.html#ObjectiveC/MaxLinesPerFunction)
- [ObjectiveC/MissingDocInterface](https://tencent.github.io/CodeAnalysis/zh/guide/代码检查/工具/TCA-Armory-C1.html#ObjectiveC/MissingDocInterface)
- [ObjectiveC/MissingDocProperty](https://tencent.github.io/CodeAnalysis/zh/guide/代码检查/工具/TCA-Armory-C1.html#ObjectiveC/MissingDocProperty)
- [ObjectiveC/MissingDocProtocol](https://tencent.github.io/CodeAnalysis/zh/guide/代码检查/工具/TCA-Armory-C1.html#ObjectiveC/MissingDocProtocol)
- [ObjectiveC/ParameterCount](https://tencent.github.io/CodeAnalysis/zh/guide/代码检查/工具/TCA-Armory-C1.html#ObjectiveC/ParameterCount)
- [ObjectiveC/ClassNaming](https://tencent.github.io/CodeAnalysis/zh/guide/代码检查/工具/TCA-Armory-C1.html#ObjectiveC/ClassNaming)
- [ObjectiveC/FunctionNaming](https://tencent.github.io/CodeAnalysis/zh/guide/代码检查/工具/TCA-Armory-C1.html#ObjectiveC/FunctionNaming)
- [ObjectiveC/GlobalVariableNaming](https://tencent.github.io/CodeAnalysis/zh/guide/代码检查/工具/TCA-Armory-C1.html#ObjectiveC/GlobalVariableNaming)
- [ObjectiveC/LocalVariableNaming](https://tencent.github.io/CodeAnalysis/zh/guide/代码检查/工具/TCA-Armory-C1.html#ObjectiveC/LocalVariableNaming)
- [ObjectiveC/MacroNaming](https://tencent.github.io/CodeAnalysis/zh/guide/代码检查/工具/TCA-Armory-C1.html#ObjectiveC/MacroNaming)
- [ObjectiveC/MethodNaming](https://tencent.github.io/CodeAnalysis/zh/guide/代码检查/工具/TCA-Armory-C1.html#ObjectiveC/MethodNaming)
- [ObjectiveC/ParameterNaming](https://tencent.github.io/CodeAnalysis/zh/guide/代码检查/工具/TCA-Armory-C1.html#ObjectiveC/ParameterNaming)
- [ObjectiveC/MaxLineLength](https://tencent.github.io/CodeAnalysis/zh/guide/代码检查/工具/TCA-Armory-C1.html#ObjectiveC/MaxLineLength)

## 启用规则包
分析方案 -> 代码检查 ->【Objective-C】代码规范规则包 -> 启用/查看规则。

## 格式化工具
为了帮助你正确地格式化代码，我们建议你使用clang-format进行代码自动格式化。工具可直接通过 Homebrew 进行安装：
```bash
brew install clang-format
```
安装完成后将 .clang-format 配置文件置于工程根目录，执行 clang-format -i FILE.m 即可完成自动格式化。目前格式化工具配置仅支持11.0版本。
