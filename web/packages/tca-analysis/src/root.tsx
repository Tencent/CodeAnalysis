import React, { Suspense } from 'react';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';
import { hot } from 'react-hot-loader';
import Loading from '@tencent/micro-frontend-shared/component/loading';
// 项目内
import { BASE_ROUTE_PREFIX } from '@src/constant';
import Routers from '@src/routes';
import routes from '@plat/routes';
import { StoreProvider } from './context/store';

const Root = () => (
  <Suspense fallback={<Loading />}>
    <Router>
      <Switch>
        {routes.map(item => (
          <Route
            key={`${item.path}`}
            path={item.path}
            component={item.component}
          />
        ))}
        <StoreProvider>
          <Route
            path={`${BASE_ROUTE_PREFIX}/(code-analysis)?/repos/:repoId?`}
            component={Routers}
          />
        </StoreProvider>
      </Switch>
    </Router>
  </Suspense>
);

export default hot(module)(Root);
