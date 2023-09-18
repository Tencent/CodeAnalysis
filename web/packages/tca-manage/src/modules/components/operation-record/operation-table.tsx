import React, { useEffect, useState, useCallback } from 'react';
import { get } from 'lodash';
import { PageInfo, Table, PrimaryTableProps } from 'tdesign-react';
import { t } from '@src/utils/i18n';
import { formatDateTime } from '@tencent/micro-frontend-shared/util';

type FetchApi<ApiArgs extends any[]> = (...args: ApiArgs) => Promise<unknown>;

interface OperationRecordTableProps extends PrimaryTableProps {
  id: number | string;
  getRecordListApi: FetchApi<any>;
}

export const DEFAULT_PAGER = {
  count: 0,
  pageSize: 10,
  currentPage: 1,
};

const OperationRecordTable = ({ id, getRecordListApi, ...otherProps }: OperationRecordTableProps) => {
  const [operationRecord, setOperationRecord] = useState<any>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [pager, setPager] = useState<any>(DEFAULT_PAGER);
  const { count, pageSize, currentPage } = pager;

  const getRecordList = useCallback((page: number, pageSize: number) => {
    getRecordListApi(id, {
      limit: pageSize,
      offset: (page - 1) * pageSize,
    }).then((res: any) => {
      setOperationRecord(res.results);
      setPager({
        count: res.count,
        pageSize,
        currentPage: page,
      });
      setLoading(false);
    });
  }, [getRecordListApi, id]);

  useEffect(() => {
    if (id) {
      setLoading(true);
      getRecordList(DEFAULT_PAGER.currentPage, DEFAULT_PAGER.pageSize);
    }
  }, [id, getRecordList]);

  const onChangePage = ({ current, pageSize }: PageInfo) => {
    setLoading(true);
    getRecordList(current, pageSize);
  };

  const columns = [
    {
      colKey: 'creator',
      title: t('操作人'),
      width: 100,
    },
    {
      colKey: 'action',
      title: t('操作类型'),
      width: 120,
    },
    {
      colKey: 'message',
      title: t('详情'),
      width: 400,
      cell: ({ row }: any) => (
        <div style={{ wordWrap: 'break-word', wordBreak: 'break-word' }}>
          {get(row, 'message')}
        </div>
      ),
    },
    {
      colKey: 'created_time',
      title: t('操作时间'),
      width: 150,
      cell: ({ row }: any) => formatDateTime(get(row, 'created_time')) || '- -',
    },
  ];

  return (
    <Table
      data={operationRecord}
      loading={loading}
      columns={columns}
      pagination={{
        current: currentPage,
        total: count,
        pageSize,
        onChange: onChangePage,
      }}
      size='small'
      rowKey='id'
      {...otherProps}
    />
  );
};

export default OperationRecordTable;
