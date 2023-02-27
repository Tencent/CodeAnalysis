// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分析方案 - 已关联分支
 */
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import cn from 'classnames';
import moment from 'moment';

import { Table, Avatar } from 'coding-oa-uikit';
import UserIcon from 'coding-oa-uikit/lib/icon/User';

import { getBranchs } from '@src/services/schemes';
import { DEFAULT_PAGER } from '@src/constant';

import commonStyle from '../style.scss';
import style from './style.scss';
import { getUserImgUrl } from '@src/utils';
import { getProjectRouter } from '@src/utils/getRoutePath';

const { Column } = Table;

interface BranchsProps {
  orgSid: string;
  teamName: string;
  repoId: number;
  schemeId: number;
}

const Branchs = (props: BranchsProps) => {
  const { orgSid, teamName, repoId, schemeId } = props;
  const [list, setList] = useState<any>([]);
  const [pager, setPager] = useState(DEFAULT_PAGER);
  const { count, pageSize, pageStart } = pager;

  useEffect(() => {
    getListData(DEFAULT_PAGER.pageStart, DEFAULT_PAGER.pageSize);
  }, [schemeId]);

  const getListData = (offset: number, limit: number) => {
    getBranchs(orgSid, teamName, repoId, schemeId, { offset, limit }).then((response) => {
      setPager({
        pageSize: limit,
        pageStart: offset,
        count: response.count,
      });

      setList(response.results || []);
    });
  };

  const onChangePageSize = (page: number, pageSize: number) => {
    getListData((page - 1) * pageSize, pageSize);
  };

  const onShowSizeChange = (current: number, size: number) => {
    getListData(DEFAULT_PAGER.pageStart, size);
  };

  return (
    <Table
      size="small"
      dataSource={list}
      rowKey={(item: any) => item.id}
      className={cn(commonStyle.schemeTable, style.branchs)}
      pagination={{
        size: 'default',
        current: Math.floor(pageStart / pageSize) + 1,
        total: count,
        pageSize,
        showSizeChanger: true,
        showTotal: (total, range) => `${range[0]} - ${range[1]} 条，共 ${total} 条`,
        onChange: onChangePageSize,
        onShowSizeChange,
      }}
    >
      <Column
      title="分支名称"
      dataIndex="branch"
      key="branch"
      render={(branch: string, item: any) => (
        <Link
          className={style.linkName}
          to={`${getProjectRouter(orgSid, teamName, repoId, item.id)}/overview`}
        >
          {branch}
        </Link>
      )}
      />
      <Column
        title="创建人"
        dataIndex="creator"
        key="creator"
        render={(creator, project: any) => {
          const userinfo = project.creator_info
            ? project.creator_info
            : { uid: creator, nickname: creator };
          return (
            creator && (
              <>
                <Avatar
                  size="small"
                  src={userinfo.avatar_url || getUserImgUrl(userinfo.uid)}
                  alt={userinfo.nickname}
                  icon={<UserIcon />}
                />
                <span className=" inline-block vertical-middle ml-sm">
                  {userinfo.nickname}
                </span>
              </>
            )
          );
        }}
      />
      <Column
        title="创建时间"
        dataIndex="created_time"
        key="created_time"
        render={time => time && moment(time, 'YYYY-MM-DD HH:mm').format('YYYY-MM-DD HH:mm')}
      />
    </Table>
  );
};

export default Branchs;
