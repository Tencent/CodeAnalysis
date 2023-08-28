import React, { Suspense } from 'react';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';
import { hot } from 'react-hot-loader/root';
import Header from '@tencent/micro-frontend-shared/tca/component/layout-header';
import Footer from '@src/modules/footer';

// 项目内
import routes from '@plat/routes';

const Root = () => (
  <Suspense fallback={null}>
    <Router>
      <Header logoColor='bule' height={56} transparent />
      <Footer />
      <Switch>
        {routes.map(item => <Route key={`${item.path}`} {...item} />)}
      </Switch>
    </Router>
  </Suspense>
);

export default hot(Root);
