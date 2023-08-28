// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分析方案 - 已关联分支
 */
import React from 'react';
import { useRequest } from 'ahooks';
import { Link } from 'react-router-dom';

import { Avatar } from 'tdesign-react';

import { getBranchs } from '@src/services/schemes';

import Table from '@tencent/micro-frontend-shared/tdesign-component/table';
import { useURLParams } from '@tencent/micro-frontend-shared/hooks';
import { formatDateTime, getUserImgUrl } from '@src/utils';
import style from './style.scss';
import { getProjectRouter } from '@src/utils/getRoutePath';

interface BranchsProps {
  orgSid: string;
  teamName: string;
  repoId: number;
  schemeId: number;
}

const Branchs = (props: BranchsProps) => {
  const { orgSid, teamName, repoId, schemeId } = props;
  const { currentPage, pageSize, filter } = useURLParams();

  const { data = {}, loading } = useRequest(() => getBranchs(orgSid, teamName, repoId, schemeId, filter), {
    refreshDeps: [orgSid, teamName, repoId, schemeId, filter],
  });

  const columns = [
    {
      colKey: 'branch',
      title: '分支名称',
      cell: ({ row }: any) => (
        <Link
          className={style.linkName}
          to={`${getProjectRouter(orgSid, teamName, repoId, row.id)}/overview`}
        >
          {row.branch}
        </Link>
      ),
    },
    {
      colKey: 'creator',
      title: '创建人',
      cell: ({ row }: any) => {
        const { creator = '' } = row;
        const userinfo = row.creator_info
          ? row.creator_info
          : { uid: creator, nickname: creator };
        return (
          creator && (
            <>
              <Avatar
                size="small"
                image={userinfo.avatar_url || getUserImgUrl(userinfo.uid)}
                alt={userinfo.nickname}
              />
              <span className=" inline-block vertical-middle ml-sm">
                {userinfo.nickname}
              </span>
            </>
          )
        );
      },
    },
    {
      colKey: 'created_time',
      title: '创建时间',
      cell: ({ row }: any) => row.created_time && formatDateTime(row.created_time),
    },
  ];

  return (
    <Table
      rowKey='id'
      data={data.results || []}
      columns={columns}
      loading={loading}
      pagination={{
        current: currentPage,
        total: data.count || 0,
        pageSize,
      }}
    />
  );
};

export default Branchs;
