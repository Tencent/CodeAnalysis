import { SearchFormField } from '@tencent/micro-frontend-shared/tdesign-component/search';
import { t } from '@src/utils/i18n';
import { generateOptions } from '@tencent/micro-frontend-shared/util';

/** 团队使用状态 */
export enum OrgStatusEnum {
  ACTIVE = 1,
  DISACTIVE,
  EXPIRED,
  FORBIDEN = 99
}

/** 团队使用状态 kv */
export const ORG_STATUS_CHOICES = {
  [OrgStatusEnum.ACTIVE]: t('活跃'),
  [OrgStatusEnum.FORBIDEN]: t('禁用'),
};

/** 团队使用状态 options */
export const ORG_STATE_OPTIONS = generateOptions(ORG_STATUS_CHOICES, true);

/** 定义筛选字段结构 */
export const ORG_SEARCH_FIELDS: SearchFormField[] = [{
  name: 'name',
  type: 'string',
  formType: 'input',
  label: '名称',
  placeholder: '团队名称',
}, {
  name: 'status',
  type: 'number',
  formType: 'select',
  label: '状态',
  options: ORG_STATE_OPTIONS,
}];

/** 高级搜索的筛选字段 */
export const ORG_MORE_SEARCH_FIELDS: SearchFormField[] = [];

/** 整体的筛选字段 */
export const ORG_FILTER_FIELDS = ORG_SEARCH_FIELDS.concat(ORG_MORE_SEARCH_FIELDS);
