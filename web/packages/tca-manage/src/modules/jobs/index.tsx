/**
 * Job 任务列表页面
 */
import React, { useState } from 'react';
import Search from '@tencent/micro-frontend-shared/tdesign-component/search';
import PageHeader from '@tencent/micro-frontend-shared/tdesign-component/page-header';
import { useURLParams, useFetch } from '@tencent/micro-frontend-shared/hooks';

// 项目内
import { jobAPI } from '@src/services/jobs';

// 模块内
import { JOB_FILTER_FIELDS as filterFields, JOB_SEARCH_FIELDS, JOB_MORE_SEARCH_FIELDS } from './constants';
import JobTable from './job-table';
import CancelJobModal from './cancel-job-modal';
import { JobData } from './types';

const Jobs = () => {
  const { filter, currentPage, pageSize, searchParams } = useURLParams(filterFields);
  const [{ data, isLoading }, reload] = useFetch(jobAPI.get, [filter]);
  const { results: listData = [], count = 0 } = data || {};
  const [modalVisible, setModalVisible] = useState<boolean>(false);
  const [selectedJob, setSelectedJob] = useState<JobData>();

  /** 点击取消任务操作 */
  const onCancelJob = (jobInfo: any) => {
    setSelectedJob(jobInfo);
    setModalVisible(true);
  };

  /** 取消任务后操作 */
  const afterCancelJob = () => {
    setModalVisible(false);
    reload();
  };

  return (
    <>
      <PageHeader title="分析记录列表" description="平台全部分析任务列表" />
      <Search
        fields={JOB_SEARCH_FIELDS}
        moreFields={JOB_MORE_SEARCH_FIELDS}
        loading={false}
        searchParams={searchParams}
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
          cancelJob={onCancelJob}
        />
        <CancelJobModal
          jobInfo={selectedJob}
          visible={modalVisible}
          onOk={afterCancelJob}
          onCancel={() => setModalVisible(false)}
        />
      </div>
    </>
  );
};

export default Jobs;
