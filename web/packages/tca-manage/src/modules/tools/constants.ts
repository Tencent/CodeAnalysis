import { SearchFormField } from '@tencent/micro-frontend-shared/tdesign-component/search';
import { t } from '@src/utils/i18n';
import { generateOptions } from '@tencent/micro-frontend-shared/util';

/** 工具运营状态 */
export enum StatusEnum {
  /** 正常运营 */
  RUNNING = 0,
  /** 暂停使用 */
  SUSPENDING,
  /** 下架 */
  DISABLE,
  /** 体验运营 */
  TRIAL,
}

/** 工具运营状态 kv */
export const STATUS_CHOICES = {
  [StatusEnum.RUNNING]: t('正常运营'),
  [StatusEnum.SUSPENDING]: t('暂停使用'),
  [StatusEnum.DISABLE]: t('已下架'),
  [StatusEnum.TRIAL]: t('体验运营'),
};

export const STATUS_OPTIONS = generateOptions(STATUS_CHOICES, true);

/** 工具使用权限 */
export enum PermEnum{
  /** 团队内可用 */
  TEAM = 1,
  /** 全平台可用 */
  ALL,
  /** 支持自定义规则且全平台可用 */
  ALL_CUSTOM,
}

/** 工具使用权限kv */
export const PERM_CHOICES = {
  [PermEnum.TEAM]: '团队内可用',
  [PermEnum.ALL]: '全平台可用',
  [PermEnum.ALL_CUSTOM]: '支持自定义规则，全平台可用',
};

/** 工具使用权限 options */
export const PERM_OPTIONS = generateOptions(PERM_CHOICES, true);

/** 定义筛选字段结构 */
export const TOOL_SEARCH_FIELDS: SearchFormField[] = [{
  name: 'fuzzy_name',
  label: '名称',
  formType: 'input',
  type: 'string',
  placeholder: '工具名称',
}, {
  name: 'status',
  label: '状态',
  formType: 'select',
  type: 'string',
  options: STATUS_OPTIONS,
}];

/** 高级搜索的筛选字段 */
export const TOOL_MORE_SEARCH_FIELDS: SearchFormField[] = [];

/** 整体的筛选字段 */
export const TOOL_FILTER_FIELDS = TOOL_SEARCH_FIELDS.concat(TOOL_MORE_SEARCH_FIELDS);
