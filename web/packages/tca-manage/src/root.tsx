import React, { Suspense } from 'react';
import { BrowserRouter as Router, Switch, Route, Redirect } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { hot } from 'react-hot-loader';
import { get } from 'lodash';

// 项目内
import Users from '@src/modules/users';
import Jobs from '@src/modules/jobs';
import Nodes from '@src/modules/nodes';
import NodeProcess from '@src/modules/nodes/process';

const Root = () => {
  const APP = useSelector((state: any) => state.APP);
  const isSuperuser = get(APP, 'user.is_superuser', false);
  if (!isSuperuser) {
    return <div className='text-center pa-lg' >
      <h1>403</h1>
      <p>您没有访问后台管理的权限</p>
    </div>
  }
  return (
    <Router>
      <Suspense fallback={null}>
        <Switch>
          <Route path="/manage/users" component={Users} />
          <Route path="/manage/jobs" component={Jobs} />
          <Route path="/manage/nodes/:nodeId/process" component={NodeProcess} />
          <Route path="/manage/nodes" component={Nodes} />
          <Redirect from="/manage" to="/manage/users" />
        </Switch>
      </Suspense>
    </Router >
  );
}

export default hot(module)(Root);
