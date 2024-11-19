# 贡献指南

欢迎报告Issue或提交Pull Request。建议在贡献代码前先阅读以下贡献指南。

## 报告问题

我们使用[Github Issues](https://github.com/Tencent/CodeAnalysis/issues)来跟踪漏洞和功能请求。

### 搜索已知issue

在您提交新的issue前，请搜索现有issue以查看是否已有人提交任何类似问题或功能请求，确认不存在重复的issue。

### 报告新issue

当您提交新的issue时，请尽量提供更多的信息，例如与问题相关的详细描述、屏幕截图、视频、logcat和导致崩溃的代码块。

## Pull Request

我们非常欢迎您提出Pull Request来帮助TCA变得更好，操作流程详见[PullRequests操作流程](./pr.md)。

### 分支管理

TCA有两个主要分支：

- `main` 分支：
	1. 它是最新的（预）发布分支。我们以 `main` 作为标签, 带有版本号 `v1.0.1`, `v1.0.2` ...
	2. **请不要在 `main` 分支提交任何PR.**
- `dev` 分支：
	1. 这是我们稳定发展的分支。经过全面测试后， `dev` 分支将合并到 `main` 分支的下一个版本。
	2. **请您将修复漏洞或开发新功能的PR提交到 `dev` 分支。**

### 提交Pull Request

代码团队将监控所有拉取请求，我们对其进行一些代码检查和测试。在所有测试通过后，我们将接受此PR。但它不会立即合并到 `main` 分支，这有一些延迟。

在提交拉取请求之前，请确保完成以下工作：

1. Fork [TCA仓库](https://github.com/Tencent/CodeAnalysis/blob/main/CONTRIBUTING.md)，并从 `main` 创建分支。
2. 如果您更改了API，请更新代码或文档。
3. 将版权声明添加到您添加的任何新文件的顶部。
4. 检查您的代码样式。
5. 测试您的代码，确保其可以正常运行。
6. 现在，您可以向 `dev` 分支提交Pull Request。

## 许可
[MIT LICENSE](https://github.com/Tencent/CodeAnalysis/blob/main/LICENSE.txt) 是 TCA 的开源许可证。任何人贡献的代码都受此许可证保护。在贡献代码之前，请确保您可以接受许可。