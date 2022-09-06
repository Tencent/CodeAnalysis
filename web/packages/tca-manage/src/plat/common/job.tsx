import React from 'react';
import { get } from 'lodash';
import { PrimaryTableCol } from 'tdesign-react';
import { SearchFormField } from '@tencent/micro-frontend-shared/tdesign-component/search';
import { t } from '@tencent/micro-frontend-shared/i18n';

import OrgAndTeamInfo from '@src/modules/components/org-team-info';

/** 定义筛选字段结构 */
export const JOB_MORE_SEARCH_FIELDS: SearchFormField[] = [{
  name: 'result_msg',
  label: t('详情'),
  type: 'string',
  formType: 'input',
  placeholder: t('结果详情'),
}, {
  name: 'created_from',
  label: t('渠道'),
  type: 'string',
  formType: 'input',
  placeholder: t('启动渠道'),
}, {
  name: 'scm_url',
  label: t('URL'),
  type: 'string',
  formType: 'input',
  placeholder: t('代码库地址'),
}, {
  name: 'creator',
  label: t('启动人'),
  type: 'string',
  formType: 'input',
  placeholder: t('启动人'),
}];

/** job列表页面团队列 */
export const ColumnOrgInfo: PrimaryTableCol<any> = {
  colKey: 'project',
  title: t('所属团队&项目'),
  width: 200,
  cell: ({ row }: any) => (<OrgAndTeamInfo org={get(row, ['project', 'organization'])} team={get(row, ['project', 'project_team'])} />),
};
