import type { NavbarConfig } from '@vuepress/theme-default'

export const en: NavbarConfig = [
  {
    text: '快速入门',
    link: '/en/quickStarted/intro.md',
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
      '/en/community/contribute.md',
      '/en/community/changelog.md',
      '/en/community/joingroup.md',
      {
        text: '体验官方版本',
        link: 'https://tca.tencent.com/',
      }
    ]
  },
]

