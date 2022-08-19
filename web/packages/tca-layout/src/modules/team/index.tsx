// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 所有团队
 */

import React, { useEffect, useState } from 'react';
import ReactDOM from 'react-dom';
import { useHistory } from 'react-router-dom';
import { get, isEmpty, concat } from 'lodash';

import { Tabs, Input, Button, Avatar, Badge, Tooltip, Divider, Spin } from 'coding-oa-uikit';
import { t } from '@src/i18n/i18next';
import { formatDateTime } from '@src/utils';

import Header from '@src/modules/layout/header';
import { getTeams } from '@src/services/team';
import {
  STATUS_ENUM,
  APPLY_STATUS_ENUM,
  APPLY_STATUS_CHOICES,
  CHECK_RESULT_ENUM,
  CHECK_RESULT_CHOICES,
} from '@src/constants/org';
import CreateTeam from './create-team';

import style from './style.scss';

const { Search } = Input;
const DEFAULT_PAGER = {
  count: 0,
  pageSize: 12,
  pageStart: 0,
  allLoaded: true,
};

const Team = () => {
  const history = useHistory();
  const [name, setName] = useState('');
  const [list, setList] = useState([]);
  const [pager, setPager] = useState(DEFAULT_PAGER);
  const [visible, setVisible] = useState(false);
  const [data, setData] = useState();
  const [scrollLoading, setScrollLoading] = useState(true);
  const { count, pageStart, allLoaded } = pager;

  const INIT_LOAD_SIZE = 50;
  const containerNode = document.getElementById('container');

  useEffect(() => {
    getTeamList(false, DEFAULT_PAGER.pageStart, INIT_LOAD_SIZE, {}, (list: any) => {
      // 用户进入团队页面，如果不存在团队，则默认弹出创建团队弹框
      if (isEmpty(list)) {
        setVisible(true);
      }
    });
  }, []);

  const getTeamList = async (
    scroll = false,
    offset = pageStart,
    limit = DEFAULT_PAGER.pageSize,
    searchParams = {},
    callback?: (...args: any[]) => any,
  ) => {
    const res = (await getTeams({ offset, limit, ...searchParams })) || {};
    setScrollLoading(false);
    setPager({
      pageSize: limit,
      pageStart: offset + limit,
      count: res.count,
      allLoaded: offset + limit >= res.count,
    });
    if (scroll) {
      setList(concat(list, res.results || []));
    } else {
      setList(res.results || []);
    }
    callback?.(res.results);
  };

  const onSearch = (value: string) => {
    getTeamList(false, DEFAULT_PAGER.pageStart, count, {
      name: value,
    });
  };

  // 滚动加载更多团队
  const loadMoreTeam = () => {
    const teamWrapper = document.getElementById('team-wrapper');
    if (teamWrapper.scrollTop + teamWrapper.clientHeight > teamWrapper.scrollHeight * 0.8 && !allLoaded && !scrollLoading) {
      setScrollLoading(true);
      getTeamList(true);
    }
  };

  const onClickTeam = (data: any) => {
    if (data.status === 2) {
      setData({
        ...data,
        apply_msg: data.last_perm_apply?.apply_msg ?? '',
      });
      setVisible(true);
    } else {
      if (data.repo_count) {
        // 存在分析任务则进入工作台
        history.push(`/t/${data.org_sid}/workspace`);
      } else {
        history.push({
          pathname: `/t/${data.org_sid}/projects`,
          state: {
            // 用户从团队进入项目，如果不存在项目则默认弹出创建项目弹框
            visible: !data.team_count,
          },
        });
      }
    }
  };

  const onCreateFinish = () => {
    setPager(DEFAULT_PAGER);
    getTeamList(false, DEFAULT_PAGER.pageStart, INIT_LOAD_SIZE, {});
  }

  return (
    <>
      <Header />
      {containerNode && ReactDOM.createPortal(
        <div className={style.teamContainer}>
          <Tabs
            defaultActiveKey="all"
            size="large"
            tabBarExtraContent={
              <>
                <Search
                  allowClear
                  defaultValue={name}
                  value={name}
                  size="middle"
                  placeholder={t('团队名称')}
                  onChange={e => setName(e.target.value)}
                  onSearch={value => onSearch(value)}
                  style={{ width: 200 }}
                />
                <Button
                  className="ml-md"
                  type="primary"
                  onClick={() => {
                    setVisible(true);
                    setData(undefined);
                  }}
                >
                  {t('创建团队')}
                </Button>
              </>
            }
          >
            <Tabs.TabPane tab={t('所有团队')} key="all">
              <div
                className={style.teamWrapper}
                id='team-wrapper'
                onScroll={loadMoreTeam}
              >
                {list.map((item: any) => (
                  <div
                    key={item.id}
                    className={style.team}
                    onClick={() => onClickTeam(item)}
                  >
                    <TeamItem data={item} />
                  </div>
                ))}
                <div style={{ textAlign: 'center' }}><Spin spinning={scrollLoading} /></div>
              </div>
              {!allLoaded && <Divider plain>滚动加载更多团队</Divider>}
            </Tabs.TabPane>
          </Tabs>
          <CreateTeam
            visible={visible}
            data={data}
            onHide={() => setVisible(false)}
            callback={onCreateFinish}
          />
        </div>, containerNode
      )}
    </>
  );
};

interface FormatCardProps {
  item: any;
  children: React.ReactNode;
}

const FormatCard = ({ item, children }: FormatCardProps) => {
  if (item.status > STATUS_ENUM.ACTIVE) {
    const status = get(item, 'last_perm_apply.status') || APPLY_STATUS_ENUM.CHECKED;
    const remark = get(item, 'last_perm_apply.check_remark') || t('团队信息审核失败');
    const badgeInfo = {
      color: '#eb333f', // red-5
      text: CHECK_RESULT_CHOICES[CHECK_RESULT_ENUM.NO_PASS],
      remark,
    };
    if (status === APPLY_STATUS_ENUM.CHECKING) {
      // 申请中
      badgeInfo.color = ''; // 默认
      badgeInfo.text = APPLY_STATUS_CHOICES[APPLY_STATUS_ENUM.CHECKING];
      badgeInfo.remark = t('平台会在1-2个工作日内完成审核，请稍候');
    } else if (status === APPLY_STATUS_ENUM.CANCELED) {
      // 取消申请
      badgeInfo.text = APPLY_STATUS_CHOICES[APPLY_STATUS_ENUM.CANCELED];
    }
    return (
      <Badge.Ribbon
        color={badgeInfo.color}
        text={
          <Tooltip placement="topLeft" color={badgeInfo.color} title={badgeInfo.remark}>
            {badgeInfo.text}
          </Tooltip>
        }
      >
        {children}
      </Badge.Ribbon>
    );
  }
  return <>{children}</>;
};

const TeamItem = (props: any) => {
  const { data } = props;
  return (
    <FormatCard item={data}>
      <div className={style.item}>
        <Avatar size="large" style={{ backgroundColor: '#adbacc' }}>
          {data?.name[0]}
        </Avatar>
        <div className={style.content}>
          <h3>{data.name}</h3>
          <p className={style.time}>创建于：{formatDateTime(data.created_time)}</p>
        </div>
      </div>
    </FormatCard>
  );
};

export default Team;
