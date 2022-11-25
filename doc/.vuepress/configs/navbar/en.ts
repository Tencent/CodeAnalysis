import type { NavbarConfig } from '@vuepress/theme-default'

export const en: NavbarConfig = [
  {
    text: '快速部署',
    link: '/en/quickStarted/',
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
          '/en/advanced/使用自建工具git库.md',
        ],
      },
      {
        text: '依赖安装参考',
        children: [
          '/en/advanced/install_python37_on_centos.md',
          '/en/advanced/install_python37_on_ubuntu.md',
          '/en/advanced/install_mysql_on_centos.md',
          '/en/advanced/install_redis_from_source.md',
          '/en/advanced/install_redis_on_centos.md',
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

