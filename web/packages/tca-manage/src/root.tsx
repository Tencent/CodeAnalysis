import React, { Suspense } from 'react';
import { BrowserRouter as Router, Switch, Route, Redirect } from 'react-router-dom';
import { hot } from 'react-hot-loader';
import Loading from '@tencent/micro-frontend-shared/tdesign-component/loading';

// 项目内
import routes from '@plat/routes';

const Root = () => <Router>
  <Suspense fallback={<Loading />}>
    <Switch>
      {routes.map(item => <Route key={`${item.path}`} path={item.path} component={item.component} />)}
      <Redirect from="/" to={routes[0].path instanceof Array ? routes[0].path[0] : routes[0].path} />,
    </Switch>
  </Suspense>
</Router >;
export default hot(module)(Root);
