import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';
import { Row, Col, Tabs } from 'coding-oa-uikit';
import { toNumber } from 'lodash';

// 项目内
import { t } from '@src/i18n/i18next';
import { getPaginationParams, getFilterURLPath } from '@src/utils';
import { DEFAULT_PAGER } from '@src/common/constants';
import { useURLParams, useDeepEffect } from '@src/utils/hooks';
import { getJobs } from '@src/services/jobs';

// 模块内
import s from './style.scss';
import Search from './search';
import JobTable from './job-table';

const { TabPane } = Tabs;

const FILTER_FIELDS = [
  // 'run_type',
  'state',
  'repo',
  'result',
  // 'origin',
  // 'platform',
  // 'project',
  // 'organization',
  // 'project_team',
];

const customFilterURLPath = (params = {}) => getFilterURLPath(FILTER_FIELDS, params);

const Jobs = () => {
  const history = useHistory();
  const [listData, setListData] = useState<Array<any>>([]);
  const [count, setCount] = useState(DEFAULT_PAGER.count);
  const [loading, setLoading] = useState(false);
  const { filter, currentPage, searchParams } = useURLParams(FILTER_FIELDS);

  /**
     * 根据路由参数获取团队列表
     */
  const getListData = () => {
    setLoading(true);

    // result_code <= 99 表示通过，result_code >= 99 表示异常
    const { result } = filter;
    const params: any = {};
    if (toNumber(result) === 0) {
      params.result_code_lte = 99;
    }

    if (toNumber(result) === 1) {
      params.result_code_gte = 99;
    }

    getJobs({ ...filter, ...params }).then((response) => {
      setCount(response.count);
      setListData(response.results || []);
      setLoading(false);
    });
  };

  // 当路由参数变化时触发
  useDeepEffect(() => {
    getListData();
  }, [filter]);

  // 筛选
  const onSearch = (params: any) => {
    history.push(customFilterURLPath({
      limit: DEFAULT_PAGER.pageSize,
      offset: DEFAULT_PAGER.pageStart,
      ...params,
    }));
  };

  // 翻页
  const onChangePageSize = (page: number, pageSize: number) => {
    const params = getPaginationParams(page, pageSize);
    history.push(customFilterURLPath(params));
  };

  return (
    <>
      <Row className={s.header} align="middle">
        <Col flex="auto">
          <Tabs defaultActiveKey="project" size="large">
            <TabPane tab={t('分析记录列表')} key="project" />
          </Tabs>
        </Col>
      </Row>
      <div className={s.filterContent}>
        <Search loading={loading} searchParams={searchParams} callback={onSearch} />
      </div>
      <div className="px-lg">
        <JobTable
          dataSource={listData}
          pagination={{
            current: currentPage,
            total: count,
            showTotal: (total: any, range: any) => `${range[0]} - ${range[1]} 条数据，共 ${total} 条`,
            onChange: onChangePageSize,
          }}
        />
      </div>
    </>
  );
};

export default Jobs;
