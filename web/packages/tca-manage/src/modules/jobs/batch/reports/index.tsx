import React from 'react';
import { useURLParams, useFetch } from '@tencent/micro-frontend-shared/hooks';

// 项目内
import { getBatchReports } from '@src/services/batchjobs';

// 模块内
import ReportTable from './report-table';

const BatchReports = () => {
  const { filter, currentPage, pageSize } = useURLParams();
  const [{ data, isLoading }] = useFetch(getBatchReports, [{ ...filter }]);
  const { results: listData = [], count = 0 } = data || {};

  return (
    <div className="px-lg">
      <ReportTable
        loading={isLoading}
        dataSource={listData}
        pagination={{
          current: currentPage,
          total: count,
          pageSize,
        }}
      />
    </div>
  );
};

export default BatchReports;
