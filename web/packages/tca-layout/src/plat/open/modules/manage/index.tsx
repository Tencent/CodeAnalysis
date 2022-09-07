import React from 'react';
import Project from 'coding-oa-uikit/lib/icon/Project';
import Group from 'coding-oa-uikit/lib/icon/Group';
import Scan from 'coding-oa-uikit/lib/icon/Scan';
import Sitemap from 'coding-oa-uikit/lib/icon/Sitemap';
import Panel from 'coding-oa-uikit/lib/icon/Panel';
import Tiles from 'coding-oa-uikit/lib/icon/Tiles';
import Key from 'coding-oa-uikit/lib/icon/Key';

export const NAVS = [
  {
    icon: <Group />,
    title: '用户管理',
    link: '/manage/users',
    key: 'users',
  },
  {
    icon: <Panel />,
    title: '团队管理',
    link: '/manage/orgs',
    key: 'orgs',
  },
  {
    icon: <Project />,
    title: '项目管理',
    link: '/manage/teams',
    key: 'teams',
  },
  {
    icon: <Scan />,
    title: '分析记录管理',
    link: '/manage/jobs',
    key: 'jobs',
  },
  {
    icon: <Sitemap />,
    title: '节点管理',
    link: '/manage/nodes',
    key: 'nodes',
  },
  {
    icon: <Tiles />,
    title: '工具管理',
    link: '/manage/tools',
    key: 'tools',
  },
  {
    icon: <Key />,
    title: 'OAuth管理',
    link: '/manage/oauths',
    key: 'oauth',
  },
];
