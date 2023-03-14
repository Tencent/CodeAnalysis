import { t } from '@src/utils/i18n';
import { SearchFormField } from '@tencent/micro-frontend-shared/tdesign-component/search';
import { generateOptions } from '@tencent/micro-frontend-shared/util';

export enum TeamStateEnum {
  ACTIVE = 1,
  INACTIVE
}

export const TEAM_STATE_CHOICES = {
  [TeamStateEnum.ACTIVE]: t('活跃'),
  [TeamStateEnum.INACTIVE]: t('禁用'),
};

export const TEAM_STATE_OPTIONS = generateOptions(TEAM_STATE_CHOICES, true);


/** 定义筛选字段结构 */
export const TEAM_SEARCH_FIELDS: SearchFormField[] = [{
  name: 'check_status',
  type: 'number',
  formType: 'select',
  label: '状态',
  options: TEAM_STATE_OPTIONS,
}, {
  name: 'display_name',
  label: '名称',
  type: 'string',
  formType: 'input',
  placeholder: '项目名称',
}, {
  name: 'organization',
  label: '团队 ID',
  type: 'number',
  formType: 'input',
  placeholder: '团队 ID',
}];

/** 高级搜索的筛选字段 */
export const TEAM_MORE_SEARCH_FIELDS: SearchFormField[] = [];

/** 整体的筛选字段 */
export const TEAM_FILTER_FIELDS = TEAM_SEARCH_FIELDS.concat(TEAM_MORE_SEARCH_FIELDS);
