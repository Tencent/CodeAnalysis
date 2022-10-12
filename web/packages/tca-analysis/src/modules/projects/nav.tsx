// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分支项目公共导航栏
 */
import React, { useEffect, useState } from 'react';
import { useParams, useHistory, Route } from 'react-router-dom';
import { toNumber, get, find } from 'lodash';

import { Tabs, Button } from 'coding-oa-uikit';
import LinkIcon from 'coding-oa-uikit/lib/icon/Link';

import SelectDropdown from '@src/components/select-dropdown';
import { useStateStore } from '@src/context/store';
import { getProjectRouter, getSchemeBlankRouter } from '@src/utils/getRoutePath';
import { PROJECT_ROUTE_PREFIX } from '@src/constant';
import {
  getProjectDetail,
  getBranchs,
  getSchemesByBranch,
} from '@src/services/projects';

import ScanModal from './project/scan-modal';
import NewProjectModal from './project/new-project-modal';
import Issues from './issues';
import Overview from './overview';
import Metric from './metric';
import ScanHistory from './scan-history';

import style from './style.scss';

const { TabPane } = Tabs;

interface NavProps {
  allSchemes: any[];
  templates: any[];
}

const Nav = ({ allSchemes, templates }: NavProps) => {
  const params: any = useParams();
  const history = useHistory();
  const { curRepo } = useStateStore();

  const [curProject, setCurProject] = useState({}) as any;
  const [branchs, setBranchs] = useState([]);
  const [schemes, setSchemes] = useState([]);
  const [visible, setVisible] = useState(false);
  const [createProjectVsb, setCreateProjectVsb] = useState(false);

  const repoId = toNumber(params.repoId);
  const projectId = toNumber(params.projectId);
  const { orgSid, teamName } = params;
  let curTab = params.tabs;

  if (curTab === 'metric') {
    curTab = 'metric/ccfiles';
  }

  useEffect(() => {
    if (repoId && projectId) {
      getData();
    }
  }, [projectId]);

  const getData = async () => {
    const project = await getProjectDetail(orgSid, teamName, repoId, projectId);
    const branch = await getBranchs(orgSid, teamName, repoId);
    const scheme = await getSchemesByBranch(
      orgSid,
      teamName,
      repoId,
      project.branch,
    );

    setCurProject(project);
    setBranchs(branch.results || []);
    setSchemes(scheme);
  };

  const getBranchsData = (id: number) => {
    id
      && (async () => {
        setBranchs(get(await getBranchs(orgSid, teamName, id), 'results', []));
      })();
  };

  const getSchemes = (branch: string) => {
    branch
      && (async () => setSchemes(await getSchemesByBranch(orgSid, teamName, curRepo.id, branch)))();
  };

  const onChangeBranch = async (branch: any) => {
    const res = await getSchemesByBranch(orgSid, teamName, repoId, branch);
    const id = get(res, '[0].id');

    setSchemes(res);
    history.push(`${getProjectRouter(orgSid, teamName, repoId, id)}/overview`);
  };

  return (
    <div className={style.nav}>
      <div className={style.searchBar}>
        <div>
          <SelectDropdown
            showSearch
            label="代码分支"
            selectedKeys={[get(curProject, 'branch', '')]}
            dropdownStyle={{ marginRight: 10 }}
            selectedTextStyle={{ fontSize: '16px', fontWeight: 600 }}
            data={branchs.map((item: any) => ({
              value: item.branch,
              text: item.branch,
            }))}
            onSelect={(item: any) => {
              onChangeBranch(item.key);
            }}
          />
          <SelectDropdown
            showSearch
            label="分析方案"
            selectedKeys={[get(curProject, 'scan_scheme.name', '')]}
            dropdownStyle={{ marginRight: 10 }}
            selectedTextStyle={{ fontSize: '16px', fontWeight: 600 }}
            data={schemes.map((item: any) => ({
              value: item.scan_scheme__name,
              text: item.scan_scheme__name,
            }))}
            onSelect={(item: any) => {
              const id = find(schemes, { scan_scheme__name: item.key })?.id;
              history.push(`${getProjectRouter(orgSid, teamName, repoId, id)}/overview`);
            }}
          />
          <a
            target="_blank"
            href={`${getSchemeBlankRouter(
              orgSid,
              teamName,
              repoId,
              get(curProject, 'scan_scheme.id', ''),
            )}`} rel="noreferrer"
          >
            查看分析方案 <LinkIcon />
          </a>
        </div>

        <div className={style.operations}>
          <Button
            style={{ marginRight: 10 }}
            onClick={() => setCreateProjectVsb(true)}
          >
            新建分支项目
          </Button>
          <Button type="primary" onClick={() => setVisible(true)}>
            启动分析
          </Button>
        </div>
      </div>
      <Tabs
        activeKey={curTab || 'overview'}
        className={style.tabs}
        onChange={(key) => {
          history.push(`${getProjectRouter(
            orgSid,
            teamName,
            curRepo.id,
            projectId,
          )}/${key}`);
        }}
      >
        <TabPane forceRender={false} tab="分支概览" key="overview">
          <Overview
            orgSid={orgSid}
            teamName={teamName}
            repoId={repoId}
            projectId={projectId}
            curTab={curTab}
            schemeId={get(curProject, 'scan_scheme.id', null)}
          />
        </TabPane>
        <TabPane forceRender={false} tab="问题列表" key="codelint-issues">
          <Issues
            orgSid={orgSid}
            teamName={teamName}
            repoId={repoId}
            projectId={projectId}
            curTab={curTab}
            curScheme={curProject?.scan_scheme?.id}
          />
        </TabPane>
        <TabPane forceRender={false} tab="度量结果" key="metric/ccfiles">
          <Route
            exact
            path={`${PROJECT_ROUTE_PREFIX}/metric/:page`}
            render={() => (
              <Metric
                orgSid={orgSid}
                teamName={teamName}
                projectId={projectId}
                repoId={repoId}
              />
            )}
          />
        </TabPane>
        <TabPane forceRender={false} tab="分析历史" key="scan-history">
          <Route
            exact
            path={`${PROJECT_ROUTE_PREFIX}/scan-history`}
            render={() => (
              <ScanHistory
                orgSid={orgSid}
                teamName={teamName}
                repoId={repoId}
                projectId={projectId}
                curTab={curTab}
              />
            )}
          />
        </TabPane>
      </Tabs>
      <ScanModal
        visible={visible}
        orgSid={orgSid}
        teamName={teamName}
        repoId={repoId}
        projectId={projectId}
        onClose={() => setVisible(false)}
      />
      <NewProjectModal
        orgSid={orgSid}
        teamName={teamName}
        repoId={repoId}
        schemes={allSchemes}
        templates={templates}
        visible={createProjectVsb}
        onClose={() => setCreateProjectVsb(false)}
        callback={(branch: string) => {
          getBranchsData(repoId);
          getSchemes(branch);
        }}
      />
    </div>
  );
};
export default Nav;
