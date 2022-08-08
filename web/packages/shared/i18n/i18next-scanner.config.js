const fs = require('fs');
const chalk = require('chalk');
const path = require('path');
const typescript = require('typescript');
const { merge } = require('lodash');

/**
 * i18next-scanner配置
 * @param {*} options 默认{}, 可传递i18next-scanner参数调整默认配置
 * @returns i18next-scanner配置
 */
const i18nScannerConfigFunc = (options = {}) => merge({
  input: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.spec.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!**/node_modules/**',
  ],
  output: './',
  options: {
    debug: true,
    func: {
      list: ['i18next.t', 'i18n.t', 't'],
      extensions: [],
    },
    trans: {
      component: 'Trans',
      i18nKey: 'i18nKey',
      extensions: [],
      fallbackKey(ns, value) {
        return value;
      },
      acorn: {
        ecmaVersion: 2020,
        sourceType: 'module', // defaults to 'module'
        // Check out https://github.com/acornjs/acorn/tree/master/acorn#interface for additional options
      },
    },
    lngs: ['zh-CN', 'en-US'],
    resource: {
      loadPath: 'public/locales/{{lng}}/{{ns}}.json',
      savePath: 'public/locales/{{lng}}/{{ns}}.json',
      jsonIndent: 2,
      lineEnding: '\n',
    },
    defaultValue: '',
    nsSeparator: false, // namespace separator
    keySeparator: false, // key separator
    removeUnusedKeys: true,
  },
  transform: function customTransform(file, enc, done) {
    'use strict';
    const { parser } = this;
    const content = fs.readFileSync(file.path, enc);
    const { outputText } = typescript.transpileModule(content, {
      compilerOptions: { target: typescript.ScriptTarget.ES2021 },
      fileName: path.basename(file.path),
    });

    // Parse Translation Function
    let count = 0;
    parser.parseFuncFromString(outputText, (key) => {
      parser.set(key, key);
      count += 1;
    });
    if (count) {
      console.log(`${chalk.blue('i18next-scanner:')} ${file.path}\n`);
    }

    // Parse Trans component
    parser.parseTransFromString(outputText);

    done();
  },
}, options);

const i18nScannerConfig = i18nScannerConfigFunc();

module.exports = {
  i18nScannerConfigFunc,
  i18nScannerConfig,
};
