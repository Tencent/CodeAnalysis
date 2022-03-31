# TCA 腾讯云代码分析 前端 VM 部署文档

## 前置条件

1. Linux 环境

2. 系统已安装 nginx

3. TCA Server 服务已部署完毕，具备后端服务地址

## 部署步骤

1. **进入前端部署源码目录**
  
    进入web服务目录，并切换至`tca-deploy-source`目录，将其视为工作目录（假设工作目录为 `/data/CodeAnalysis/web/tca-deploy-source`）

2. **部署/更新前端服务**

    ```bash
    # 部署、更新都使用此命令
    sh ./scripts/deploy.sh init -d
    ```

    具体请查阅部署脚本内容，可根据业务调整配置。

3. **额外说明**

    `tca-deploy-source/scripts/config.sh` 已配置默认环境变量，用户可根据需要调整环境变量再部署前端服务，具体可查阅脚本内容。
