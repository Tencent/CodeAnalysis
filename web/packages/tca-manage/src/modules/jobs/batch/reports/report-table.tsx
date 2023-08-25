import React from 'react';
import { Link } from 'react-router-dom';
import { t } from '@src/utils/i18n';
import { get, round } from 'lodash';
import { PaginationProps, Progress, PrimaryTableCol, Space, Loading, Divider } from 'tdesign-react';
import Table from '@tencent/micro-frontend-shared/tdesign-component/table';
import { formatDateTime } from '@tencent/micro-frontend-shared/util/time';

// 项目内
import { getUserName } from '@src/utils';

// 模块内
import { BATCH_STATE_CHOICES, BatchStateEnum } from './constants';
import s from './style.scss';

interface JobTableProps {
  loading: boolean;
  dataSource: any[];
  pagination: PaginationProps;
}

const calTaskProgress = (taskInfo: any) => {
  if (!taskInfo) {
    return 0;
  }
  const taskNum = get(taskInfo, 'failed_num', 0) + get(taskInfo, 'success_num', 0) + get(taskInfo, 'running_num', 0);
  if (taskNum > 0) {
    return round(100 - (get(taskInfo, 'running_num', 0) / taskNum * 100));
  }
  return 0;
};

const JobDetail = (resultData: any) => {
  if (!resultData) {
    return '- -';
  }
  const { success_num: successNum = 0, failed_num: failedNum = 0, running_num: runningNum = 0 } = resultData || {};
  return (
    <Space className={s.jobResultSummary} align="center" separator={<Divider layout="vertical" />}>
      <div className={s.success}>
        {successNum}
        <p>{t('成功')}</p>
      </div>
      <div className={s.failed}>
        {failedNum}
        <p>{t('失败')}</p>
      </div>
      <div className={s.running}>
        {runningNum}
        <p>{t('执行中')}</p>
      </div>
    </Space>
  );
};

const JobTable = ({ loading, dataSource, pagination }: JobTableProps) => {
  const columns: PrimaryTableCol<any>[] = [{
    colKey: 'job',
    title: t('分析任务'),
    width: 300,
    fixed: 'left',
    cell: ({ row }) => (<>
      <Link
        className="link-name tca-text-weight-bold"
        to={`/manage/batch/reports/${row.report_id}`}
      >
        {row.name}
      </Link>
      <div className="tca-mt-xs tca-fs-12 tca-text-grey-6">
        {t('启动人：')}{getUserName(row.creator)} / {t('启动来源：')}{row.ext_data?.created_from}
      </div>
    </>),
  }, {
    colKey: 'state',
    title: t('任务状态'),
    width: 140,
    cell: ({ row }) => (
      <Space align='center'>
        {row.state !== BatchStateEnum.CLOSED
          ? <Loading loading={true} text={BATCH_STATE_CHOICES[row.state as BatchStateEnum]} size="small" />
          : <span>{BATCH_STATE_CHOICES[row.state as BatchStateEnum]}</span>}
      </Space>
    ),
  }, {
    colKey: 'result_msg',
    title: t('任务结果'),
    width: 280,
    cell: ({ row }) => JobDetail(row.result_data),
  }, {
    colKey: 'task_num',
    title: t('任务进度'),
    width: 200,
    cell: ({ row }) => (
      <div style={{ minWidth: '150px' }}>
        <Progress
          color={{
            '0%': '#108ee9',
            '100%': '#87d068',
          }}
          percentage={calTaskProgress(row.result_data)}
        />
      </div>
    ),
  }, {
    colKey: 'create_time',
    title: t('创建时间'),
    width: 200,
    cell: ({ row }: any) => (
      <div style={{ minWidth: '150px' }}>{formatDateTime(get(row, 'created_time'))}</div>
    ),
  }, {
    colKey: 'expired_time',
    title: t('过期时间'),
    width: 200,
    cell: ({ row }: any) => (
      <div style={{ minWidth: '150px' }}>{formatDateTime(get(row, 'expired_time'))}</div>
    ),
  }, {
    colKey: 'creator',
    title: t('启动人'),
    width: 160,
  }];

  return (
    <Table
      className={s.batchReportTable}
      loading={loading}
      data={dataSource}
      columns={columns}
      pagination={pagination}
    />
  );
};

export default JobTable;
