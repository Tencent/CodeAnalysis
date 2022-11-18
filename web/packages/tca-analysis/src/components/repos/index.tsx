// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 代码库列表组件
 */

import React, { useState, useEffect } from 'react';
import cn from 'classnames';
import { useParams, Link } from 'react-router-dom';

import { isEmpty, find, toNumber } from 'lodash';

import { Dropdown, Menu, Input, Tooltip } from 'coding-oa-uikit';
import RepoIcon from 'coding-oa-uikit/lib/icon/Repos';
import CaretDown from 'coding-oa-uikit/lib/icon/CaretDown';
import LinkIcon from 'coding-oa-uikit/lib/icon/Link';
import ConfigIcon from 'coding-oa-uikit/lib/icon/Cog';

import Copy from '@tencent/micro-frontend-shared/component/copy';
import { getRepoName } from '@tencent/micro-frontend-shared/tca/util';
import { getRepos } from '@src/services/common';
import { getReposRouter } from '@src/utils/getRoutePath';
import { useStateStore, useDispatchStore } from '@src/context/store';
import { SET_CUR_REPO } from '@src/context/constant';
import style from './style.scss';

interface IProps {
  orgSid?: string;
  teamName?: string;
  callback: (id: number) => void;
}

const Repos = (props: IProps) => {
  const { repoId } = useParams<any>();
  const { orgSid, teamName, callback } = props;
  const { curRepo, repos } = useStateStore();
  const dispatch = useDispatchStore();

  const [visible, setVisible] = useState(false);
  const [searchValue, onChangeSearchValue] = useState('');
  const [searchRepos, setSearchRepos] = useState([]);

  useEffect(() => {
    if (repoId && toNumber(repoId) !== curRepo.id) {
      const repo = find(repos, { id: toNumber(repoId) });
      if (repo) {
        dispatch({
          type: SET_CUR_REPO,
          payload: repo,
        });
      } else {
        // message.error('代码库不存在');
      }
    }
  }, [repoId]);

  const handleVisibleChange = (flag: boolean) => {
    setVisible(flag);
  };

  const handleMenuClick = (e: any) => {
    if (e.key !== 'search') {
      setVisible(false);
    }

    let repo = find(repos, { id: toNumber(e.key) });

    if (!repo) {
      repo = find(searchRepos, { id: toNumber(e.key) });
    }
    onChangeRepo(repo);
  };

  const onSearch = (value: string) => {
    onChangeSearchValue(value);
    getRepos(orgSid, teamName, {
      scope: 'related_me',
      scm_url_or_name: value,
      limit: 10,
      offset: 0,
    }).then((res) => {
      setSearchRepos(res.results || []);
    });
  };

  const onChangeRepo = (repo: any) => {
    if (!isEmpty(repo)) {
      dispatch({
        type: 'SET_CUR_REPO',
        payload: repo,
      });
      callback(repo);
    }
  };

  const renderRepoItem = () => {
    const repoList = searchValue ? searchRepos : repos;
    return repoList.map(item => (
      <Menu.Item key={item.id}>
        <RepoIcon className={cn(style.gitMark, style.repoListIcon)} />
        {getRepoName(item)}
      </Menu.Item>
    ));
  };

  return (
    <div className={style.reposContainer}>
      <div className={style.repoUrlContainer}>
        <Dropdown
          visible={visible}
          onVisibleChange={handleVisibleChange}
          overlay={
            <Menu
              onClick={handleMenuClick}
              selectedKeys={[`${curRepo.id}`]}
            >
              <Menu.Item key='search'>
                <Input.Search
                  size='middle'
                  allowClear
                  placeholder='代码库筛选'
                  onSearch={(value: string) => {
                    onSearch(value);
                  }}
                />
              </Menu.Item>
              {renderRepoItem()}
            </Menu>
          }>
          <div className={style.curRepo}>
            <RepoIcon className={style.gitMark} />
            <span className={style.repoUrl}>{getRepoName(curRepo)}</span>
            <CaretDown className={style.icon} />
          </div>
        </Dropdown>
        <Copy text={`点击复制代码库ID：${curRepo.id}`} copyText={curRepo.id}/>
        {/* <Copy text={curRepo.scm_url} className={style.copyIcon} /> */}
        <Tooltip title={<div style={{ wordBreak: 'break-all' }}>跳转代码库: {curRepo.scm_url}</div>}>
          <a className={style.repoLink} target="_blank" href={curRepo.scm_url} rel="noreferrer">
            <LinkIcon />
          </a>
        </Tooltip>
        <Tooltip title='仓库设置'>
          <Link className={style.repoLink} to={`${getReposRouter(orgSid, teamName)}/${curRepo.id}`}>
            <ConfigIcon />
          </Link>
        </Tooltip>
      </div>
    </div>
  );
};

export default Repos;
