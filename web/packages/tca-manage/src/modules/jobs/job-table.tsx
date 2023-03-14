import React from 'react';
import { t } from '@src/utils/i18n';
import { get } from 'lodash';
import { PaginationProps, Tag, Progress, Button, PrimaryTableCol, Space, Loading } from 'tdesign-react';
import Table from '@tencent/micro-frontend-shared/tdesign-component/table';
import { secToHMS, formatDateTime } from '@tencent/micro-frontend-shared/util/time';

// 项目内
import { ColumnOrgInfo } from '@plat/job';
import { getUserName } from '@src/utils';
import { getJobRouter } from '@plat/util';

// 模块内
import { STATE_CHOICES, StateEnum } from './constants';
import { JobData } from './types';

interface JobTableProps {
  loading: boolean;
  dataSource: JobData[];
  pagination: PaginationProps;
  archived?: boolean;
  cancelJob?: (jobInfo: JobData) => void;
}

const JobTable = ({ loading, dataSource, pagination, cancelJob, archived = false }: JobTableProps) => {
  const getColumns = () => {
    const columns: PrimaryTableCol<JobData>[] = [{
      colKey: 'job',
      title: t('分析任务'),
      width: 450,
      fixed: 'left',
      cell: ({ row }) => (<>
        <a
          className="link-name text-weight-bold"
          href={getJobRouter(row, archived)}
          target='_blank'
          rel="noopener noreferrer"
        >
          {row.project?.repo_scm_url}
        </a>
        <div className="mt-xs fs-12 text-grey-6">
          分支：{row.project?.branch} / 启动人：{getUserName(row.creator)} / 启动来源：{row.created_from}
        </div>
      </>),
    }, {
      colKey: 'task_num',
      title: t('执行进度'),
      width: 200,
      cell: ({ row }) => (
        <div style={{ minWidth: '150px' }}>
          <Progress
            color={{
              '0%': '#108ee9',
              '100%': '#87d068',
            }}
            percentage={row.task_num ? Math.floor((row.task_done / row.task_num) * 100) : 0}
          />
        </div>
      ),
    }, {
      colKey: 'state',
      title: t('执行状态'),
      width: 180,
      cell: ({ row }) => (
        <Space align='center'>
          {row.state !== StateEnum.CLOSED
            ? <Loading loading={true} text={STATE_CHOICES[row.state as StateEnum]} size="small" />
            : <span>{STATE_CHOICES[row.state as StateEnum]}</span>}
          {row.state !== StateEnum.CLOSED && <Button
            theme='danger' size='small'
            onClick={() => {
              cancelJob?.(row);
            }}
          >
            {t('取消任务')}
          </Button>}
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
      cell: ({ row }) => (
        <Space direction='vertical' size={4}>
          <div>等待：{secToHMS(row.waiting_time)}</div>
          <div>执行：{secToHMS(row.execute_time)}</div>
          <div>入库：{secToHMS(row.save_time)}</div>
        </Space>
      ),
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
    }, {
      colKey: 'created_from',
      title: t('启动渠道'),
      width: 160,
    }, {
      colKey: 'creator',
      title: t('启动人'),
      width: 160,
    }];
    // 配置额外的列
    ColumnOrgInfo && columns.splice(1, 0, ColumnOrgInfo);
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

export default JobTable;
