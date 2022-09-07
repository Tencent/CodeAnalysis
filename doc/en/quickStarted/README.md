# Tencent Cloud Code Analysis


**Tencent Cloud Code Analysis** (TCA for short, code-named CodeDog inside the company early) is a comprehensive platform for code analysis and issue tracking. TCA consist of three components, **server, web and client**. It integrates of a number of self-developed tools, and also supports dynamic integration of code analysis tools in various programming languages.

**Code analysis** is a technology, using lexical analysis, syntax analysis, control-flow analysis, data-flow analysis to make a comprehensive analysis of the code, so as to verify whether the code meets the requirements of normative, security, reliability, maintainability and other indicators.

Using TCA can help team find normative, structural, security vulnerabilities and other issues in the code, continuously monitor the quality of the project code and issue alerts. At the same time, TCA opens up APIs to support connection with upstream and downstream systems, so as to integrate code analysis capabilities, ensure code quality, and be more conducive to inheriting an excellent team code culture.

![组件图](https://tencent.github.io/CodeAnalysis/media/Components.png)

![流程图](https://tencent.github.io/CodeAnalysis/media/Flow.png)

---

For the first experience, it is recommended that you use the [Docker deployment](./dockerDeploy.md) to quickly build and experience the Tencent Cloud code analysis platform for the first experience.

If you have more environmental requirements, you can also deploy Tencent Cloud Code Analysis Platform in the following two ways: 

- Deploy through [Docker-Compose](./dockercomposeDeploy.md) 

- Deploy through [source code](./codeDeploy.md)
