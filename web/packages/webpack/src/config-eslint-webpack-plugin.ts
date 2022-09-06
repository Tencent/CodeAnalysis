import EslintWebpackPlugin from 'eslint-webpack-plugin';

const eslintWebpackPlugin = new EslintWebpackPlugin({
  fix: true,
  extensions: ['js', 'jsx', 'tsx', 'ts'],
  /** 可以选择将其设置为与 .eslintrc.* 模式相同的配置对象。这将作为默认配置，
   * 并与 .eslintrc.* 中的任何配置进行合并，其中 .eslintrc.* 文件的配置优先。 */
  baseConfig: {
    env: {
      browser: true,
      es2021: true,
      node: true,
    },
    parser: 'esprima',  // ESLint 默认使用Espree作为其解析器
    parserOptions: {
      ecmaVersion: 2021,
      sourceType: 'module',
      ecmaFeatures: {
        jsx: true,  // 允许解析JSX
      },
    },
    plugins: ['react'],
    extends: [
      'eslint:recommended',
      'plugin:react/recommended',
    ],
    settings: {
      react: {
        version: 'detect', // 告诉eslint-plugin-react自动检测要使用的React版本
      },
    },
    overrides: [
      {
        files: ['*.ts', '*.tsx'],
        parser: '@typescript-eslint/parser',
        plugins: ['@typescript-eslint'],
        extends: [
          'plugin:@typescript-eslint/recommended',
        ],
      },
    ],
  },
});

export default eslintWebpackPlugin;
