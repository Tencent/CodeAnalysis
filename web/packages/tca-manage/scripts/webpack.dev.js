const path = require('path');
const { merge } = require('webpack-merge');
const common = require('./webpack.common.js');
const host = process.env.HOST || '127.0.0.1';
const port = process.env.PORT || 5058;
const webSocketURL = `ws://${host}:${port}/ws`;
module.exports = merge(common, {
  devServer: {
    static: path.join(__dirname, '../dist'),
    hot: true,
    liveReload: false,
    allowedHosts: 'all',
    host,
    port,
    client: {
      webSocketURL,
    },
    historyApiFallback: true,
    compress: true,
    devMiddleware: {
      writeToDisk: true,
    },
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
  },
});
