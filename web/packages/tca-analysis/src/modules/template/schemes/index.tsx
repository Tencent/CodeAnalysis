// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 模板生成的分析方案列表
 */

import React from 'react';
import { useRequest } from 'ahooks';
import { get } from 'lodash';

import Table from '@tencent/micro-frontend-shared/tdesign-component/table';
import { getSchemeList } from '@src/services/template';
import { useURLParams } from '@tencent/micro-frontend-shared/hooks';

interface SchemeListProps {
  orgSid: string;
  tmplId: number;
}

const SchemeList = (props: SchemeListProps) => {
  const { orgSid, tmplId } = props;
  const { currentPage, pageSize, filter } = useURLParams();

  const { data = {}, loading } = useRequest(() => getSchemeList(orgSid, tmplId, filter), {
    refreshDeps: [orgSid, tmplId, filter],
  });

  const columns = [
    {
      colKey: 'name',
      title: '分析方案名称',
      cell: ({ row }: any) => (row.name),
    },
    {
      colKey: 'repo',
      title: '所属代码库',
      cell: ({ row }: any) => (
        <a
          className='link-name'
          target='_blank'
          href={get(row, 'repo.scm_url')}
          rel="noreferrer"
        >
          {get(row, 'repo.scm_url')}
        </a>
      ),
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

export default SchemeList;
