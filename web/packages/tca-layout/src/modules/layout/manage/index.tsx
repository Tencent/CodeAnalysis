// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================


import React from 'react';
import { useHistory } from 'react-router-dom';
import { Button } from 'coding-oa-uikit';

// 项目内
import Header from '@src/modules/layout/header';
import { useStateStore } from '@src/context/store';
import { getHomeRouter } from '@src/utils/getRoutePath';
import SiderBarManage from './siderbar-manage';
import s from './style.scss'


function Manage() {
  const history = useHistory();
  const { userinfo } = useStateStore();
  if (!userinfo.is_superuser) {
    return <div className={s.manageNotPrem}>
      <h1>403</h1>
      <p className='mb-md'>没有权限访问后台管理页面</p>
      <Button onClick={() => {
        history.goBack()
      }} type='primary'>返回上一页</Button><Button onClick={() => {
        history.replace(getHomeRouter())
      }} type='secondary' className='ml-md'>返回首页</Button>
    </div>
  }
  return (
    <>
      <Header />
      <SiderBarManage />
    </>
  );
}

export default Manage;
