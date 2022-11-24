// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分析项目入口文件
 */

import React, { useEffect, useState } from 'react';
import { Switch, Route, useHistory, useParams, Redirect } from 'react-router-dom';
import { isEmpty, get } from 'lodash';
import { useStateStore } from '@src/context/store';

import Repos from '@src/components/repos';
import { getProjectRouter } from '@src/utils/getRoutePath';
import { getSchemes } from '@src/services/schemes';
import { getTmplList } from '@src/services/template';

import { BASE_ROUTE_PREFIX, PROJECT_ROUTE_PREFIX } from '@src/constant';
import Nav from './nav';
import ProjectList from './project/project-list';
import FirstModal from './project/first-modal';

const Projects = () => {
  const history = useHistory();
  const { orgSid, teamName }: any = useParams();
  const { curRepo } = useStateStore();
  const [schemes, setSchemes] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    getTmplList(orgSid, { limit: 100 }).then((res: any) => {
      setTemplates(get(res, 'results', []));
    });
  }, []);

  useEffect(() => {
    if (curRepo.id) {
      getSchemesById();
    }
  }, [curRepo.id]);

  const getSchemesById = async () => {
    let res = await getSchemes(orgSid, teamName, curRepo.id, {
      limit: 1000,
      status: 1,
    });
    res = res.results || [];
    setSchemes(res);
    isEmpty(res) && setVisible(true);
  };

  return (
    <div>
      <Repos
        orgSid={orgSid}
        teamName={teamName}
        callback={(repo: any) => history.push(getProjectRouter(orgSid, teamName, repo.id))
        }
      />
      <FirstModal
        orgSid={orgSid}
        teamName={teamName}
        repoId={curRepo.id}
        visible={visible}
        templates={templates}
        onClose={() => setVisible(false)}
      />
      <Switch>
        <Route
          exact
          path={`${BASE_ROUTE_PREFIX}/code-analysis/(project)?/repos/:repoId?/projects`}
          render={() => <ProjectList templates={templates} schemes={schemes} />}
        />
        <Route
          path={`${PROJECT_ROUTE_PREFIX}/:tabs`}
          // path={`${BASE_ROUTE_PREFIX}/code-analysis/repos/:repoId?/projects/:projectId?/:tabs`}
          render={() => <Nav templates={templates} allSchemes={schemes} />}
        />
        <Redirect from={`${BASE_ROUTE_PREFIX}/code-analysis/project/repos/`} to={`${BASE_ROUTE_PREFIX}/code-analysis/project/repos/:repoId?/projects`} />
      </Switch>
    </div>
  );
};
export default Projects;
