// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 代码库列表组件
 */

import React, { useState } from 'react';
import cn from 'classnames';
import { isEmpty, find, toNumber } from 'lodash';

import { Dropdown, Menu, Input } from 'coding-oa-uikit';
import RepoIcon from 'coding-oa-uikit/lib/icon/Repos';
import CaretDown from 'coding-oa-uikit/lib/icon/CaretDown';
import Link from 'coding-oa-uikit/lib/icon/Link';


import Copy from '@src/components/copy';
import { useStateStore, useDispatchStore } from '@src/context/store';

import style from './style.scss';

interface IProps {
  orgSid?: string;
  teamName?: string;
  callback: (id: number) => void;
}

const Repos = (props: IProps) => {
  const { callback } = props;
  const { curRepo, repos } = useStateStore();
  const dispatch = useDispatchStore();

  const [visible, setVisible] = useState(false);
  const [searchValue, onChangeSearchValue] = useState('');

  const handleVisibleChange = (flag: boolean) => {
    setVisible(flag);
  };

  const handleMenuClick = (e: any) => {
    if (e.key !== 'search') {
      setVisible(false);
    }

    const repo = find(repos, { id: toNumber(e.key) });
    onChangeRepo(repo);
  };

  const onSearch = (value: string) => {
    onChangeSearchValue(value);
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
                  onChange={(e: any) => {
                    onSearch(e.target.value);
                  }}
                />
              </Menu.Item>
              {
                repos
                  .filter((item: any) => item.name?.toLowerCase().includes(searchValue.toLowerCase()))
                  .map((item: any) => (
                    <Menu.Item key={item.id}>
                      <RepoIcon className={cn(style.gitMark, style.repoListIcon)} />
                      {item.name}
                    </Menu.Item>
                  ))
              }
            </Menu>
          }>
          <div className={style.curRepo}>
            <RepoIcon className={style.gitMark} />
            <span className={style.repoUrl}>{curRepo.scm_url}</span>
            <CaretDown className={style.icon} />
          </div>
        </Dropdown>
        <Copy text={curRepo.scm_url} className={style.copyIcon} />
        <a className={style.repoLink} target="_blank" href={curRepo.scm_url} rel="noreferrer">
          <Link />
        </a>
      </div>
    </div>
  );
};

export default Repos;
