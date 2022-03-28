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

const MENUS: MenuItem[] = [
  {
    icon: <Group />,
    title: t('用户管理'),
    link: '/manage/users',
    key: 'users',
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
];

export default MENUS;
