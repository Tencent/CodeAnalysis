import { SearchFormField } from '@tencent/micro-frontend-shared/tdesign-component/search';
import { generateOptions } from '@tencent/micro-frontend-shared/util';

/** 问题解决方式 */
export enum IssueResolutionEnum {
  /** 已修复 */
  FIXED = 1,
  /** 无需修复 */
  WONTFIX,
  /** 误报 */
  INVALID,
  /** 重复单过滤 */
  DUPLICATE,
  /** 路径过滤 */
  FILTERED,
  /** 规则移除 */
  REMOVED,
  /** 历史问题 */
  EXPIRED,
  /** 注释忽略 */
  COMMENT,
}

/** 问题解决方式 kv */
export const ISSUE_RESOLUTION_CHOICES = {
  [IssueResolutionEnum.FIXED]: '已修复',
  [IssueResolutionEnum.WONTFIX]: '无需修复',
  [IssueResolutionEnum.INVALID]: '误报',
  [IssueResolutionEnum.DUPLICATE]: '重复单过滤',
  [IssueResolutionEnum.FILTERED]: '路径过滤',
  [IssueResolutionEnum.REMOVED]: '规则移除',
  [IssueResolutionEnum.EXPIRED]: '历史问题',
  [IssueResolutionEnum.COMMENT]: '注释忽略',
};

/** 问题解决方式 options */
export const ISSUE_RESOLUTION_OPTIONS = generateOptions(ISSUE_RESOLUTION_CHOICES, true);

/** 定义筛选字段结构 */
export const ISSUE_SEARCH_FIELDS: SearchFormField[] = [{
  name: 'checkrule_gid',
  label: '规则ID',
  type: 'string',
  formType: 'input',
}, {
  name: 'resolution',
  label: '解决方式',
  type: 'number',
  formType: 'select',
  options: ISSUE_RESOLUTION_OPTIONS,
}];

/** 问题状态 */
export enum IssueStateEnum {
  ACTIVE = 1,
  RESOLVED,
  CLOSED
}

/** 问题状态 kv */
export const ISSUE_STATE_CHOICES = {
  [IssueStateEnum.ACTIVE]: '未处理',
  [IssueStateEnum.RESOLVED]: '已处理',
  [IssueStateEnum.CLOSED]: '已关闭',
};
