import { defineUserConfig } from '@vuepress/cli'
import { defaultTheme } from '@vuepress/theme-default'
import { navbar, sidebar } from './configs'
const { searchPlugin } = require('@vuepress/plugin-search')

const isProd = process.env.NODE_ENV === 'production'


export default defineUserConfig({
  base: process.env.BASE ? `/${process.env.BASE}/` : '/',

  head: [
    [
      'link',
      {
        rel: 'icon',
        type: 'image/png',
        href: `/images/favicon.png`,
      },
    ],
    ['meta', { name: 'msapplication-TileColor', content: '#3eaf7c' }],
    ['meta', { name: 'theme-color', content: '#3eaf7c' }],
  ],

  pagePatterns: ['**/*.md', '!.vuepress', '!node_modules', '!old'],

  plugins: [
    searchPlugin({
      // 配置项
    }),
  ],

  markdown: {
    toc: {
      level: [2, 3, 4],
    }
  },

  // site-level locales config
  locales: {
    '/': {
      lang: 'zh-CN',
      title: '腾讯云代码分析',
      description: '用心关注每行代码迭代、助力传承卓越代码文化！',
    },
    '/en': {
      lang: 'en-US',
      title: 'Tencent Cloud Code Analysis',
      description: '用心关注每行代码迭代、助力传承卓越代码文化！',
    },
  },


  theme: defaultTheme({
    logo: '/images/favicon.png',

    repo: 'https://github.com/Tencent/CodeAnalysis',

    docsDir: 'doc',

    // theme-level locales config
    locales: {
      /**
       * English locale config
       *
       * As the default locale of @vuepress/theme-default is English,
       * we don't need to set all of the locale fields
       */
      '/en': {
        // navbar
        navbar: navbar.en,
        selectLanguageName: 'English',
        selectLanguageText: 'Languages',
        selectLanguageAriaLabel: 'Languages',

        // sidebar
        sidebar: sidebar.en,
        sidebarDepth: 1,

        // page meta
        editLinkText: 'Edit this page on GitHub',

      },

      /**
       * Chinese locale config
       */
      '/': {
        // navbar
        navbar: navbar.zh,
        selectLanguageName: '简体中文',
        selectLanguageText: '选择语言',
        selectLanguageAriaLabel: '选择语言',

        // sidebar
        sidebar: sidebar.zh,
        sidebarDepth: 1,

        // page meta
        editLinkText: '在 GitHub 上编辑此页',
        lastUpdatedText: '上次更新',
        contributorsText: '贡献者',

        // custom containers
        tip: '提示',
        warning: '注意',
        danger: '警告',

        // 404 page
        notFound: [
          '这里什么都没有',
          '我们怎么到这来了？',
          '这是一个 404 页面',
          '看起来我们进入了错误的链接',
        ],
        backToHome: '返回首页',

        // a11y
        openInNewWindow: '在新窗口打开',
        toggleDarkMode: '切换夜间模式',
        toggleSidebar: '切换侧边栏',

      },
    },

    themePlugins: {
      // only enable git plugin in production mode
      git: isProd,
      // use shiki plugin in production mode instead
      prismjs: !isProd,
    },

  }),
})
