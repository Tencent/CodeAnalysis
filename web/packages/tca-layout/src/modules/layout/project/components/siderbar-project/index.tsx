
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
