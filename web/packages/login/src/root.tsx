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
