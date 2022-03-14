// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { Suspense } from 'react';
import { BrowserRouter as Router, Switch, Route, Redirect } from 'react-router-dom';
import { hot } from 'react-hot-loader';

import User from '@src/modules/layout/user';
import Teams from '@src/modules/team';
import Invite from '@src/modules/team/components/invite';
import Team from '@src/modules/layout/team';
import Home from '@src/modules/home';
import Manage from '@src/modules/layout/manage';
import LoadInitService from './load-init-service';

const Root = () => (
  <Router>
    <Suspense fallback={null}>
      <Switch>
        <Route path="/" exact component={Home} />
        <Route path="/login" render={() => ''} />
        <LoadInitService>
          <Switch>
            <Route path="/manage" component={Manage} />
            <Route path="/user" component={User} />
            <Route path="/teams" component={Teams} />
            <Route path="/t/invite/:code" component={Invite} />
            <Route path="/t/:orgSid" component={Team} />
            <Redirect to="/" />
          </Switch>
        </LoadInitService>
      </Switch>
    </Suspense>
  </Router>
);

export default hot(module)(Root);
