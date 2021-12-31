const path = require('path');
const webpack = require('webpack');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const EslintWebpackPlugin = require('eslint-webpack-plugin');
// 日志优化
const FriendlyErrorsWebpackPlugin = require('friendly-errors-webpack-plugin');
const WebpackBar = require('webpackbar');

// 根据NODE_ENV分别获取不同的config
const isDev = process.env.NODE_ENV === 'development';
// 获取项目环境变量
const { envs, runtimeEnvs } = require('./envs');
// 打包目录路径
const BASE_DIR = path.resolve(__dirname, '..');
const buildPath = path.resolve(BASE_DIR, 'dist');
// index.html路径
const indexPath = path.resolve(BASE_DIR, 'public', 'index.html');
// static 路径
const staticPath = path.resolve(BASE_DIR, 'public', 'static');

const htmlMinify = {
  html5: true, // 根据HTML5规范解析输入
  collapseWhitespace: true, // 折叠空白区域
  preserveLineBreaks: false,
  minifyCSS: true, // 压缩文内css
  minifyJS: true, // 压缩文内js
  removeComments: true, // 移除注释
};

module.exports = {
  entry: {
    framework: path.resolve(BASE_DIR, 'src/index.ts'),
  },
  output: {
    filename: '[name].bundle.js',
    path: buildPath,
    publicPath: process.env.PUBLIC_PATH || '/',
  },
  resolve: {
    // 尝试按顺序解析这些后缀名
    extensions: ['.ts', '.tsx', '.js', '.jsx', '.svg'],
    alias: {
      '@src': path.resolve(BASE_DIR, 'src'),
      'react-dom': '@hot-loader/react-dom',
    },
    modules: [BASE_DIR, 'node_modules'],
  },
  module: {
    rules: [
      {
        test: /\.[jt]sx?$/i,
        exclude: /node_modules/,
        loader: 'babel-loader',
        options: {
          rootMode: 'upward',
        },
      },
      // Images
      {
        test: /\.(?:ico|gif|png|jpg|jpeg)$/i,
        type: 'asset/resource',
      },
      // Fonts and SVGs
      {
        test: /\.(woff(2)?|eot|ttf|otf|svg|)$/i,
        type: 'asset/inline',
      },
      {
        test: /\.css$/i,
        use: [
          isDev ? 'style-loader' : MiniCssExtractPlugin.loader,
          'css-loader',
        ],
      },
      {
        test: /\.s[ac]ss$/i,
        exclude: [path.resolve(BASE_DIR, 'public')],
        use: [
          // 将 JS 字符串生成为 style 节点
          isDev ? 'style-loader' : MiniCssExtractPlugin.loader,
          // 将 CSS 转化成 CommonJS 模块
          {
            loader: 'css-loader',
            options: {
              modules: {
                localIdentName: '[local]-[hash:base64:10]',
                exportLocalsConvention: 'camelCase',
              },
              importLoaders: 2,
            },
          },
          // 将 Sass 编译成 CSS
          {
            loader: 'sass-loader',
            options: {
              // Prefer `dart-sass`
              implementation: require('sass'),
            },
          },
        ],
      },
    ],
  },
  plugins: [
    // 打包前移除/清理 打包目录
    new FriendlyErrorsWebpackPlugin(),
    new CleanWebpackPlugin(),
    new webpack.DefinePlugin({
      'process.env': Object.keys(envs).reduce((e, key) => {
        e[key] = JSON.stringify(envs[key]);
        return e;
      }, {}),
    }),
    new EslintWebpackPlugin({
      fix: true,
      extensions: ['js', 'jsx', 'tsx', 'ts'],
    }),
    new HtmlWebpackPlugin({
      inject: true,
      template: indexPath,
      envs,
      minify: htmlMinify,
    }),
    // 该配置生成一个 index.runtime.html 模板用于提供 index.html runtime 的能力
    new HtmlWebpackPlugin({
      inject: true,
      template: indexPath,
      filename: 'index.runtime.html',
      minify: htmlMinify,
      envs: {
        ...envs,
        ...runtimeEnvs,
      },
    }),
    new CopyWebpackPlugin({
      patterns: [{
        from: staticPath,
        to: path.resolve(buildPath, 'static'),
      }, {
        from: path.resolve(BASE_DIR, 'public', '404.html'),
        to: buildPath,
      }, {
        from: path.resolve(BASE_DIR, 'public', 'unsupported-browser.html'),
        to: buildPath,
      }],
    }),
    // // 忽略第三方包指定目录，让这些指定目录不要被打包进去，对moment操作参考：https://blog.csdn.net/qq_17175013/article/details/86845624
    new webpack.IgnorePlugin({
      resourceRegExp: /^\.\/locale$/,
      contextRegExp: /moment$/,
    }),
    new WebpackBar(),
  ],
};
