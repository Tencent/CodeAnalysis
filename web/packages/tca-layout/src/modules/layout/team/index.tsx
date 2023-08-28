import React, { useEffect, useState } from 'react';
import { useParams, useHistory, Switch, Route, Redirect } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { message } from 'tdesign-react';

import Loading from '@tencent/micro-frontend-shared/tdesign-component/loading';

// 项目内
import Header from '@plat/modules/header';
import Container from '@src/component/container';
import Members from '@src/modules/team/components/members';
import Profile from '@src/modules/team/components/profile';
import Projects from '@src/modules/team/components/projects';
import Workspace from '@src/modules/team/components/workspace';
import Analysis from '@src/modules/layout/project/index';
import Tools from '@src/modules/tools';
import ToolDetail from '@src/modules/tools/detail-components';
import Toollibs from '@src/modules/tool-libs';
import Nodes from '@src/modules/nodes';
import NodeProcess from '@src/modules/nodes/process';
import { getTeamInfo } from '@src/services/team';
import Constant from '@src/reducer/constant';
import { getTeamsRouter } from '@src/utils/getRoutePath';
import { reportOrgInfo } from '@plat/util';

// 模块内
import Sidebar from './sidebar';


const TeamLayout = () => {
  const [loading, setLoading] = useState(true);

  const { orgSid }: any = useParams();
  const history = useHistory();
  const storeDispatch = useDispatch();

  useEffect(() => {
    storeDispatch({
      type: Constant.SET_PROJECT_COMPLETED,
      payload: false,
    });
    setLoading(true);
    getTeamInfo(orgSid)
      .then((response: any) => {
        reportOrgInfo(response);
        if (response.status > 1) {
          message.error('您的团队还未审核通过');
          history.replace(getTeamsRouter());
        } else {
          storeDispatch({
            type: Constant.SET_PROJECT_COMPLETED,
            payload: true,
          });
          storeDispatch({
            type: Constant.SET_ORG,
            payload: response,
          });
        }
      })
      .catch(() => {
        history.replace(getTeamsRouter());
      })
      .finally(() => {
        setLoading(false);
      });
  }, [orgSid, storeDispatch, history]);

  if (loading) {
    return <Loading />;
  }

  return (
    <Switch>
      <Route path="/t/:orgSid/p/:name/" component={Analysis} />
      <>
        <Header />
        <Sidebar />
        <Container>
          <Switch>
            <Route path={'/t/:orgSid'} exact component={Workspace} />
            <Route path={'/t/:orgSid/workspace'} component={Workspace} />
            <Route path={'/t/:orgSid/projects'} component={Projects} />
            <Route path={'/t/:orgSid/profile'} component={Profile} />
            <Route path={'/t/:orgSid/members'} component={Members} />
            <Route exact path="/t/:orgSid/tools/:toolId/:tab?" component={ToolDetail} />
            <Route exact path="/t/:orgSid/tools" component={Tools} />
            <Route exact path="/t/:orgSid/toollibs" component={Toollibs} />
            <Route path="/t/:orgSid/nodes/:nodeId/process" component={NodeProcess} />
            <Route path="/t/:orgSid/nodes/" component={Nodes} />
            <Route path={'/t/:orgSid/template'} component={null} />
            <Redirect to="/" />
          </Switch>
        </Container>
      </>
    </Switch>
  );
};

export default TeamLayout;
