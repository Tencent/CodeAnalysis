const AssetsWebpackPlugin = require('assets-webpack-plugin');
const merge = require('lodash/merge');
const chalk = require('chalk');

const PLUGIN_NAME = 'ConfigWebpackPlugin';
const PLUGIN_PREFIX = `[${PLUGIN_NAME}] `;

function isTrue(value) {
  return value === true || value === 'true';
}

class ConfigWebpackPlugin {
  constructor(options) {
    if (!options) {
      options = {};
    }
    const productName = this.getProductName(options);
    const description = this.getDescription(options);
    this.options = merge(
      {
        enable: process.env.CONFIG_ENABLED || true, // 默认启用
        productName,
        description,
        commitId: process.env.GIT_REVISION || '',
        match: process.env.PRODUCT_ROUTE_MATCH,
        prefix: process.env.PUBLIC_PATH || '/',
      },
      options,
    );
    this.isDev = (!!options.isDev) || process.env.NODE_ENV !== 'production';

    // AssetsWebpackPlugin所需
    this.path = options.path;
    this.filename = `${productName}.json`;
    this.assetKeys = options.assetKeys || [];

    // 未启用
    if (!isTrue(this.options.enable)) {
      console.info(chalk.yellow(PLUGIN_PREFIX)
        + chalk.green('plugin is disabled, please use process.env.CONFIG_ENABLED enable it'));
      return;
    }
    this.optionCheck(this.options);
  }

  // 对启用该插件进行必要参数校验
  optionCheck(options) {
    if (!options.productName) {
      throw new Error(`${PLUGIN_PREFIX} 需要设置 productName。const productName = options?.productName || options?.pkgInfo?.name || process.env.PRODUCT_NAME;`);
    }

    if (!options.path) {
      throw new Error(`${PLUGIN_PREFIX} 需要设置 path。用于AssetsWebpackPlugin打包资源到path下`);
    }

    if (!options.assetKeys) {
      throw new Error(`${PLUGIN_PREFIX} 需要设置 assetKeys。用于资源获取。`);
    }

    if (!options.match) {
      throw new Error(`${PLUGIN_PREFIX} 需要设置 match。用于资源路由match`);
    }
  }

  // 获取应用名称
  getProductName(options) {
    if (options) {
      if (options.productName) {
        return options.productName;
      }
      if (options.pkgInfo?.name) {
        return options.pkgInfo.name;
      }
    }
    return process.env.PRODUCT_NAME;
  }

  // 获取应用描述
  getDescription(options) {
    if (options?.pkgInfo?.description) {
      return options.pkgInfo.description;
    }
    return process.env.PRODUCT_DESC || '';
  }

  apply(compiler) {
    const plugins = [
      new AssetsWebpackPlugin({
        path: this.path,
        filename: this.filename,
        processOutput: this.processOutput.bind(this),
      }),
    ];

    plugins.forEach((plugin) => {
      plugin.apply(compiler);
    });

    // 在 compilation 完成时执行，dev环境将配置地址打印出来
    compiler.hooks.done.tap(PLUGIN_NAME, (stats) => {
      // 用于dev，生成api.json url
      if (this.isDev) {
        const { https = false, host = 'localhost', port = 8080 } = stats.compilation.options.devServer;
        const reg = new RegExp(/https?:\/\//);
        const publicPath = this.options.prefix;
        const prefix = reg.test(publicPath) ? publicPath : `http${https ? 's' : ''}://${host}:${port}${publicPath}`;
        const api = `${prefix}${this.filename}`;
        setTimeout(() => {
          console.info(`${chalk.yellow('[dev环境]')}: ${chalk.green(`API = ${chalk.yellow(api)} , `)}`);
        }, 20);
      }
    });
  }

  processOutput(assets) {
    // 插件未启用
    if (!isTrue(this.options.enable)) {
      console.info(chalk.yellow(PLUGIN_PREFIX) + chalk.green('插件未启用，跳过...'));
      return '';
    }

    // 获取资源内的js和css
    const js = this.assetKeys.map(k => assets[k]?.js).filter(v => !!v);
    const css = this.assetKeys.map(k => assets[k]?.css).filter(v => !!v);

    // 生成config
    const config = {
      name: this.options.productName,
      description: this.options.description,
      commitId: this.options.commitId,
      match: this.options.match,
      js,
      css,
      prefix: [this.options.prefix],
    };

    console.log(chalk.yellow(PLUGIN_PREFIX) + chalk.yellow('[config]') + chalk.green(JSON.stringify(config)));
    return this.options.processOutput ? this.options.processOutput(assets, config) : JSON.stringify(config);
  }
}

module.exports = ConfigWebpackPlugin;
