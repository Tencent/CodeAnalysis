/**
 * Job 批量任务列表页面
 */
import React from 'react';
import { Switch, Route, Redirect } from 'react-router-dom';
import { t } from '@src/utils/i18n';

import PageHeader, { PageHeaderTabProps } from '@tencent/micro-frontend-shared/tdesign-component/page-header';

// 模块内
import BatchReports from './reports';
import TrendReports from './trendreports';

const pageHeaderTab: PageHeaderTabProps = {
  options: [{
    label: t('批次任务'),
    value: 'reports',
  }, {
    label: t('趋势分析'),
    value: 'trendreports',
  }],
  routeChangeHandler: value => `/manage/batch/${value}`,
};

const BatchComponent = () => (
  <>
    <PageHeader title="批量记录列表" tab={pageHeaderTab} />
    <Switch>
      <Route path='/manage/batch/reports' component={BatchReports} />x
      <Route path='/manage/batch/trendreports' component={TrendReports} />
      <Redirect from='/manage/batch' to='/manage/batch/reports' />
    </Switch>
  </>
);

export default BatchComponent;
