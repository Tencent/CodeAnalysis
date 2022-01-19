// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

const { merge } = require('webpack-merge');
// 文件体积监控
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');

const common = require('./webpack.common.js');

const externals = process.env.ENABLE_EXTERNALS === 'TRUE' ? {
  react: 'React',
  'react-dom': 'ReactDOM',
  'react-redux': 'ReactRedux',
  classnames: 'Classnames',
  'coding-oa-uikit': 'CodingOAUikit',
  lodash: 'Lodash',
} : {};

module.exports = merge(common, {
  performance: {
    hints: false,
  },
  plugins: [
    new BundleAnalyzerPlugin({
      analyzerMode: 'disabled', // 不启动展示打包报告的http服务器
      generateStatsFile: true, // 不打开网站，但是在dist生成stats.json文件
    }),
  ],
  externals,
});
