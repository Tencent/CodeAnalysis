// Copyright (c) 2021-2024 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

// import React, { useEffect, useState, lazy } from 'react';
import React, { useEffect, useState } from 'react';
import { Route, Switch, useHistory } from 'react-router-dom';
import { toNumber, isEmpty, find } from 'lodash';

import { useDispatchStore } from '@src/context/store';
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
} from '@src/constant';
// import { getBaseRouter } from '@src/utils/getRoutePath';
import { getRepos, getProjectTeamMembers } from '@src/services/common';
import { getRepo } from '@src/services/repos';

import Loading from '@tencent/micro-frontend-shared/tdesign-component/loading';

import Projects from '@src/modules/projects';
import PkgRules from '@src/modules/schemes/code-lint/pkg-rules';
import AllRules from '@src/modules/schemes/code-lint/all-rules';
import SchemeCheckRules from '@src/modules/schemes/code-lint/rules';
import Schemes from '@src/modules/schemes';

import Welcome from '@src/modules/welcome';
// import Create from '@src/modules/repos/create';
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
import { useParams } from '@plat/hooks';


const PATH_NAME = ['/repos/create', '/template'];

const Routers = () => {
  const history = useHistory();
  const { orgSid, teamName, repoId: repoStrId } = useParams();
  const [repos, setRepos] = useState([]);

  const dispatch = useDispatchStore();
  const [loading, setLoading] = useState(true);
  const [isWelcome, setIsWelcome] = useState(PATH_NAME.every((path: any) => !window.location.pathname.match(path)));

  const repoId = toNumber(repoStrId);

  const getPageStatus = (pathname: string) => setIsWelcome(PATH_NAME.every((path: any) => !pathname.match(path)));

  const init = async () => {
    setLoading(true);
    getRepos(orgSid, teamName, {
      scope: 'related_me',
      scm_url_or_name: '',
      limit: 12,
    }).then((res) => {
      const repos = (res?.results ?? []).map((item: any) => ({
        ...item,
        url: item.scm_url,
      }));
      setRepos(repos);
      dispatch({
        type: SET_REPOS,
        payload: repos,
      });

      if (repoId && !isNaN(toNumber(repoId))) {  // 从链接跳转进入
        getRepo(orgSid, teamName, repoId)
          .then((res: any) => {
            const repo = {
              ...res,
              url: res.scm_url,
            };
            dispatch({
              type: SET_CUR_REPO,
              payload: repo,
            });

            /* 如果当前代码库不存在代码库列表中，则追加到代码库列表 */
            if (!find(repos, { id: toNumber(repoId) })) {
              dispatch({
                type: SET_REPOS,
                payload: repos.concat(repo),
              });
            }
          })
          .finally(() => {
            setLoading(false);
          });
      } else {
        dispatch({
          type: SET_CUR_REPO,
          payload: repos[0] || {},
        });
        setLoading(false);
      }
    });
    // 成员设置
    const members = await getProjectTeamMembers(orgSid, teamName);
    dispatch({
      type: SET_PROJECT_MEMBER,
      payload: members,
    });
  };

  useEffect(() => {
    dispatch({
      type: SET_REPOS_LOADING,
      payload: loading,
    });
  }, [loading]);

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
        path={[
          // 从自定义规则包跳转的路由匹配
          `${SCHEMES_ROUTE_PREFIX}/check-profiles/:checkProfileId/pkg/:pkgId/add-rule`,
          // 从已配置规则列表跳转的路由匹配
          `${SCHEMES_ROUTE_PREFIX}/check-profiles/:checkProfileId/add-rule`,
        ]}
        // path={`${SCHEMES_ROUTE_PREFIX}/check-profiles/:checkProfileId/pkg/:pkgId/add-rule`}
        component={AllRules}
      />
      <Route
        exact
        path={`${SCHEMES_ROUTE_PREFIX}/check-profiles/:checkProfileId/checkrules`}
        component={SchemeCheckRules}
      />
      {/* <Route path={`${BASE_ROUTE_PREFIX}/schemes/:schemeId?/:tabs?`} component={Schemes} /> */}
      <Route path={`${SCHEMES_ROUTE_PREFIX}/:tabs?`} component={Schemes} />

      <Route
        exact
        path={[`${BASE_ROUTE_PREFIX}/code-analysis/repos/:repoId?/projects`, `${BASE_ROUTE_PREFIX}/code-analysis/project/repos/:repoId?/(projects)?`]}
        component={Projects}
      />
      <Route
        path={[`${BASE_ROUTE_PREFIX}/code-analysis/repos/:repoId?/schemes`, `${BASE_ROUTE_PREFIX}/code-analysis/scheme/repos/:repoId?/(schemes)?`]}
        component={Schemes}
      />
    </Switch>
  );
};

export default Routers;
