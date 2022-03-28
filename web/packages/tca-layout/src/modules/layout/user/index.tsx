// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React from 'react';
import ReactDOM from 'react-dom';
import { useRouteMatch, Route, Redirect, Switch } from 'react-router-dom';
// 项目内
import Header from '@src/modules/layout/header';
import SiderBarUser from './components/siderbar-user';
import Profile from './profile';
import Auth from './auth';
import Token from './token';

const User = () => {
  const { url } = useRouteMatch();
  const containerNode = document.getElementById('container');
  return (
    <>
      <Header />
      <SiderBarUser />
      {containerNode
        && ReactDOM.createPortal(
          <Switch>
            <Route path={`${url}/profile`} component={Profile} />
            <Route path={`${url}/auth`} component={Auth} />
            <Route path={`${url}/token`} component={Token} />
            <Redirect to={`${url}/profile`} />
          </Switch>,
          containerNode,
        )}
    </>
  );
};

export default User;
