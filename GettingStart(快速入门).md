# 腾讯云代码分析快速入门

## 1. 部署服务

详见服务部署文档：[doc/deploy.md](doc/deploy.md)

## 2. 配置项目  
**Step 1：在浏览器输入http://<部署机IP>/，进入TCA主页，开始项目配置。**  
![homepage](https://tencent.github.io/CodeAnalysis/media/homepage.png)

**Step 2：创建团队及项目。**

<img src="https://tencent.github.io/CodeAnalysis/media/createTeam.png" width = "50%" /><img src="https://tencent.github.io/CodeAnalysis/media/createProject.png" width = "45%" />

**Step 3：登记代码库。输入代码库地址及配置凭证信息。**

<img src="https://tencent.github.io/CodeAnalysis/media/registerCodeRepo.png" width = "90%" />   

    注：在本地扫描模式下，待扫描的代码库需在客户端配置文件中配置本地路径，步骤3中登记的代码库并非最终实际扫描的代码库，详见客户端使用文档。

**Step 4：创建分析方案，配置代码检查规则包。首次扫描可勾选「普通创建」，根据待分析的语言及问题类型勾选「分析语言」及「功能」。**

<img src="https://tencent.github.io/CodeAnalysis/media/creataAnalysePlan.png" width = "50%" />
<img src="https://tencent.github.io/CodeAnalysis/media/planPage.png"/>

## 3. 启动客户端

详见客户端使用文档：[doc/client.md](doc/client.md)
