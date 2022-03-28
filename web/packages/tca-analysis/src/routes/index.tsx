// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

// import React, { useEffect, useState, lazy } from 'react';
import React, { useEffect, useState } from 'react';
import { Route, Switch, useParams, useHistory } from 'react-router-dom';
import { toNumber, isEmpty, get, find } from 'lodash';

import { useStateStore, useDispatchStore } from '@src/context/store';
import {
  SET_CUR_REPO,
  SET_PROJECT_MEMBER,
  SET_REPOS,
  SET_REPOS_LOADING,
} from '@src/context/constant';
import {
  PROJECT_ROUTE_PREFIX,
  SCHEMES_ROUTE_PREFIX,
  BASE_ROUTE_PREFIX,
  REPOS_ROUTE_PREFIX,
} from '@src/common/constants';
// import { getBaseRouter } from '@src/utils/getRoutePath';
import { getRepos, getProjectTeamMembers } from '@src/services/common';

import Loading from '@src/components/loading';

import Projects from '@src/modules/projects';
import Repos from '@src/modules/repos';
import PkgRules from '@src/modules/schemes/code-lint/pkg-rules';
import AllRules from '@src/modules/schemes/code-lint/all-rules';
import Schemes from '@src/modules/schemes';

import Welcome from '@src/modules/welcome';
import Create from '@src/modules/repos/create';
import Detail from '@src/modules/projects/issues/detail';
import CCFilesDetail from '@src/modules/projects/metric/ccfiles/detail';
import CCIssuesDetail from '@src/modules/projects/metric/ccissues/detail';
import DupDetail from '@src/modules/projects/metric/dupfiles/detail';
import ScanDetail from '@src/modules/projects/scan-history/detail';

// const Projects = lazy(() => import('@src/modules/projects'));
// const Repos = lazy(() => import('@src/modules/repos'));
// const PkgRules = lazy(() => import('@src/modules/schemes/code-lint/pkg-rules'));
// const AllRules = lazy(() => import('@src/modules/schemes/code-lint/all-rules'));
// const Schemes = lazy(() => import('@src/modules/schemes'));

// const Welcome = lazy(() => import('@src/modules/welcome'));
// const Create = lazy(() => import('@src/modules/repos/create'));
// const Detail = lazy(() => import('@src/modules/projects/issues/detail'));
// const CCFilesDetail = lazy(() => import('@src/modules/projects/metric/ccfiles/detail'));
// const CCIssuesDetail = lazy(() => import('@src/modules/projects/metric/ccissues/detail'));
// const DupDetail = lazy(() => import('@src/modules/projects/metric/dupfiles/detail'));
// const ScanDetail = lazy(() => import('@src/modules/projects/scan-history/detail'));


const PATH_NAME = ['/repos/create', '/template'];

