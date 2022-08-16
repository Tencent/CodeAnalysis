# `@tencent/micro-frontend-webpack`

> 微前端 webpack 公共配置

## Usage

### NPM包产物引用

**`webpack.config.js`**

```js
const { webpackConfig } = require('@tencent/micro-frontend-webpack');
const { merge } = require('webpack-merge');

module.exports = merge(webpackConfig, {
  // webpack custom config ...
});
```

### 单仓中直接源码引用

**`webpack.config.ts`**

```ts
import { webpackConfig } from '@tencent/micro-frontend-webpack/src/index';
import { merge } from 'webpack-merge';

export default merge(webpackConfig, {
  // webpack custom config ...
});
```
