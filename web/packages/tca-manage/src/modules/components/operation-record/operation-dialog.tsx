import React from 'react';
import { Dialog } from 'tdesign-react';
import { t } from '@src/utils/i18n';
import OperationRecordTable from './operation-table';

type FetchApi<ApiArgs extends any[]> = (...args: ApiArgs) => Promise<unknown>;

interface OperationRecordDialogProps {
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

const OperationRecordDialog = ({ id, getRecordListApi, visible, onCancel }: OperationRecordDialogProps) => (
  <Dialog
    header={t('操作记录')}
    placement='top'
    visible={visible}
    onClose={onCancel}
    destroyOnClose
    footer={false}
    width='900px'
  >
    <OperationRecordTable
      id={id}
      getRecordListApi={getRecordListApi}
      rowKey='id'
      maxHeight='600px'
    />
  </Dialog>
);

export default OperationRecordDialog;
