import type { SidebarConfig } from '@vuepress/theme-default'

export const en: SidebarConfig = {
  '/en/guide/': [
    {
      text: '快速入门',
      children: [
        '/en/guide/README.md',
        '/en/guide/快速入门/快速启动一次代码分析.md',
      ],
    },
    {
      text: '团队管理相关',
      children: [
        '/en/guide/团队管理/团队管理.md',
        '/en/guide/团队管理/成员权限.md',
      ]
    },
    {
      text: '代码检查',
      children: [
        '/en/guide/代码检查/分析结果查看.md',
      ]
    },
    {
      text: '分析方案 & 模板',
      children: [
        '/en/guide/分析方案/基础属性配置.md',
        '/en/guide/分析方案/代码检查配置.md',
        '/en/guide/分析方案/代码检查规则配置.md',
        '/en/guide/分析方案/代码检查编译配置.md',
        '/en/guide/分析方案/代码度量配置.md',
        '/en/guide/分析方案/过滤配置.md',
        '/en/guide/分析方案/分析方案模板说明.md',
      ]
    },
    {
      text: '工具管理',
      children: [
        '/en/guide/工具管理/工具管理说明.md',
        '/en/guide/工具管理/自定义规则.md',
        '/en/guide/工具管理/自定义工具.md',
      ]
    },
    {
      text: '后台管理',
      children: [
        '/en/guide/后台管理/后台管理说明.md',
      ]
    },
    {
      text: 'CLIENT 客户端',
      children: [
        '/en/guide/客户端/配置说明.md',
        '/en/guide/客户端/本地分析.md',
        '/en/guide/客户端/常驻节点分析.md',
      ]
    },

  ],
  '/en/api/': [
    {
      text: '开放 API',
      children: [
        '/en/api/README.md',
        '/en/api/对象主要字段说明.md',
        '/en/api/项目管理模块接口.md',
        '/en/api/任务管理模块接口.md',
        '/en/api/结果概览模块接口.md',
        '/en/api/代码扫描数据模块接口.md',
        '/en/api/代码度量数据模块接口.md',
      ]
    },
  ]
}