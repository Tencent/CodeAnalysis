import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { t } from '@src/utils/i18n';
import { get } from 'lodash';
import { PaginationProps, PrimaryTableCol, Space, Button, Tag, TdTagProps, Popconfirm, Checkbox, message } from 'tdesign-react';
import { LoadingIcon, InfoCircleIcon, CheckCircleIcon } from 'tdesign-icons-react';

import Table from '@tencent/micro-frontend-shared/tdesign-component/table';
import { formatDateTime, formatDate } from '@tencent/micro-frontend-shared/util/time';

// 项目内
import { getUserName } from '@src/utils';
import { postMergeTrendReport } from '@src/services/batchjobs';

// 模块内
import { REPORT_STATE_CHOICES, ReportStateEnum } from './constants';

interface JobTableProps {
  loading: boolean;
  dataSource: any[];
  pagination: PaginationProps;
}

const JobTable = ({ loading, dataSource, pagination }: JobTableProps) => {
  const [forceMerge, setForceMerge] = useState(false);

  const onConfirmMergeReport = (row: any) => {
    postMergeTrendReport(row.report_id, forceMerge).then(({ msg }) => {
      message.success(msg);
    });
  };
  const columns: PrimaryTableCol<any>[] = [{
    colKey: 'job',
    title: t('分析任务'),
    width: 300,
    fixed: 'left',
    cell: ({ row }) => (<>
      <Link
        className="link-name tca-text-weight-bold"
        to={`/manage/batch/trendreports/${row.report_id}`}
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
    width: 300,
    cell: ({ row }) => {
      let params: [TdTagProps['theme'], React.ReactElement] = ['default', undefined];
      if (row.state < ReportStateEnum.CLOSED) {
        params = ['primary', <LoadingIcon key={row.state} />];
      } else if (row.state === ReportStateEnum.STOPPED) {
        params = ['danger', <InfoCircleIcon key={row.state} />];
      }
      if (row.state === ReportStateEnum.CLOSED) {
        params = ['success', <CheckCircleIcon key={row.state} />];
      }
      const [theme, icon] = params;
      return <>
        <Tag variant="light" theme={theme} icon={icon}>{REPORT_STATE_CHOICES[row.state as ReportStateEnum]}</Tag>
        {row.result_msg && <p className='tca-mt-sm tca-fs-12'>{row.result_msg}</p>}
      </>;
    },
  }, {
    colKey: 'job_num',
    title: t('任务量'),
  }, {
    colKey: 'ext_data.start_date',
    title: t('度量区间'),
    width: 220,
    cell: ({ row }: any) => <>
      {formatDate(get(row, 'ext_data.start_date'))} - {formatDate(get(row, 'ext_data.end_date'))}
    </>,
  }, {
    colKey: 'ext_data.scheme_id',
    title: t('方案ID'),
  }, {
    colKey: 'create_time',
    title: t('创建时间'),
    width: 200,
    cell: ({ row }: any) => (
      <div style={{ minWidth: '150px' }}>{formatDateTime(get(row, 'created_time'))}</div>
    ),
  }, {
    colKey: 'creator',
    title: t('启动人'),
    width: 80,
  }, {
    colKey: 'op',
    title: t('操作'),
    width: 120,
    cell: ({ row }) => (
      <Space size={4}>
        <Popconfirm placement='left' onVisibleChange={(v) => {
          if (v) {
            setForceMerge(false);
          }
        }} onConfirm={() => {
          onConfirmMergeReport(row);
        }} content={<>
          <p style={{ width: 200 }} className='tca-text-weight-medium'>确定合并报告？</p>
          <p className='tca-mt-md'><Checkbox value={forceMerge}>强制合并</Checkbox></p>
        </>} showArrow>
          <Button theme='primary' variant='text' disabled={row.state === ReportStateEnum.CLOSEING}>合并报告</Button>
        </Popconfirm>
      </Space>
    ),
  }];

  return (
    <Table
      loading={loading}
      data={dataSource}
      columns={columns}
      pagination={pagination}
    />
  );
};

export default JobTable;
