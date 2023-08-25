import React from 'react';
import { t } from '@src/utils/i18n';
import { get } from 'lodash';
import { PaginationProps, Tag, PrimaryTableCol, Space, Loading } from 'tdesign-react';
import Table from '@tencent/micro-frontend-shared/tdesign-component/table';
import { formatDateTime } from '@tencent/micro-frontend-shared/util/time';

// 项目内
import { ColumnOrgInfo } from '@plat/job';
import { getJobRouterByParams } from '@plat/util';

// 模块内
import { STATE_CHOICES, StateEnum } from '@src/modules/jobs/constants';

interface JobTableProps {
  loading: boolean;
  dataSource: any[];
  pagination: PaginationProps;
}

const JobTable = ({ loading, dataSource, pagination }: JobTableProps) => {
  const getColumns = () => {
    const columns: PrimaryTableCol<any>[] = [{
      colKey: 'job.project',
      title: t('分析任务'),
      width: 450,
      fixed: 'left',
      cell: ({ row }) => (<>
        <a
          className="link-name text-weight-bold"
          href={getJobRouterByParams(row.job.project.repo, row.job.project.id, row.job.id, row.job.archived)}
          target='_blank'
          rel="noopener noreferrer"
        >
          {row.job.project.repo_scm_url}
        </a>
        <div className="tca-mt-xs tca-fs-12 tca-text-grey-6">
          {t('分支：')}{row.job.project.branch} / {t('区间：')}{row.start_date} - {row.end_date}
        </div>
      </>),
    }, {
      colKey: 'job.state',
      title: t('执行状态'),
      width: 160,
      cell: ({ row }) => (
        <Space align='center'>
          {row.job.state !== StateEnum.CLOSED
            ? <Loading loading={true} text={STATE_CHOICES[row.job.state as StateEnum]} size="small" />
            : <span>{STATE_CHOICES[row.job.state as StateEnum]}</span>}
        </Space>
      ),
    }, {
      colKey: 'result_msg',
      title: t('执行结果'),
      width: 300,
      cell: ({ row }) => (
        <>
          {row.job.result_code !== null ? (
            <Tag theme={row.job.result_code < 100 ? 'success' : 'danger'} variant='light'>
              {row.job.result_code.toString()} {row.job.result_code_msg}
            </Tag>
          ) : '- -'}
          {row.job.result_msg && <div className="tca0mt-xs tca-fs-12 tca-text-grey-6">{row.job.result_msg}</div>}
        </>
      ),
    }, {
      colKey: 'create_time',
      title: t('创建时间'),
      width: 200,
      cell: ({ row }: any) => (
        <div style={{ minWidth: '150px' }}>{formatDateTime(get(row, 'job.create_time'))}</div>
      ),
    }, {
      colKey: 'start_time',
      title: t('完成时间'),
      width: 200,
      cell: ({ row }: any) => (
        <div style={{ minWidth: '150px' }}>{formatDateTime(get(row, 'job.end_time')) || '- -'}</div>
      ),
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
