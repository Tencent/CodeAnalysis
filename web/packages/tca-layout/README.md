# `tca-layout`

腾讯云代码分析导航微前端。

- 导航菜单

- 团队管理

- 个人中心

## 本地启动脚本

```bash
PUBLIC_PATH=http://127.0.0.1:5056/ yarn run dev
```

## 开发模式启动方式

使用如下命令启动：

  ```bash
  xxx=xxx yarn run dev

  # 如
  PUBLIC_PATH=http://127.0.0.1:5056/ yarn run dev
  ```

启动后可通过以下进行开发：

- **基座插件模式**
  
  使用浏览器插件进行脚本配置，如 `Tampermonkey` 插件。

  ```js
  (function() {
      'use strict';

      const HOOK_NAME = 'microDevApiList'
      if (!window.hasOwnProperty.call(window, HOOK_NAME)) {
          const apiList = new Array();

          Object.defineProperty(window, HOOK_NAME, {
              enumerable: false,
              writable: false,
              value: apiList,
          });
      }

      window.microDevApiList.push({
          'name': 'tca-layout',
          'url': 'http://localhost:5056/tca-layout.json'
      })
  })();
  ```

- **基座开发模式**

  在基座使用快捷键开启 `Micro Frontend Dev` 配置面板，配置子微前端名称和子微前端dev地址

  ```txt
  Windows快捷键：ctrl+alt+shift+d

  Mac 快捷键：ctrl+command+shift+d
  ```

- **独立启动开发**

  直接浏览器访问当前地址+端口的页面，如 `http://localhost:5056`

## 环境变量说明

|                       环境变量 | 说明                                   |
| -----------------------------: | :------------------------------------- |
|                          TITLE | 网页标题                               |
|                    DESCRIPTION | 网页说明                               |
|                       KEYWORDS | 网页关键词                             |
|                        FAVICON | 网页图标                               |
|                   GIT_REVISION | git 版本号                             |
|             MICRO_FRONTEND_API | 微前端资源配置地址                     |
|         MICRO_VERSION_INTERVAL | 版本更新获取间隔时间，默认 5 分钟      |
|          MICRO_VERSION_ENABLED | 开启版本更新功能                       |
|     MICRO_FRONTEND_SETTING_API | 微前端动态setting资源配置地址     |
|                    PUBLIC_PATH | 资源路径前缀     |
|                   PLATFORM_ENV | 平台类型                      |
|                  ENABLE_MANAGE | 开启后台版                      |
|               ENABLE_EXTERNALS | 开启排除额外依赖（用于具有全局依赖时）           |
|                 CONFIG_ENABLED | 开启config-webpack-plugin              |
|                   PRODUCT_NAME | 产品名称                      |
|                   PRODUCT_DESC | 产品描述                      |
|            PRODUCT_ROUTE_MATCH | 产品路由匹配                      |

备注：上述环境变量很多已做默认值处理，启动或构建时需根据需要进行配置
