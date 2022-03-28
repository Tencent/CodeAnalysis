// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================


import React from 'react';
// 项目内
import MenuLayout from '@src/components/menu-layout';
import menus from './menus';

const SiderBar = () => <MenuLayout menus={menus} breakpoint="md"></MenuLayout>;

export default SiderBar;
