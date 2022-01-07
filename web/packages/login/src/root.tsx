// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { Suspense } from 'react';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';
import { hot } from 'react-hot-loader/root';

import Login from './modules/login';


const Root = () => (
  <Suspense fallback={null}>
    <Router>
      <Switch>
        <Route path="/login" exact component={Login} />
      </Switch>
    </Router>
  </Suspense>
);

export default hot(Root);
