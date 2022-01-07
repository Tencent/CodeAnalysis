// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================


import React from 'react';
import { useParams } from 'react-router-dom';
// 项目内
import MenuLayout from '@src/components/menu-layout';
import getMenus from './menus';

const SiderBar = () => {
  const { orgSid, name }: any = useParams();
  return (
    <MenuLayout
      menus={getMenus(orgSid, name)}
      breakpoint="md"
    />
  );
};

export default SiderBar;
