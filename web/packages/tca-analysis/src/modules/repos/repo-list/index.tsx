// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useState } from 'react';
import { useParams, useHistory } from 'react-router-dom';
import classnames from 'classnames';
import { Row, Col, Tabs, Button, message } from 'coding-oa-uikit';
import LoadingIcon from 'coding-oa-uikit/lib/icon/Loading';
import ExternalLinkIcon from 'coding-oa-uikit/lib/icon/ExternalLink';
import Copy from '@src/components/copy';
import { toNumber, get, find, remove, isEmpty } from 'lodash';
import { useSelector } from 'react-redux';

// 项目内
import { SET_REPOS } from '@src/context/constant';
import { useDispatchStore } from '@src/context/store';
import { getProjectRouter, getReposRouter } from '@src/utils/getRoutePath';
import { delRepo } from '@src/services/repos';
import { t } from '@src/i18n/i18next';
import { useInitRepo } from '@src/modules/repos/hooks';
import LeftList from './left-list';
import Members from './tabs/members';
import Authority from './tabs/authority';
import Overview from './tabs/overview';
import s from './style.scss';
import { REPO_TAB_TYPE, REPO_TAB_TYPE_TXT } from '../constants';
import { getRepoRouter } from '../routes';
import DeleteModal from '@src/components/delete-modal';

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
  const dispatch = useDispatchStore();
  const { curRepo, curRepoMember } = useInitRepo(orgSid, teamName, repoId);
  const { admins = [], users = [] } = curRepoMember;
  const tabValue = getTabValue();
  // 判断是否有权限删除代码库
  const APP = useSelector((state: any) => state.APP);
  const isSuperuser = get(APP, 'user.is_superuser', false); // 当前用户是否是超级管理员
  const userName = get(APP, 'user.username', null);
  const isAdmin = !!find(admins, { username: userName });  // 当前用户是否是代码库管理员
  const deletable = isAdmin || isSuperuser;  // 删除权限
  const [deleteVisible, setDeleteVisible] = useState<boolean>(false);

  // tab 切换跳转路由
  const onTabChange = (key: string) => {
    history.push(getRepoRouter(orgSid, teamName, repoId, key));
  };

  const onDeleteRepo = () => {
    setDeleteVisible(true);
  };
  
  const handleDeleteRepo = () => {
    delRepo(orgSid, teamName, repoId).then(() => {
      message.success('已删除代码库');
      remove(repos, (item: any) => item?.id === repoId);
      const firstRepoId = isEmpty(repos) ? null : repos[0].id;
      dispatch({
        type: SET_REPOS,
        payload: repos,
      });
      if (firstRepoId) {
        history.push(getRepoRouter(orgSid, teamName, firstRepoId));
      } else {
        history.push(getReposRouter(orgSid, teamName));
      }
    }).finally(() => {
      setDeleteVisible(false);
    });
  };

  return (
    <Row className=" full-height">
      <DeleteModal
        deleteType={t('代码库')}
        confirmName={curRepo?.name}
        visible={deleteVisible}
        onCancel={() => setDeleteVisible(false)}
        onOk={handleDeleteRepo}
      />
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
                  deletable={deletable}
                  onDelete={onDeleteRepo}
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
