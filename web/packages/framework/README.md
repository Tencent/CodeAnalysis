# `framework`

微前端基座。

- 基于 [single-spa](https://single-spa.js.org/docs/getting-started-overview/) 封装，通过接口调用读取微前端配置。

- 提供微前端应用生命周期管理。

- 使用 `Redux` 作为全局状态管理，以确保共享数据机制。

- 功能：支持版本更新；支持微前端开发模式、插件模式；暴露全局依赖。

## 开发模式启动方式

- 使用如下命令启动

  ```node
  MICRO_FRONTEND_API={微前端配置资源地址} yarn run dev

  // 如：
  MICRO_FRONTEND_API=http://127.0.0.1:5058/api.json yarn run dev
  ```

- 如果本地启动时，**微前端配置资源地址**，即 `yarn run dev`

  可通过**devServer**代理获取微前端资源地址

## 环境变量说明

### 构建时可配置环境变量

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

### 运行时可配置环境变量

即在容器部署中，通过环境变量，执行脚本，动态改变 `index.runtime.html` 的 `meta`，并覆盖`index.html`

|           环境变量 | 说明               |
| -----------------: | :----------------- |
|              TITLE | 网页标题           |
|        DESCRIPTION | 网页说明           |
|           KEYWORDS | 网页关键词         |
|            FAVICON | 网页图标           |
| MICRO_FRONTEND_API | 微前端资源配置地址 |

### setting 接口配置项

|               环境变量 | 说明                                          |
| ---------------------: | :-------------------------------------------- |

## 公共依赖处理

微前端基座已经将部分公共依赖使用 `expose-loader` 暴露为全局依赖。子前端项目只需要在 webpack 配置中加入如下配置，将这部分公共依赖排除打包。

```js
module.exports = {
  // ...
  externals: {
    react: 'React',
    'react-dom': 'ReactDOM',
    'react-redux': 'ReactRedux',
    classnames: 'Classnames',
    'coding-oa-uikit': 'CodingOAUikit',
    lodash: 'Lodash',
  },
  // ...
};
```

公共依赖保持版本跟框架层一致，具体可以查看 `package.json` 文件
