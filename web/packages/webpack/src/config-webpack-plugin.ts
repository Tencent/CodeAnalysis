/**
 * 微前端生成配置json Webpack 插件
 */
import webpack, { Compiler, Stats, Compilation } from 'webpack';
import chalk from 'chalk';
import { isTrue } from './util';
import { StrBoolean } from './type';

const { green, yellow } = chalk.bold;

/** 插件名称 */
const PLUGIN_NAME = 'ConfigWebpackPlugin';
/** 当前工作目录下当前package.json中的name */
const DEFAULT_PROJECT_NAME = process.env.npm_package_name;
/** 当前工作目录下当前package.json中的description */
const DEFAULT_PROJECT_DESC = process.env.npm_package_description;

const {
  NODE_ENV,
  CONFIG_ENABLED,
  GIT_REVISION,
  PRODUCT_ROUTE_MATCH,
  PUBLIC_PATH,
  WEBPACK_CONFIG_ENABLE,
  WEBPACK_CONFIG_PROJECT_NAME,
  WEBPACK_CONFIG_PROJECT_DESC,
  WEBPACK_CONFIG_MATCH,
} = process.env;

/** 是否dev */
const IS_DEV = NODE_ENV === 'development';

interface ConfigJson {
  /** 配置名称 */
  name: string;
  /** 资源描述 */
  description: string;
  /** git version版本号 */
  commitId: string;
  /** 微前端资源匹配规则 */
  match: string | RegExp;
  /** js 资源 */
  js: string[];
  /** css 资源 */
  css: string[];
  /** 前缀 */
  prefix: string[];
}

interface ConfigWebpackPluginProps {
  /** 是否启用，默认启用 */
  enable?: StrBoolean;
  /** 微前端产品名称 */
  productName?: string;
  /** 微前端产品描述 */
  description?: string;
  /** commit 版本号 */
  commitId?: string;
  /** 匹配规则 */
  match?: string | RegExp;
  /** 资源 */
  assetKeys?: string[];
  /** 是否开启 plugin 日志，默认关闭 */
  enableLog?: StrBoolean;
}

interface Config {
  /** 是否启用，默认启用 */
  enable: boolean;
  /** 微前端产品名称 */
  productName: string;
  /** 微前端产品描述 */
  description: string;
  /** 微前端配置前缀 */
  prefix: string[];
  /** PUBLIC_PATH */
  publicPath: string;
  /** commit 版本号 */
  commitId: string;
  /** 匹配规则 */
  match: string | RegExp;
  /** 资源 */
  assetKeys: Array<string>
  /** 是否开启 plugin 日志，默认关闭 */
  enableLog: boolean;
}

class ConfigWebpackPlugin {
  config: Config;
  constructor(options?: ConfigWebpackPluginProps) {
    const { enable, productName, description, commitId, match, assetKeys, enableLog } = options || {};
    const projectName = productName || WEBPACK_CONFIG_PROJECT_NAME || DEFAULT_PROJECT_NAME || '';
    const publicPath = PUBLIC_PATH || '/';
    const prefix = [publicPath.endsWith('/') ? publicPath : `${publicPath}/`];
    this.config = {
      enable: isTrue(enable || CONFIG_ENABLED || WEBPACK_CONFIG_ENABLE || true),
      productName: projectName,
      description: description || WEBPACK_CONFIG_PROJECT_DESC || DEFAULT_PROJECT_DESC || '',
      prefix,
      publicPath,
      commitId: commitId || GIT_REVISION || 'dirty',
      assetKeys: assetKeys || [`runtime~${projectName}`, `vendors~${projectName}`, `${projectName}`],
      match: match || PRODUCT_ROUTE_MATCH || WEBPACK_CONFIG_MATCH || '',
      enableLog: isTrue(enableLog || false),
    };

    this.debug('配置项: ', this.config);

    if (!this.config.enable) {
      log('插件未启用');
      return;
    }

    if (!this.config.productName) {
      throw new Error(`[${PLUGIN_NAME}]: 需要配置 productName`);
    }

    if (!this.config.assetKeys.length) {
      throw new Error(`[${PLUGIN_NAME}]: 需要配置 assetKeys`);
    }

    if (!this.config.match) {
      throw new Error(`[${PLUGIN_NAME}]: 需要配置 match`);
    }
  }

  apply(compiler: Compiler) {
    if (!this.config.enable) {
      return;
    }
    // 将config配置资源添加到asset中
    compiler.hooks.compilation.tap(PLUGIN_NAME, (compilation) => {
      compilation.hooks.processAssets.tap({
        name: PLUGIN_NAME,
        stage: Compilation.PROCESS_ASSETS_STAGE_ADDITIONS,
      }, (assets) => {
        const keys = Object.keys(assets);
        if (keys.length) {
          const config  = this.generateConfig(keys);
          const configTxt = JSON.stringify(config);
          compilation.emitAsset(`${this.config.productName}.json`,  new webpack.sources.RawSource(configTxt));
          log(green(`[config] ${configTxt}`));
        }
      });
    });

    // 在 compilation 完成时执行，dev环境将配置地址打印出来
    compiler.hooks.done.tap(PLUGIN_NAME, ({ compilation }: Stats) => {
      // 用于dev，生成api.json url
      if (IS_DEV) {
        const { devServer } = compilation.options;
        const https = devServer?.https || false;
        const host = devServer?.host || 'localhost';
        const port = devServer?.port || '8080';
        const reg = new RegExp(/https?:\/\//);
        const { publicPath, productName } = this.config;
        const prefix = reg.test(publicPath) ? publicPath : `http${https ? 's' : ''}://${host}:${port}${publicPath}`;
        const api = `${prefix}${productName}.json`;
        const timer = setTimeout(() => {
          log(`${yellow('[dev环境]')}: API = ${green(api)}`);
          clearTimeout(timer);
        }, 20);
      }
    });
  }

  /** 生成cofing.json资源文件 */
  private generateConfig(assets: string[]) {
    const { productName, publicPath, assetKeys, ...other } = this.config;
    const config: ConfigJson = {
      name: productName,
      ...other,
      js: [],
      css: [],
    };
    assets.forEach((asset) => {
      assetKeys.forEach((assetKey) => {
        if (asset.startsWith(assetKey)) {
          const file = `${publicPath}${asset}`;
          if (asset.endsWith('.js')) {
            config.js.push(file);
          } else if (asset.endsWith('.css')) {
            config.css.push(file);
          }
        }
      });
    });
    return config;
  }

  /** debug 日志 */
  private debug = (...rest: any[]) => {
    this.config.enableLog && log(...rest);
  };
}

export default ConfigWebpackPlugin;

/** 日志 */
const log = (...rest: any[]) => {
  console.log(chalk.bgMagenta(`[${PLUGIN_NAME}]:`), ...rest);
};
