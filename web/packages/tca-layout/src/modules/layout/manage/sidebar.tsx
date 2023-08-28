import React from 'react';
// 项目内
import LayoutMenu from '@src/component/layout-menu';
import { NAVS as menus } from '@plat/modules/manage';


const SiderBar = () => <LayoutMenu menus={menus} breakpoint='lg' />;

export default SiderBar;
