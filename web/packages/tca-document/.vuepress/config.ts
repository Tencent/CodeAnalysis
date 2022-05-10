import { defineUserConfig } from '@vuepress/cli'
import { defaultTheme } from '@vuepress/theme-default'
import { navbar, sidebar } from './configs'

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

  // site-level locales config
  locales: {
    '/': {
      lang: 'zh-CN',
      title: '腾讯云代码分析',
      description: '腾讯云代码分析帮助文档',
    },
    '/en': {
      lang: 'en-US',
      title: 'Tencent Code Analysis',
      description: 'Tencent Code Analysis Document',
    },
  },


  theme: defaultTheme({
    logo: '/images/favicon.png',

    repo: 'https://github.com/Tencent/CodeAnalysis',

    docsDir: 'web/packages/tca-document',

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