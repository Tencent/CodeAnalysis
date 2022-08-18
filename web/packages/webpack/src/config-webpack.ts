import path from 'path';
import sass from 'sass';
import webpack, { Configuration } from 'webpack';
import { merge } from 'webpack-merge';
import { CleanWebpackPlugin } from 'clean-webpack-plugin';
import HtmlWebpackPlugin from 'html-webpack-plugin';
import CopyWebpackPlugin from 'copy-webpack-plugin';
import MiniCssExtractPlugin from 'mini-css-extract-plugin';
/** 分析loader、plugin构建速度 */
import SpeedMeasurePlugin from 'speed-measure-webpack-plugin';
/** 文件体积监控插件 */
import { BundleAnalyzerPlugin } from 'webpack-bundle-analyzer';
/** tsconfig-paths 插件 */
import TsconfigPathsPlugin from 'tsconfig-paths-webpack-plugin';
/** 自定义插件，用于生成资源文件地址 */
import ConfigWebpackPlugin from './config-webpack-plugin';
import eslintWebpackPlugin from './config-eslint-webpack-plugin';
import CosWebpackPlugin from './config-cos-webpack-plugin';

/** 默认的环境变量配置 */
import 'webpack-dev-server';

import defaultEnvConfig, { EnvConfig, Envs } from './env';
import { isTrue, modTsConfigPaths } from './util';
import { StrBoolean } from './type';

const smp = new SpeedMeasurePlugin();

/** 页面资源压缩配置 */
const htmlMinify = {
  html5: true, // 根据HTML5规范解析输入
  collapseWhitespace: true, // 折叠空白区域
  preserveLineBreaks: false,
  minifyCSS: true, // 压缩文内css
  minifyJS: true, // 压缩文内js
  removeComments: true, // 移除注释
};


/** 当前工作目录路径 */
const BASE_PATH = process.cwd();

/** 当前工作目录下当前package.json中的name */
const NAME = process.env.npm_package_name;

const {
  ENABLE_MANAGE,
  NODE_ENV,
  HOST, PORT,
  PUBLIC_PATH,
  PLATFORM_ENV,
  BUNDLE_ANALYZER,
  ENABLE_EXTERNALS,
  WEBPACK_COS_ENABLE,
} = process.env;
/** 根据NODE_ENV判断是否为开发模式 */
const IS_DEV = NODE_ENV === 'development';

export interface Options {
  /** 入口文件路径，默认 src/index */
  entryFilePath?: string,
  /** 出口目录路径，默认 dist */
  outputPath?: string,
  /** public路径，默认 public */
  publicDir?: string,
  /** 环境变量配置 */
  envConfig?: EnvConfig,
  /** ConfigWebpackPlugin 配置，默认启用 */
  configWebpackOptions?: {
    enable?: StrBoolean
    match?: string | RegExp
  },
}

/**
 * 初始化配置webpack
 * @param options 参数
 * @returns webpack 配置, context
 */
