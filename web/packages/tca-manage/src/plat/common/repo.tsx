import React from 'react';
import { SearchFormField } from '@tencent/micro-frontend-shared/tdesign-component/search';
import { t } from '@tencent/micro-frontend-shared/i18n';

import OrgAndTeamInfo from '@src/modules/components/org-team-info';

/** 定义筛选字段结构 */
export const REPO_SEARCH_FIELDS: SearchFormField[] = [{
  name: 'organization',
  type: 'number',
  formType: 'input',
  placeholder: t('团队 ID'),
}, {
  name: 'project_team',
  type: 'number',
  formType: 'input',
  placeholder: t('项目 ID'),
}];

export const ColumnOrgInfo = {
  colKey: 'organization',
  title: t('所属团队&项目'),
  width: 150,
  cell: ({ row }: any) => (
    <OrgAndTeamInfo org={row.organization} team={row.project_team} />
  ),
};
