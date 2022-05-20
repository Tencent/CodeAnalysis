import type { NavbarConfig } from '@vuepress/theme-default'

export const en: NavbarConfig = [
  {
    text: '快速入门',
    link: '/en/quickStarted/intro.html',
  },
  {
    text: '帮助文档',
    link: '/en/guide/',
  },
  {
    text: 'API',
    link: '/en/api/',
  },
  {
    text: '社区',
    children: [
      '/en/community/contribute.html',
      '/en/community/changelog.html',
      '/en/community/joingroup.html',
      {
        text: '体验官方版本',
        link: 'https://tca.tencent.com/',
      }
    ]
  },
]