export const webpackConfig = (options?: Options) => {
  /** 默认配置 */
  const {
    entryFilePath = 'src/index',
    outputPath = 'dist',
    publicDir = 'public',
    configWebpackOptions,
    envConfig,
  } = options || {};
  const outDir = path.resolve(BASE_PATH, isTrue(ENABLE_MANAGE) ? `${outputPath}-admin` : outputPath);
  const templatePath = path.resolve(BASE_PATH, publicDir, 'index.html');
  const { envs, runtimeEnvs } = envConfig ? merge(defaultEnvConfig, envConfig) : defaultEnvConfig;
  if (!NAME) {
    throw new Error('webpack 未获取到 process.env.npm_package_name，请确认package.json中是否存在name字段');
  }
  const tsConfigFile = path.resolve(BASE_PATH, 'tsconfig.json');
  modTsConfigPaths(tsConfigFile, PLATFORM_ENV);
  let config: Configuration = {
    entry: { [NAME]: path.resolve(BASE_PATH, entryFilePath) },
    output: {
      path: outDir,
      publicPath: PUBLIC_PATH || '/',
      filename: `[name]${IS_DEV ? '' : '-[chunkhash:8]'}.js`,
      chunkFilename: `[name]${IS_DEV ? '' : '-[chunkhash:8]'}.js`,
    },
    resolve: {
      extensions: ['.tsx', '.jsx', '.ts', '.js'],
      // Webpack 5 不再自动填充 Node.js 核心模块, 必须从 npm 安装兼容模块并自己包含它们
      fallback: {
        path: require.resolve('path-browserify'),
      },
      alias: {
        // '@src': path.resolve(BASE_PATH, 'src'),
        // '@plat': path.resolve(BASE_PATH, `src/plat/${PLATFORM_ENV}`),
        'react-dom': '@hot-loader/react-dom',
      },
      modules: ['node_modules'],
      plugins: [new TsconfigPathsPlugin({
        // 读取 tsconfig paths 定义别名
        configFile: tsConfigFile,
      })],
    },
    module: {
      rules: [
        {
          // https://github.com/vfile/vfile/issues/38#issuecomment-683198538
          // 用于解决react-markdown process issue https://github.com/remarkjs/react-markdown/issues/339
          test: /node_modules\/vfile\/core\.js/,
          use: [{
            loader: 'imports-loader',
            options: {
              type: 'commonjs',
              imports: ['single process/browser process'],
            },
          }],
        },
        {
          test: /\.[jt]sx?$/i,
          exclude: /node_modules/,
          loader: 'babel-loader',
          options: {
            presets: [
              '@babel/env',
              '@babel/preset-react',
              '@babel/typescript',
            ],
            plugins: [
              '@babel/proposal-class-properties',
              '@babel/proposal-object-rest-spread',
              '@babel/plugin-transform-runtime',
              'react-hot-loader/babel',
            ],
            // rootMode: 'upward',
          },
        },
        {
          test: /\.(ico|png|svg|jpe?g|gif)$/i,
          // asset 根据资源限制大小将其进行asset/resource 或 asset/inline 处理
          type: 'asset',
          generator: {
            filename: 'images/[hash][ext][query]', // 局部指定输出位置
          },
          parser: {
            dataUrlCondition: {
              maxSize: 10 * 1024, // 限制于10kb
            },
          },
        },
        {
          test: /\.(woff(2)?|eot|ttf|otf)$/i,
          type: 'asset/resource',
          generator: {
            filename: 'fonts/[hash][ext][query]',
          },
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
                implementation: sass,
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
        name: (module: any, chunks: Array<any>, cacheGroupKey: string) => {
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
      new CleanWebpackPlugin(),
      new webpack.DefinePlugin({
        'process.env': Object.keys(envs).reduce((e: Envs, key) => {
          e[key] = JSON.stringify(envs[key]);
          return e;
        }, {}),
        PLATFORM_ENV: JSON.stringify(PLATFORM_ENV),
        ENABLE_MANAGE: JSON.stringify(isTrue(ENABLE_MANAGE)),
      }),
      new CopyWebpackPlugin({
        patterns: [{
          from: path.resolve(BASE_PATH, publicDir),
          globOptions: {
            ignore: [
              '**/index.html',
            ],
          },
        }],
      }),
      new HtmlWebpackPlugin({
        inject: true,
        template: path.resolve(BASE_PATH, templatePath),
        filename: 'index.html',
        envs,
        minify: htmlMinify,
      }),
      // 该配置生成一个 index.runtime.html 模板用于提供 index.html runtime 的能力
      new HtmlWebpackPlugin({
        inject: true,
        template: path.resolve(BASE_PATH, templatePath),
        filename: 'index.runtime.html',
        minify: htmlMinify,
        envs: merge(envs, runtimeEnvs),
      }),
      new ConfigWebpackPlugin(configWebpackOptions),
      // 忽略第三方包指定目录，让这些指定目录不要被打包进去，对moment操作参考：https://blog.csdn.net/qq_17175013/article/details/86845624
      new webpack.IgnorePlugin({
        resourceRegExp: /^\.\/locale$/,
        contextRegExp: /moment$/,
      }),
    ],
    performance: {
      hints: false,
    },
  };
  if (IS_DEV) {
    const host = HOST || '127.0.0.1';
    const port = PORT || 8080;
    // const webSocketURL = `ws://${host}:${port}/ws`;
    config = merge(config, {
      devtool: 'eval-cheap-module-source-map',
      target: 'web',
      cache: {
        type: 'filesystem',
        // PLATFORM_ENV变化时缓存切换
        version: PLATFORM_ENV,
      },
      devServer: {
        static: outDir,
        hot: true,
        liveReload: false,
        allowedHosts: 'all',
        host,
        port,
        // client: {
        //   webSocketURL,
        // },
        historyApiFallback: true,
        compress: true,
        devMiddleware: {
          writeToDisk: true,
        },
        headers: {
          'Access-Control-Allow-Origin': '*',
        },
      },
      plugins: [
        eslintWebpackPlugin,
      ],
    });
  } else {
    config = merge(config, {
      /** 外部扩展配置，如果开启了ENABLE_EXTERNALS，则构建时会忽略这些项，仅用于生产环境 */
      externals: isTrue(ENABLE_EXTERNALS) ? {
        react: 'React',
        'react-dom': 'ReactDOM',
        'react-redux': 'ReactRedux',
        classnames: 'Classnames',
        'coding-oa-uikit': 'CodingOAUikit',
        lodash: 'Lodash',
      } : undefined,
    });
    // 开启BUNDLE_ANALYZER时才执行
    if (isTrue(BUNDLE_ANALYZER)) {
      config.plugins?.push(new BundleAnalyzerPlugin());
    }
    if (isTrue(WEBPACK_COS_ENABLE)) {
      config.plugins?.push(new CosWebpackPlugin());
    }
  }
  // 避免MiniCssExtractPlugin与SpeedMeasurePlugin异常
  // https://github.com/stephencookdev/speed-measure-webpack-plugin/issues/167
  config = smp.wrap(config);
  config.plugins?.push(new MiniCssExtractPlugin({
    filename: `[name]${IS_DEV ? '' : '-[contenthash:8]'}.css`,
    chunkFilename: `[name]${IS_DEV ? '' : '-[contenthash:8]'}.css`,
    // 对于通过使用 scoping 或命名约定来解决 css order 的项目，可以通过将插件的 ignoreOrder 选项设置为 true 来禁用 css order 警告。
    ignoreOrder: true,
  }));
  return {
    config,
    context: {
      baseParh: BASE_PATH,
      outDir,
    },
  };
};
