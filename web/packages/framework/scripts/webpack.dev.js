const { merge } = require('webpack-merge');
const common = require('./webpack.common.js');
module.exports = merge(common, {
  devtool: 'inline-source-map',
  target: 'web',
  devServer: {
    hot: true,
    allowedHosts: 'all',
    host: process.env.HOST || '0.0.0.0',
    port: process.env.PORT || 4000,
    historyApiFallback: true,
    compress: true,
    devMiddleware: {
      writeToDisk: true,
    },
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
    proxy: {
      // '/static': {
      //   ws: false,
      //   target: 'http://ip',
      //   changeOrigin: true,
      // },
      // '/server': {
      //   ws: false,
      //   target: 'http://ip:8000',
      //   changeOrigin: true,
      //   pathRewrite: {
      //     '^/server': '',
      //   },
      // },
    },
  },
});
