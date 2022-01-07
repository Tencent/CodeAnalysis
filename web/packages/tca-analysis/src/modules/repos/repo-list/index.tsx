// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React from 'react';
import { useParams, useHistory } from 'react-router-dom';
import classnames from 'classnames';
import { Row, Col, Tabs, Button } from 'coding-oa-uikit';
import LoadingIcon from 'coding-oa-uikit/lib/icon/Loading';
import ExternalLinkIcon from 'coding-oa-uikit/lib/icon/ExternalLink';
import Copy from '@src/components/copy';
import { toNumber } from 'lodash';

// 项目内
import { getProjectRouter } from '@src/utils/getRoutePath';
import { t } from '@src/i18n/i18next';
import { useInitRepo } from '@src/modules/repos/hooks';
import LeftList from './left-list';
import Members from './tabs/members';
import Authority from './tabs/authority';
import Overview from './tabs/overview';
import s from './style.scss';
import { REPO_TAB_TYPE, REPO_TAB_TYPE_TXT } from '../constants';
import { getRepoRouter } from '../routes';

interface IProps {
  repos: Array<any>;
}

/**
 * 根据路由获取tab
 */
const getTabValue = () => {
  const url = window.location.href;
  if (url.indexOf(REPO_TAB_TYPE.MEMBER) > -1) {
    return REPO_TAB_TYPE.MEMBER;
  }
  if (url.indexOf(REPO_TAB_TYPE.AUTH) > -1) {
    return REPO_TAB_TYPE.AUTH;
  }
  if (url.indexOf(REPO_TAB_TYPE.OVERVIEW) > -1) {
    return REPO_TAB_TYPE.OVERVIEW;
  }
  return '';
};

const RepoList = ({ repos }: IProps) => {
  const params: any = useParams();
  const repoId = toNumber(params.repoId);
  const { org_sid: orgSid, team_name: teamName }: any = params;
  const history = useHistory();
  const { curRepo, curRepoMember } = useInitRepo(orgSid, teamName, repoId);
  const { admins = [], users = [] } = curRepoMember;
  const tabValue = getTabValue();

  // tab 切换跳转路由
  const onTabChange = (key: string) => {
    history.push(getRepoRouter(orgSid, teamName, repoId, key));
  };

  return (
        <Row className=" full-height">
            <LeftList repos={repos} />
            <Col flex="auto" className={classnames(s.rightContainer)}>
                {curRepo ? (
                    <>
                        <div className={s.header}>
                            <div className=" text-weight-medium fs-18">
                                {curRepo.name}
                                <Button
                                    className=" float-right"
                                    type="default"
                                    icon={<ExternalLinkIcon />}
                                    onClick={() => history.push(getProjectRouter(orgSid, teamName, repoId))}
                                >
                                    {t('代码分析')}
                                </Button>
                            </div>
                            <div className=" text-grey-6 mt-xs">
                                <span className="mr-xs">{curRepo.scm_url}</span>
                                <Copy text={curRepo.scm_url} copyText={curRepo.scm_url} />
                            </div>
                        </div>
                        <Tabs
                            activeKey={tabValue}
                            onChange={key => onTabChange(key)}
                            className={s.tabs}
                        >
                            <Tabs.TabPane tab={REPO_TAB_TYPE_TXT.MEMBER} key={REPO_TAB_TYPE.MEMBER}>
                                <Members
                                    orgSid={orgSid}
                                    teamName={teamName}
                                    repoId={repoId}
                                    admins={admins}
                                    users={users}
                                />
                            </Tabs.TabPane>
                            <Tabs.TabPane tab={REPO_TAB_TYPE_TXT.AUTH} key={REPO_TAB_TYPE.AUTH}>
                                <Authority
                                    orgSid={orgSid}
                                    teamName={teamName}
                                    repoId={repoId}
                                    curRepo={curRepo}
                                />
                            </Tabs.TabPane>
                            <Tabs.TabPane
                                tab={REPO_TAB_TYPE_TXT.OVERVIEW}
                                key={REPO_TAB_TYPE.OVERVIEW}
                            >
                                <Overview
                                    orgSid={orgSid}
                                    teamName={teamName}
                                    repoId={repoId}
                                    curRepo={curRepo}
                                />
                            </Tabs.TabPane>
                        </Tabs>
                    </>
                ) : (
                    <div className="text-center pa-sm fs-12">
                        <LoadingIcon />
                        <span className="ml-xs">{t('正在加载')}...</span>
                    </div>
                )}
            </Col>
        </Row>
  );
};

export default RepoList;
