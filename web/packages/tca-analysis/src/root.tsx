import React, { Suspense } from 'react';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';
import { hot } from 'react-hot-loader';

import {
  TMPL_ROUTE_PREFIX,
  BASE_ROUTE_PREFIX,
} from '@src/common/constants';
import Loading from '@src/components/loading';
import Routers from '@src/routes';
import Template from '@src/modules/template';
import TemplateDetail from '@src/modules/template/detail';
import PkgRules from '@src/modules/template/code-lint/pkg-rules';
import AllRules from '@src/modules/template/code-lint/all-rules';
import PTOverview from '@src/modules/project-team/overview';
import PTGroup from '@src/modules/project-team/group';

const Root = () => (
        <Suspense fallback={Loading}>
            <Router>
                <Switch>
                    <Route exact path={`${BASE_ROUTE_PREFIX}/profile`} component={PTOverview} />
                    <Route exact path={`${BASE_ROUTE_PREFIX}/group`} component={PTGroup} />
                    <Route
                        exact
                        path={`${TMPL_ROUTE_PREFIX}/:id/check-profiles/:checkProfileId/pkg/:pkgId/add-rule`}
                        component={AllRules}
                    />
                    <Route
                        exact
                        path={`${TMPL_ROUTE_PREFIX}/:id/check-profiles/:checkProfileId/pkg/:pkgId`}
                        component={PkgRules}
                    />
                    <Route
                        path={`${TMPL_ROUTE_PREFIX}/:id/:tabs?`}
                        component={TemplateDetail}
                    />
                    <Route path={`${TMPL_ROUTE_PREFIX}`} component={Template} />
                    <Route
                        path={`${BASE_ROUTE_PREFIX}/(code-analysis)?/repos/:repoId?`}
                        component={Routers}
                    />
                    {/* <Route path='/t/:org_sid/p/:team_name' /> */}
                </Switch>
            </Router>
        </Suspense>
);

export default hot(module)(Root);
