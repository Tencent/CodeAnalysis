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
    text: '了解更多',
    children: [
      {
        text: '深入',
        children: [
          '/en/advanced/任务分布式执行.md',
          '/en/advanced/集成代码分析工具.md',
        ],
      },
      {
        text: '文章',
        children: [

        ],
      },
    ]
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

