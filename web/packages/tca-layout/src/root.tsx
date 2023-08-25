import React, { Suspense } from 'react';
import { BrowserRouter as Router, Switch, Route, Redirect } from 'react-router-dom';
import { hot } from 'react-hot-loader/root';
import Loading from '@tencent/micro-frontend-shared/tdesign-component/loading';

import Home from '@src/modules/home';
import LoadInitService from './load-init-service';

// 项目内
import routes from '@plat/routes';

const Root = () => (
  <Router>
    <Suspense fallback={<Loading />}>
      <Switch>
        <Route path="/" exact component={Home} />
        <Route path="/login" render={() => ''} />
        <LoadInitService>
          <Switch>
            {routes.map(item => <Route key={`${item.path}`} {...item} />)}
            <Redirect from="/" to={routes[0].path instanceof Array ? routes[0].path[0] : routes[0].path} />,
          </Switch>
        </LoadInitService>
      </Switch>
    </Suspense>
  </Router>
);

export default hot(Root);
