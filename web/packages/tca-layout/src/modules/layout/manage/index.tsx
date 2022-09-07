/**
 * 后台管理 nav
 * biz-start
 * 目前适用于体验、开源
 * biz-end
 */
import React from 'react';

// 项目内
import Header from '@src/modules/layout/header';
import SideBar from './sidebar';

function Manage() {
  return (
    <>
      <Header />
      <SideBar />
    </>
  );
}

export default Manage;
