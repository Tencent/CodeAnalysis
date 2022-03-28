# TCA Web 部署

## 工程结构

TCA Web 采用 [Lerna](https://www.lernajs.cn/) 进行 `monorepo` 管理。

> [Lerna GitHub地址](https://github.com/lerna/lerna)
>
> [Lerna 中文命令文档](http://www.febeacon.com/lerna-docs-zh-cn/)

由 `framework`、`login`、`tca-layout`、`tca-analysis`、`tca-manage`微前端以及`tca-document`前端帮助文档组成。

### packages 目录说明

- `shared`: 公共模块

- `framework`: 微前端基座

- `login`: 登录微前端

- `tca-layout`: 腾讯云代码分析layout微前端

- `tca-analysis`: 腾讯云代码分析analysis微前端

- `tca-manage`: 腾讯云代码分析后台管理微前端

- `tca-document`: 腾讯云代码分析帮助文档

## 基于构建后资源部署（tca-deploy-source）

已将当前版本各个微前端构建打包到此目录，可通过阅读该目录下的 **README** 直接进行前端部署。

## 基于开发模式启动

- 按上一节完成一套 **TCA Web** 部署

- 根据要调整的内容，启动对应的微前端（login、tca-layout、tca-analysis），具体可进入不同 `package` 参考阅读其目录下的 `README` 进行开发。

**其他**：

- **根目录下启动单个项目**

  ```bash
  # framework
  yarn dev --scope framework
  # login
  PUBLIC_PATH=http://127.0.0.1:5055/ yarn dev --scope login
  # tca-layout
  PUBLIC_PATH=http://127.0.0.1:5056/ yarn dev --scope tca-layout
  # tca-analysis
  PUBLIC_PATH=http://127.0.0.1:5057/ yarn dev --scope tca-analysis
  # tca-analysis
  PUBLIC_PATH=http://127.0.0.1:5058/ yarn dev --scope tca-manage
  # tca-document
  yarn dev --scope tca-document
  # 或进入对应项目内，查阅对应README
  ```

## 本地开发后构建部署

- 如对项目进行变更，本地开发结束后，需要部署最新资源可通过执行 `sh build-source.sh` 将构建后资源更新到**tca-deploy-source** 目录内，再参考该目录下的 **README** 直接进行前端更新/重新部署操作。

- 可通过阅读 `build-source.sh` 内容，以及 **tca-deploy-source** 目录下的 **README**，用户可根据需要自行进行前端部署。
