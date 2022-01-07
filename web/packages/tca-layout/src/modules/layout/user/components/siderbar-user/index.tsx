// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React from 'react';
// 项目内
import { t } from '@src/i18n/i18next';
import MenuLayout from '@src/components/menu-layout';
import menus from './menus';

const useTitle = () => <div className="fs-18">{t('个人中心')}</div>;

const SiderBar = () => {
  const title = useTitle();
  return <MenuLayout menus={menus} title={title} />;
};

export default SiderBar;
