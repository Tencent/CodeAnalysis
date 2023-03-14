import React, { useEffect, useState } from 'react';
import { get } from 'lodash';
import { Dialog, PageInfo, Table } from 'tdesign-react';
import { t } from '@src/utils/i18n';
import { formatDateTime } from '@tencent/micro-frontend-shared/util';

type FetchApi<ApiArgs extends any[]> = (...args: ApiArgs) => Promise<unknown>;

interface OperationRecordModalProps {
  id: number | string;
  visible: boolean;
  getRecordListApi: FetchApi<any>;
  onCancel: () => void;
}

export const DEFAULT_PAGER = {
  count: 0,
  pageSize: 10,
  currentPage: 1,
};

const OperationRecordModal = ({ id, getRecordListApi, visible, onCancel }: OperationRecordModalProps) => {
  const [operationRecord, setOperationRecord] = useState<any>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [pager, setPager] = useState<any>(DEFAULT_PAGER);
  const { count, pageSize, currentPage } = pager;

  useEffect(() => {
    if (visible && id) {
      setLoading(true);
      getRecordList(DEFAULT_PAGER.currentPage, DEFAULT_PAGER.pageSize);
    }
  }, [visible]);

  const getRecordList = (page: number, pageSize: number) => {
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
  };

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
    <Dialog
      header={t('操作记录')}
      placement='top'
      visible={visible}
      onClose={onCancel}
      onClosed={() => setOperationRecord([])}
      footer={null}
      width='900px'
    >
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
        maxHeight='600px'
        size='small'
        rowKey='id'
      />
    </Dialog>
  );
};

export default OperationRecordModal;
