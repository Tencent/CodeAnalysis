// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

const { merge } = require('webpack-merge');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
// 文件体积监控
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');


const common = require('./webpack.common.js');

module.exports = merge(common, {
  output: {
    filename: '[name]-[chunkhash:8].js',
    chunkFilename: '[name]-[chunkhash:8].js',
    publicPath: process.env.PUBLIC_PATH || '/',
  },
  devtool: false,
  optimization: {
    runtimeChunk: true,
    splitChunks: {
      chunks: 'all',
      name: (module, chunks, cacheGroupKey) => {
        const allChunksNames = chunks.map(item => item.name).join('~');
        return `${cacheGroupKey}~${allChunksNames}`;
      },
      cacheGroups: {
        vendors: {
          test: /[\\/]node_modules[\\/]/,
          chunks: 'all',
          enforce: true,
        },
      },
    },
  },
  performance: {
    hints: false,
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: '[name]-[chunkhash:8].css',
      chunkFilename: '[name]-[chunkhash:8].css',
      ignoreOrder: false,
    }),
    new BundleAnalyzerPlugin({
      analyzerMode: 'disabled', // 不启动展示打包报告的http服务器
      generateStatsFile: true, // 不打开网站，但是在dist生成stats.json文件
    }),
  ],
});
