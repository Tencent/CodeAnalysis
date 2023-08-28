import React from 'react';
import { t } from '@src/utils/i18n';
import { get } from 'lodash';
import { PaginationProps, Tag, PrimaryTableCol, Space, Loading } from 'tdesign-react';
import Table from '@tencent/micro-frontend-shared/tdesign-component/table';
import { secToHMS, formatDateTime } from '@tencent/micro-frontend-shared/util/time';

// 模块内
import { getTaskRouter } from '@plat/util';
import { TASK_STATE_CHOICES, TaskStateEnum } from './constants';
import { TaskData } from './types';

interface TaskTableProps {
  loading: boolean;
  dataSource: TaskData[];
  pagination: PaginationProps;
  archived?: boolean;
}

const TaskTable = ({ loading, dataSource, pagination, archived = false }: TaskTableProps) => {
  const getColumns = () => {
    const columns: PrimaryTableCol<TaskData>[] = [{
      colKey: 'job.id',
      title: t('JobID'),
      width: 150,
      fixed: 'left',
      cell: ({ row }) => (<>
        <a
          className="link-name text-weight-bold"
          href={getTaskRouter(row.job, row.id, archived)}
          target='_blank'
          rel="noopener noreferrer"
        >
          {row.job.id} - {row.id}
        </a>
      </>),
    }, {
      colKey: 'task_name',
      title: t('执行任务'),
      width: 150,
      fixed: 'left',
    }, {
      colKey: 'state',
      title: t('执行状态'),
      width: 180,
      cell: ({ row }) => (
        <Space align='center'>
          {row.state !== TaskStateEnum.CLOSED
            ? <Loading loading={true} text={TASK_STATE_CHOICES[row.state as TaskStateEnum]} size="small" />
            : <span>{TASK_STATE_CHOICES[row.state as TaskStateEnum]}</span>}
        </Space>
      ),
    }, {
      colKey: 'result_msg',
      title: t('执行结果'),
      width: 300,
      cell: ({ row }) => (
        <>
          {row.result_code !== null && (
            <Tag theme={row.result_code < 100 ? 'success' : 'danger'} variant='light'>
              {row.result_code} {row.result_code_msg}
            </Tag>
          )}
          {row.result_msg && <div className="mt-xs fs-12 text-grey-6">{row.result_msg}</div>}
        </>
      ),
    }, {
      colKey: 'total_time',
      title: t('总耗时'),
      width: 220,
      cell: ({ row }) => secToHMS(row.total_time),
    }, {
      colKey: 'create_time',
      title: t('创建时间'),
      width: 200,
      cell: ({ row }: any) => (
        <div style={{ minWidth: '150px' }}>{formatDateTime(get(row, 'create_time'))}</div>
      ),
    }, {
      colKey: 'start_time',
      title: t('启动时间'),
      width: 200,
      cell: ({ row }: any) => (
        <div style={{ minWidth: '150px' }}>{formatDateTime(get(row, 'start_time'))}</div>
      ),
    }];
    return columns;
  };

  return (
    <Table
      loading={loading}
      data={dataSource}
      columns={getColumns()}
      pagination={pagination}
    />
  );
};

export default TaskTable;
