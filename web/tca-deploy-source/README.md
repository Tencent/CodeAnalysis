# TCA 腾讯云代码分析 前端 VM 部署文档

## 前置条件

1. Linux 环境

2. 系统已安装 nginx

3. TCA Server 服务已部署完毕，具备后端服务地址

## 部署步骤

1. clone 到服务器合适位置，建议/data 目录下，并进入该库根目录下。

2. 方式一：执行`sh init.sh -d`即可：设置默认的环境变量，安装前端资源，配置 hosts、nginx 等，启动 nginx 服务

    方式二：先执行`source config.sh`设置环境变量，再执行`sh init.sh`

3. 如果需要对默认环境变量进行调整，可`vi config.sh`文件，再执行步骤2

> 注：以下是 `init.sh` 环境变量配置。如不按照步骤2执行，可人工 `export 相关环境变量` 后再执行 `init.sh`

|                      Name | 说明                                                      |
| ------------------------: | :-------------------------------------------------------- |
|                SERVER_ENV | 访问的后端地址，必填项                                    |
|       INGRESS_SERVER_NAME | ingress 配置的服务名称，默认 tca.tencent.com              |
|              INGRESS_PORT | ingress 配置的端口，默认 80                               |

## 其他

### 重新部署前端

1. 方式一：`sh reset.sh -d`

2. 方式二：先执行`source config.sh`，再执行 `sh reset.sh`

### 更新前端

1. pull 最新代码

2. 方式一：直接执行 `sh update.sh param` 即可

    其中 `param` 可以是 `all` `framework` `layout` `login` `analysis` `document` 其中的一个或多个，代表更新不同的模块，多个用`,`分隔，

    ```bash
    # 如更新全部
    sh update.sh all

    # 如更新layout前端、帮助文档前端
    sh update.sh layout,document

    # 如更新layout前端、analysis前端
    sh update.sh layout,analysis
    ```

    方式二：先人工 `export 相关环境变量` 后再执行 `sh update.sh`

    ```bash
    # 如更新全部
    export UPDATE_All=TRUE
    sh update.sh

    # 如仅更新layout前端
    export UPDATE_LAYOUT=TRUE
    ```

> 注：以下是更新前端的环境变量配置，用于方式二。

|            Name | 说明                 |
| --------------: | :------------------- |
|      UPDATE_ALL | 全部更新             |
|     UPDATE_FRAMEWORK | 更新 framework 基座     |
|   UPDATE_LAYOUT | 更新 tca-layout 微前端   |
|    UPDATE_LOGIN | 更新 login 微前端    |
| UPDATE_ANALYSIS | 更新 tca-analysis 微前端 |
|     UPDATE_DOCUMENT | 更新 tca-document     |

### 停止服务

`nginx -s stop`
