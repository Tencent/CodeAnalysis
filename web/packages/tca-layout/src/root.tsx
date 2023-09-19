import React, { Suspense } from 'react';
import { BrowserRouter as Router, Switch, Route, Redirect } from 'react-router-dom';
import { get } from 'lodash';

import Loading from '@tencent/micro-frontend-shared/tdesign-component/loading';

import Home from '@src/modules/home';
import LoadInitService from './load-init-service';

// 项目内
import { ROOT_ROUTERS } from '@src/routes';

/** 路由 */
const routes = ROOT_ROUTERS.map(item => <Route key={`${item.path}`} {...item} />);
/** 重定向路由 */
const redirectRoute = <Redirect from="/" to={get(ROOT_ROUTERS, '0.path.0') || get(ROOT_ROUTERS, '0.path')} />;

const Root = () => (
  <Router>
    <Suspense fallback={<Loading />}>
      <Switch>
        <Route path="/" exact component={Home} />
        <Route path="/login" render={() => ''} />
        <LoadInitService>
          <Switch>
            {routes}{redirectRoute}
          </Switch>
        </LoadInitService>
      </Switch>
    </Suspense>
  </Router>
);

export default Root;
