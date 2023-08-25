import React, { useEffect, useState } from 'react';
import { useParams, useHistory } from 'react-router-dom';
import { Space, Button } from 'tdesign-react';
import { useURLParams, useFetch } from '@tencent/micro-frontend-shared/hooks';
import { ArrowLeftIcon } from 'tdesign-icons-react';

// 项目内
import { t } from '@src/utils/i18n';
import { getTrendReportJobs, getTrendReport } from '@src/services/batchjobs';

// 模块内
import JobTable from './job-table';
import PageHeader from '@tencent/micro-frontend-shared/tdesign-component/page-header';

const ArchivedJobs = () => {
  const { reportId }: any = useParams();
  const history = useHistory();
  const [reportInfo, setReportInfo] = useState<any>({});
  const { filter, currentPage, pageSize } = useURLParams();
  const [{ data, isLoading }] = useFetch(getTrendReportJobs, [reportId, { ...filter }]);
  const { results: listData = [], count = 0 } = data || {};

  useEffect(() => {
    getTrendReport(reportId).then((res: any) => {
      setReportInfo(res);
    });
  }, [reportId]);

  return (
    <>
      <PageHeader title={
        <Space align='center' size={8}>
          <Button icon={<ArrowLeftIcon />} shape='circle' onClick={() => history.push('/manage/batch/trendreports')} />
          <span>{reportInfo?.name} {t('任务详情')}</span>
        </Space>
      } />
      <div className="px-lg">
        <JobTable
          loading={isLoading}
          dataSource={listData}
          pagination={{
            current: currentPage,
            total: count,
            pageSize,
          }}
        />
      </div>
    </>
  );
};

export default ArchivedJobs;
