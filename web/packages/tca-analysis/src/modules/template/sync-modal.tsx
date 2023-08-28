// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 同步操作
 */

import React, { useEffect, useState } from 'react';
import { useRequest } from 'ahooks';
import { useParams } from 'react-router-dom';
import { Table, Dialog, PrimaryTableCol } from 'tdesign-react';
import { get } from 'lodash';

import { DEFAULT_PAGER } from '@src/constant';
import { getSchemeList } from '@src/services/template';

interface SyncModalProps {
  onlySync?: boolean;
  tmplId: number;
  visible: boolean;
  onClose: () => void;
  onOk: (keys: any) => void;
}

const SyncModal = (props: SyncModalProps) => {
  const { orgSid } = useParams() as any;
  const { onlySync, visible, tmplId, onClose, onOk } = props;

  const [selectedRowKeys, setSelectedRowKeys] = useState<any>([]);
  const [pager, setPager] = useState<any>(DEFAULT_PAGER);
  const { pageSize, current } = pager;

  const { data, loading } = useRequest(getSchemeList, {
    defaultParams: [orgSid, tmplId, {
      offset: (current - 1) * pageSize,
      limit: pageSize,
    }],
    refreshDeps: [orgSid, tmplId, pager],
  });

  useEffect(() => {
    if (visible) {
      setSelectedRowKeys([]);
    }
  }, [visible]);

  const columns: PrimaryTableCol<any>[] = [
    {
      colKey: 'row-select',
      type: 'multiple',
      width: 50,
    },
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
    <Dialog
      header={`${onlySync ? '' : '保存 & '}同步`}
      width={800}
      visible={visible}
      onClose={onClose}
      onConfirm={() => onOk(selectedRowKeys)}
    >
      <p style={{ marginBottom: 10 }}>
        当前模板下存在以下分析方案，请勾选需要同步的分析方案
        {!onlySync && '；若不勾选，则只修改模板，不进行同步操作'}
      </p>
      <Table
        size='small'
        data={data?.results || []}
        rowKey='id'
        columns={columns}
        loading={loading}
        selectedRowKeys={selectedRowKeys}
        onSelectChange={setSelectedRowKeys}
        pagination={{
          current,
          total: data?.count || 0,
          pageSize,
          onChange: setPager,
        }}
      />
    </Dialog>
  );
};

export default SyncModal;
