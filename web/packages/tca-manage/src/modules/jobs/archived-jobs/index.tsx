/**
 * Job 归档任务列表页面
 * biz-start
 * 目前适用于全平台
 * biz-end
 */
import React from 'react';
import { t } from '@src/utils/i18n';
import { Row, Col, Tabs } from 'tdesign-react';
import Search from '@tencent/micro-frontend-shared/tdesign-component/search';
import { useURLParams, useFetch } from '@tencent/micro-frontend-shared/hooks';

// 项目内
import { jobAPI } from '@src/services/jobs';

// 模块内
import { ARCHIVE_JOB_FILTER_FIELDS as filterFields, ARCHIVE_JOB_MORE_SEARCH_FIELDS, ARCHIVE_JOB_SEARCH_FIELDS, DEFAULT_ARCHIVE_JOB_FILTER } from '../constants';
import JobTable from '../job-table';
import s from '../../style.scss';

const { TabPanel } = Tabs;

const ArchivedJobs = () => {
  const { filter, currentPage, pageSize, searchParams } = useURLParams(filterFields);
  const [{ data, isLoading }] = useFetch(jobAPI.getArchived, [{ ...DEFAULT_ARCHIVE_JOB_FILTER, ...filter }]);
  const { results: listData = [], count = 0 } = data || {};

  return (
    <>
      <Row className={s.header} align="middle">
        <Col flex="auto">
          <Tabs defaultValue="project" size="large">
            <TabPanel label={t('归档分析记录列表')} value="project" />
          </Tabs>
        </Col>
      </Row>
      <Search
        fields={ARCHIVE_JOB_SEARCH_FIELDS}
        moreFields={ARCHIVE_JOB_MORE_SEARCH_FIELDS}
        loading={false}
        searchParams={searchParams}
        filters={filterFields}
        defaultValues={DEFAULT_ARCHIVE_JOB_FILTER}
      />
      <div className="px-lg">
        <JobTable
          archived
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
