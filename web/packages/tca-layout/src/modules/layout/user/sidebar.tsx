import React from 'react';
import { useTranslation } from 'react-i18next';
import User from 'coding-oa-uikit/lib/icon/User';
import Shield from 'coding-oa-uikit/lib/icon/Shield';
import Ticket from 'coding-oa-uikit/lib/icon/Ticket';
// 项目内
import LayoutMenu from '@src/component/layout-menu';

const SiderBar = () => {
  const { t } = useTranslation();
  return <LayoutMenu
    title={<div className="fs-18">{t('个人中心')}</div>}
    menus={[
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
        icon: <Ticket />,
        title: t('个人令牌'),
        link: '/user/token',
        key: 'token',
      },
    ]}
  />;
};

export default SiderBar;
