import type { NavbarConfig } from '@vuepress/theme-default'

export const zh: NavbarConfig = [
  {
    text: '快速入门',
    link: '/zh/quickStarted/intro.html',
  },
  {
    text: '帮助文档',
    link: '/zh/guide/',
  },
  {
    text: 'API',
    link: '/zh/api/',
  },
  {
    text: '社区',
    children: [
      '/zh/community/contribute.html',
      '/zh/community/changelog.html',
      '/zh/community/joingroup.html',
      {
        text: '体验官方版本',
        link: 'https://tca.tencent.com/',
      }
    ]
  },
]
