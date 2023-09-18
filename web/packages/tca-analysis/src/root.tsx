import React, { Suspense } from 'react';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';

import Loading from '@tencent/micro-frontend-shared/tdesign-component/loading';
import routes, { RouteListener } from '@plat/routes';
import { BASE_ROUTE_PREFIX } from '@src/constant';
import Routers from '@src/routes';
import { StoreProvider } from './context/store';

const Root = () => (
  <Suspense fallback={<Loading />}>
    <Router>
      <RouteListener>
        <Switch>
          {routes.map(item => <Route key={`${item.path}`} {...item} />)}
          <StoreProvider>
            <Route
              path={`${BASE_ROUTE_PREFIX}/(code-analysis)?/(project|scheme)?/repos/:repoId?`}
              component={Routers}
            />
          </StoreProvider>
        </Switch>
      </RouteListener>
    </Router>
  </Suspense>
);

export default Root;
