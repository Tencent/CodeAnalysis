module.exports = {
  root: true,
  env: {
    browser: true,
    es2020: true,
    node: true,
  },
  extends: [
    'eslint:recommended',
  ],
  parserOptions: {
    ecmaVersion: 11,
    sourceType: 'module',
    tsconfigRootDir: __dirname,
  },
  overrides: [
    {
      files: [
        '*.ts',
        '*.tsx',
      ],
      extends: [
        'plugin:react/recommended',
      ],
      parser: '@typescript-eslint/parser',
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
        ecmaVersion: 11,
        sourceType: 'module',
      },
      plugins: [
        'react',
        '@typescript-eslint',
      ],
      rules: {
        '@typescript-eslint/no-require-imports': 'off',
        // 禁止对函数参数再赋值 - 关闭
        'no-param-reassign': 'off',
        '@typescript-eslint/no-unused-vars': ['error', { vars: 'all', args: "after-used", ignoreRestSiblings: true }],
        'no-undef': 'off'
      },
    },
  ],
  rules: {
    // 禁止对函数参数再赋值 - 关闭
    'no-param-reassign': 'off',
  },
  settings: {
    react: {
      pragma: 'React',
      version: 'detect',
    },
  },
};
