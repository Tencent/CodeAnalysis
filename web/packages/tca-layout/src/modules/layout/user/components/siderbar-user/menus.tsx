import React from 'react';

// 项目内
import { t } from '@src/i18n/i18next';
import { MenuItem } from '@src/components/menu-layout';
import User from 'coding-oa-uikit/lib/icon/User';
import Shield from 'coding-oa-uikit/lib/icon/Shield';
import Group from 'coding-oa-uikit/lib/icon/Group';
import Ticket from 'coding-oa-uikit/lib/icon/Ticket';

const MENUS: MenuItem[] = [
  {
    icon: <User />,
    title: t('用户信息'),
    link: '/user/profile',
    key: 'profile',
  },
  {
    icon: <Shield />,
    title: t('凭证管理'),
    link: '/user/auth',
    key: 'auth',
  },
  {
    icon: <Group />,
    title: t('用户管理'),
    link: '/user/manage',
    key: 'manage',
  },
  {
    icon: <Ticket />,
    title: t('个人令牌'),
    link: '/user/token',
    key: 'token',
  },
];

export default MENUS;
