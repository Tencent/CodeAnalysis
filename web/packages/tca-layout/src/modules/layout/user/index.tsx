import React from 'react';
import { useRouteMatch, Route, Redirect, Switch } from 'react-router-dom';
// 项目内
import Container from '@src/component/container';
import Header from '@plat/modules/header';
import SideBar from './sidebar';
import Profile from './profile';
import Auth from './auth';
import Token from './token';

const User = () => {
  const { url } = useRouteMatch();
  return (
    <>
      <Header />
      <SideBar />
      <Container>
        <Switch>
          <Route path={`${url}/profile`} component={Profile} />
          <Route path={`${url}/auth`} component={Auth} />
          <Route path={`${url}/token`} component={Token} />
          <Redirect to={`${url}/profile`} />
        </Switch>
      </Container>
    </>
  );
};

export default User;
