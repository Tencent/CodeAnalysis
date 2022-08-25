import type { SidebarConfig } from '@vuepress/theme-default'

export const zh: SidebarConfig = {
  '/zh/guide/': [
    {
      text: '介绍',
      children: [
        '/zh/guide/README.md',
        '/zh/guide/快速入门/快速启动一次代码分析.md'
      ],
    },
    {
      text: '团队管理',
      children: [
        '/zh/guide/团队管理/团队管理.md',
        '/zh/guide/团队管理/成员权限.md',
        '/zh/guide/团队管理/节点管理.md',
      ]
    },
    {
      text: '分析结果',
      children: [
        '/zh/guide/代码检查/分析结果查看.md',
        '/zh/guide/代码检查/添加规则配置.md',
        {
          text: '典型工具接入指引',
          children: [
            '/zh/guide/代码检查/工具/eslint.md',
            '/zh/guide/代码检查/工具/golangcilint.md',
          ],
        },
      ]
    },
    {
      text: '分析方案',
      children: [
        '/zh/guide/分析方案/基础属性配置.md',
        '/zh/guide/分析方案/代码检查配置.md',
        '/zh/guide/分析方案/代码检查规则配置.md',
        '/zh/guide/分析方案/代码检查编译配置.md',
        '/zh/guide/分析方案/代码度量配置.md',
        '/zh/guide/分析方案/过滤配置.md',
        '/zh/guide/分析方案/分析方案模板说明.md',
      ]
    },
    {
      text: '工具管理',
      children: [
        '/zh/guide/工具管理/工具管理说明.md',
        '/zh/guide/工具管理/自定义规则.md',
        '/zh/guide/工具管理/自定义工具.md',
      ]
    },
    {
      text: '后台管理',
      children: [
        '/zh/guide/后台管理/用户管理.md',
        '/zh/guide/后台管理/团队管理.md',
        '/zh/guide/后台管理/项目管理.md',
        '/zh/guide/后台管理/分析记录管理.md',
        '/zh/guide/后台管理/节点管理.md',
        '/zh/guide/后台管理/工具管理.md',
        '/zh/guide/后台管理/OAuth管理.md',
      ]
    },
    {
      text: '客户端',
      children: [
        '/zh/guide/客户端/本地分析.md',
        '/zh/guide/客户端/常驻节点分析.md',
        '/zh/guide/客户端/其他配置.md',
      ]
    },
    {
      text: '服务端',
      children: [
        '/zh/guide/服务端/server.md',
        '/zh/guide/服务端/deploy_with_minio.md',
      ]
    },
    {
      text: 'Web端',
      children: [
        '/zh/guide/web/web.md',
        '/zh/guide/web/deploySource.md',
      ]
    },
  ],
  '/zh/advanced/': [
    {
      text: '深入',
      children: [
        '/zh/advanced/任务分布式执行.md',
        '/zh/advanced/集成代码分析工具.md',
      ],
    }
  ],
  '/zh/community/': [
    {
      text: '社区资源',
      children: [
        '/zh/community/contribute.md',
        '/zh/community/pr.md',
        '/zh/community/changelog.md',
        '/zh/community/joingroup.md',
      ]
    },
  ],
  '/zh/api/': [
    {
      text: 'API',
      children: [
        '/zh/api/README.md',
        '/zh/api/对象主要字段说明.md',
        '/zh/api/项目管理模块接口.md',
        '/zh/api/任务管理模块接口.md',
        '/zh/api/结果概览模块接口.md',
        '/zh/api/代码扫描数据模块接口.md',
        '/zh/api/代码度量数据模块接口.md',
      ]
    },
  ],
  '/zh/quickStarted/': [
    {
      text: '快速入门',
      children: [
        '/zh/quickStarted/README.md',
        '/zh/quickStarted/dockerDeploy.md',
        '/zh/quickStarted/dockercomposeDeploy.md',
        '/zh/quickStarted/codeDeploy.md',
      ]
    },
    {
      text: '其他',
      // collapsible: true,
      children: [
        '/zh/quickStarted/enhanceDeploy.md',
        '/zh/quickStarted/tools.md',
        '/zh/quickStarted/FAQ.md',
      ],
    },
  ],
}