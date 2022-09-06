module.exports = {
  root: true,
  env: {
    browser: true,
    es2020: true,
    node: true,
  },
  parser: 'esprima',
  parserOptions: {
    ecmaVersion: 2021,
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true, // 允许解析JSX
    },
    // tsconfigRootDir: __dirname,
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
  rules: {
    // 禁止对函数参数再赋值 - 关闭
    'no-param-reassign': 'off',
  },
  overrides: [
    {
      files: ['*.ts', '*.tsx'],
      parser: '@typescript-eslint/parser',
      plugins: ['@typescript-eslint'],
      extends: [
        'plugin:@typescript-eslint/recommended',
      ],
      rules: {
        // 禁止 ts any - 关闭
        '@typescript-eslint/no-explicit-any': 'off',
        // 禁止 ts require - 关闭
        '@typescript-eslint/no-require-imports': 'off',
        // 禁止定义了变量却不使用它
        '@typescript-eslint/no-unused-vars': [
          'error',
          {
            args: 'after-used',
            ignoreRestSiblings: true,
            argsIgnorePattern: '^_.+',
            varsIgnorePattern: '^_.+'
          }
        ]
      },
    },
  ],
};