const Routers = () => {
  const history = useHistory();
  const { org_sid: orgSid, team_name: teamName }: any = useParams();
  let { repoId }: any = useParams();
  const { repos } = useStateStore();
  const dispatch = useDispatchStore();
  const [loading, setLoading] = useState(true);
  const [isWelcome, setIsWelcome] = useState(PATH_NAME.every((path: any) => !window.location.pathname.match(path)));

  repoId = toNumber(repoId);

  const getPageStatus = (pathname: string) => setIsWelcome(PATH_NAME.every((path: any) => !pathname.match(path)));

  const getRepoList = async (page = 1) => {
    const offset = (page - 1) * 100;
    const response = await getRepos(orgSid, teamName, { limit: 100, offset });
    let list = get(response, 'results', []);

    if (response.next) {
      list = list.concat(await getRepoList(page + 1));
    }
    return list;
  };

  const init = async () => {
    dispatch({
      type: SET_REPOS,
      payload: [],
    });
    // 获取当前项目内的代码库列表
    setLoading(true);
    dispatch({
      type: SET_REPOS_LOADING,
      payload: true,
    });
    const list = (await getRepoList()) || [];
    if (!isEmpty(list)) {
      // 将获取的代码库列表存入SET_REPOS
      dispatch({
        type: 'SET_REPOS',
        payload: list,
      });
    }
    setLoading(false);
    dispatch({
      type: SET_REPOS_LOADING,
      payload: false,
    });

    // 成员设置
    const members = await getProjectTeamMembers(orgSid, teamName);
    dispatch({
      type: SET_PROJECT_MEMBER,
      payload: members,
    });

    // 如果没有curRepo，则获取链接中的代码库或列表中第一个代码库
    // if (isEmpty(curRepo)) {
    //     const repo = repoId ? find(list, { id: repoId }) : list[0];

    //     // 存在repo，将其存入context
    //     if (!isEmpty(repo)) {
    //         dispatch({
    //             type: SET_CUR_REPO,
    //             payload: repo,
    //         });
    //     } else {
    //         // history.replace(`${getBaseRouter(orgSid, teamName)}/repos`);
    //     }
    // }
    // 由于切换项目时，curRepo存在，因此不用上述内容，切换项目重新set repo
    const repo = repoId ? find(list, { id: repoId }) : list[0];

    // 存在repo，将其存入context
    if (!isEmpty(repo)) {
      dispatch({
        type: SET_CUR_REPO,
        payload: repo,
      });
    } else {
      // history.replace(`${getBaseRouter(orgSid, teamName)}/repos`);
    }
  };

  useEffect(() => getPageStatus(history.location?.pathname), [
    teamName,
    history.location?.pathname,
  ]);

  useEffect(() => {
    init();
  }, [teamName]);

  if (loading) {
    return <Loading />;
  }

  if (isEmpty(repos) && isWelcome) {
    return <Welcome />;
  }

  return (
    <Switch>
      <Route exact path={`${REPOS_ROUTE_PREFIX}/create`} component={Create} />
      <Route path={`${REPOS_ROUTE_PREFIX}/:repoId?`} component={Repos} />

      <Route
        exact
        path={`${PROJECT_ROUTE_PREFIX}/codelint-issues/:issueId`}
        component={Detail}
      />
      <Route
        exact
        path={`${PROJECT_ROUTE_PREFIX}/metric/ccfiles/:fileId`}
        component={CCFilesDetail}
      />
      <Route
        exact
        path={`${PROJECT_ROUTE_PREFIX}/metric/ccissues/:issueId`}
        component={CCIssuesDetail}
      />
      <Route
        exact
        path={`${PROJECT_ROUTE_PREFIX}/metric/dupfiles/:issueId`}
        component={DupDetail}
      />
      <Route
        exact
        path={`${PROJECT_ROUTE_PREFIX}/scan-history/:jobId/:scanTab?`}
        component={ScanDetail}
      />
      <Route path={`${PROJECT_ROUTE_PREFIX}`} component={Projects} />
      <Route
        exact
        path={`${SCHEMES_ROUTE_PREFIX}/check-profiles/:checkProfileId/pkg/:pkgId`}
        component={PkgRules}
      />
      <Route
        exact
        path={`${SCHEMES_ROUTE_PREFIX}/check-profiles/:checkProfileId/pkg/:pkgId/add-rule`}
        component={AllRules}
      />
      {/* <Route path={`${BASE_ROUTE_PREFIX}/schemes/:schemeId?/:tabs?`} component={Schemes} /> */}
      <Route path={`${SCHEMES_ROUTE_PREFIX}/:tabs?`} component={Schemes} />

      <Route
        exact
        path={`${BASE_ROUTE_PREFIX}/code-analysis/repos/:repoId?/projects`}
        component={Projects}
      />
      <Route
        path={`${BASE_ROUTE_PREFIX}/code-analysis/repos/:repoId?/schemes`}
        component={Schemes}
      />
    </Switch>
  );
};

export default Routers;
