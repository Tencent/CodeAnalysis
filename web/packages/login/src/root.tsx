import React, { Suspense } from 'react';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';
import { hot } from 'react-hot-loader/root';

// 项目内
import routes from '@plat/routes';

const Root = () => (
  <Suspense fallback={null}>
    <Router>
      <Switch>
        {routes.map(item => <Route key={`${item.path}`} {...item} />)}
      </Switch>
    </Router>
  </Suspense>
);

export default hot(Root);
