import React, { Suspense } from 'react';
import { BrowserRouter as Router, Switch, Route, Redirect } from 'react-router-dom';
import { hot } from 'react-hot-loader';
import Loading from '@tencent/micro-frontend-shared/component/loading';

// import { isEnableManage } from '@src/utils';
// import Manage from '@src/modules/layout/manage';
// import User from '@src/modules/layout/user';
// import Teams from '@src/modules/team';
// import Invite from '@src/modules/team/components/invite';
// import Team from '@src/modules/layout/team';
import Home from '@src/modules/home';
import LoadInitService from './load-init-service';
import InitMatomo from './init-matomo';

// 项目内
import routes from '@plat/routes';

const Root = () => (
  <Router>
    <Suspense fallback={<Loading />}>
      <InitMatomo>
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
      </InitMatomo>
    </Suspense>
  </Router>
);

export default hot(module)(Root);
