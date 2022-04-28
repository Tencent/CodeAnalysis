// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useEffect, useState } from 'react';
import { useParams, useHistory, Switch, Route, Redirect } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { message } from 'coding-oa-uikit';
import LoadingIcon from 'coding-oa-uikit/lib/icon/Loading';
import { t } from '@src/i18n/i18next';

import Container from './container';
import Members from '@src/modules/team/components/members';
import Profile from '@src/modules/team/components/profile';
import Projects from '@src/modules/team/components/projects';
import Workspace from '@src/modules/team/components/workspace';
import Analysis from '@src/modules/layout/project/index';
import Tools from '@src/modules/tools';
import ToolDetail from '@src/modules/tools/detail-components';
import Toollibs from '@src/modules/tool-libs';


// 项目内
import { getTeamInfo } from '@src/services/team';

import Header from '@src/modules/layout/header';
import Constant from '@src/reducer/constant';

// 模块内
import Sidebar from './sidebar';

const getComponent = (Component: any) => (
  <>
    <Header />
    <Sidebar />
    <Container>
      <Component />
    </Container>
  </>
);

const TeamLayout = () => {
  const { orgSid }: any = useParams();
  const history = useHistory();
  const storeDispatch = useDispatch();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    storeDispatch({
      type: Constant.SET_PROJECT_COMPLETED,
      payload: false,
    });
    setLoading(true);
    getTeamInfo(orgSid)
      .then((response) => {
        if (response.status > 1) {
          message.error('您的团队还未审核通过');
          history.replace('/teams');
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
        history.replace('/teams');
      })
      .finally(() => {
        setLoading(false);
      });
  }, [orgSid]);

  if (loading) {
    return (
      <div className="text-center pa-sm fs-12">
        <LoadingIcon />
        <span className="ml-xs">{t('正在加载')}...</span>
      </div>
    );
  }

  return (
    <>
      <Switch>
        <Route path={'/t/:orgSid'} exact render={() => getComponent(Workspace)} />
        <Route path={'/t/:orgSid/workspace'} render={() => getComponent(Workspace)} />
        <Route path={'/t/:orgSid/projects'} render={() => getComponent(Projects)} />
        <Route path={'/t/:orgSid/profile'} render={() => getComponent(Profile)} />
        <Route path={'/t/:orgSid/members'} render={() => getComponent(Members)} />
        <Route key='detail' exact path="/t/:orgSid/tools/:toolId/:tab?" render={() => getComponent(ToolDetail)} />,
        <Route key='tools' exact path="/t/:orgSid/tools" render={() => getComponent(Tools)} />,
        <Route key='toollibs' exact path="/t/:orgSid/toollibs" render={() => getComponent(Toollibs)} />,
        <Route path="/t/:orgSid/p/:name/" render={() => <Analysis />} />
        <Redirect to="/" />
      </Switch>
    </>
  );
};

export default TeamLayout;
