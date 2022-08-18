// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================


import React from 'react';

// 项目内
import { t } from '@src/i18n/i18next';
import { MenuItem } from '@src/components/menu-layout';
import Group from 'coding-oa-uikit/lib/icon/Group';
import Scan from 'coding-oa-uikit/lib/icon/Scan';
import Sitemap from 'coding-oa-uikit/lib/icon/Sitemap';
import Key from 'coding-oa-uikit/lib/icon/Key';
import Tiles from 'coding-oa-uikit/lib/icon/Tiles';
import Panel from 'coding-oa-uikit/lib/icon/Panel';
import Project from 'coding-oa-uikit/lib/icon/Project';

const MENUS: MenuItem[] = [
  {
    icon: <Group />,
    title: t('用户管理'),
    link: '/manage/users',
    key: 'users',
  },
  {
    icon: <Panel />,
    title: t('团队管理'),
    link: '/manage/orgs',
    key: 'orgs',
  },
  {
    icon: <Project />,
    title: t('项目管理'),
    link: '/manage/teams',
    key: 'teams',
  },
  {
    icon: <Scan />,
    title: t('分析记录管理'),
    link: '/manage/jobs',
    key: 'jobs',
  },
  {
    icon: <Sitemap />,
    title: t('节点管理'),
    link: '/manage/nodes',
    key: 'nodes',
  },
  {
    icon: <Tiles />,
    title: t('工具管理'),
    link: '/manage/tools',
    key: 'tools',
  },
  {
    icon: <Key />,
    title: t('OAuth管理'),
    link: '/manage/oauths',
    key: 'oauths',
  },
];

export default MENUS;
