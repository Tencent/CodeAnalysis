import React, { useEffect, useState } from 'react';
import { useParams, useHistory } from 'react-router-dom';
import { Space, Button } from 'tdesign-react';
import Search from '@tencent/micro-frontend-shared/tdesign-component/search';
import { useURLParams, useFetch } from '@tencent/micro-frontend-shared/hooks';
import { ArrowLeftIcon } from 'tdesign-icons-react';

// 项目内
import { t } from '@src/utils/i18n';
import { getBatchJobs, getBatchReport } from '@src/services/batchjobs';

// 模块内
import { JOB_FILTER_FIELDS as filterFields, JOB_MORE_SEARCH_FIELDS, JOB_SEARCH_FIELDS } from './constants';
import JobTable from './job-table';
import PageHeader from '@tencent/micro-frontend-shared/tdesign-component/page-header';

const ArchivedJobs = () => {
  const { reportId }: any = useParams();
  const history = useHistory();
  const [reportInfo, setReportInfo] = useState<any>({});
  const { filter, currentPage, pageSize, searchParams } = useURLParams(filterFields);
  const [{ data, isLoading }] = useFetch(getBatchJobs, [reportId, { ...filter }]);
  const { results: listData = [], count = 0 } = data || {};

  useEffect(() => {
    getBatchReport(reportId).then((res: any) => {
      setReportInfo(res);
    });
  }, [reportId]);

  return (
    <>
      <PageHeader title={
        <Space align='center' size={8}>
          <Button icon={<ArrowLeftIcon />} shape='circle' onClick={() => history.push('/manage/batch/reports')} />
          <span>{reportInfo?.name} {t('任务详情')}</span>
        </Space>
      } />
      <Search
        fields={JOB_SEARCH_FIELDS}
        moreFields={JOB_MORE_SEARCH_FIELDS}
        loading={false}
        searchParams={searchParams}
        filters={filterFields}
      />
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
