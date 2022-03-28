const path = require('path');
const webpack = require('webpack');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const EslintWebpackPlugin = require('eslint-webpack-plugin');
// 日志优化
const FriendlyErrorsWebpackPlugin = require('friendly-errors-webpack-plugin');
const WebpackBar = require('webpackbar');
const ConfigWebpackPlugin = require('./config-webpack-plugin');

const pkgInfo = require('../package.json');

// 根据NODE_ENV分别获取不同的config
const isDev = process.env.NODE_ENV === 'development';
// 获取项目环境变量
const { envs, runtimeEnvs } = require('./envs');
// 打包目录路径
const BASE_DIR = path.resolve(__dirname, '..');
const buildPath = process.env.ENABLE_MANAGE === 'TRUE' ? path.resolve(BASE_DIR, 'dist-admin') : path.resolve(BASE_DIR, 'dist');
// index.html路径
const indexPath = path.resolve(BASE_DIR, 'public', 'index.html');

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
    [pkgInfo.name]: path.resolve(BASE_DIR, 'src/index.tsx'),
  },
  output: {
    path: buildPath,
    publicPath: process.env.PUBLIC_PATH || '/',
    filename: `[name]${isDev ? '' : '-[chunkhash:8]'}.js`,
    chunkFilename: `[name]${isDev ? '' : '-[chunkhash:8]'}.js`,
  },
  devtool: isDev ? 'inline-source-map' : false,
  target: 'web',
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
          MiniCssExtractPlugin.loader,
          'css-loader',
        ],
      },
      {
        test: /\.s[ac]ss$/i,
        exclude: [path.resolve(BASE_DIR, 'public')],
        use: [
          MiniCssExtractPlugin.loader,
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
  plugins: [
    // 打包前移除/清理 打包目录
    new FriendlyErrorsWebpackPlugin(),
    new CleanWebpackPlugin(),
    new webpack.DefinePlugin({
      'process.env': Object.keys(envs).reduce((e, key) => {
        e[key] = JSON.stringify(envs[key]);
        return e;
      }, {}),
      PLATFORM_ENV: JSON.stringify(process.env.PLATFORM_ENV),
      ENABLE_MANAGE: JSON.stringify(process.env.ENABLE_MANAGE),
    }),
    new EslintWebpackPlugin({
      fix: true,
      extensions: ['js', 'jsx', 'tsx', 'ts'],
    }),
    new MiniCssExtractPlugin({
      filename: `[name]${isDev ? '' : '-[contenthash:8]'}.css`,
      chunkFilename: `[name]${isDev ? '' : '-[contenthash:8]'}.css`,
      ignoreOrder: false,
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
    new ConfigWebpackPlugin({
      pkgInfo,
      isDev,
      path: buildPath,
      match: process.env.PRODUCT_ROUTE_MATCH || '^/manage',
      assetKeys: ['runtime~tca-manage', 'vendors~tca-manage', 'tca-manage'],
    }),
    // 忽略第三方包指定目录，让这些指定目录不要被打包进去，对moment操作参考：https://blog.csdn.net/qq_17175013/article/details/86845624
    new webpack.IgnorePlugin({
      resourceRegExp: /^\.\/locale$/,
      contextRegExp: /moment$/,
    }),
    new WebpackBar(),
  ],
};
