import invert from 'lodash/invert';
import { generateOptions } from '@tencent/micro-frontend-shared/util';

export enum ToolStatusEnum {
  NORMAL,
  SUSPENSION,
  DOWN,
  EXPERIENCE
}

export const TOOL_STATUS_CHOICES = {
  [ToolStatusEnum.NORMAL]: '正常使用',
  [ToolStatusEnum.SUSPENSION]: '暂停使用',
  [ToolStatusEnum.DOWN]: '已下架',
  [ToolStatusEnum.EXPERIENCE]: '体验运营',
};

export const TOOL_STATUS_OPTIONS = generateOptions(TOOL_STATUS_CHOICES, true);

export enum ToolScopeEnum {
  PUBLIC,
  PRIVATE,
  MAINTAIN,
  CUSTOM
}

export enum RuleSeverityEnum {
  FATAL = 1,
  ERROR,
  WARNING,
  INFO,
}

export const RuleSeverityInvertEnum = invert(RuleSeverityEnum);

export const RULE_SEVERITY_CHOICES = {
  [RuleSeverityEnum.FATAL]: '致命',
  [RuleSeverityEnum.ERROR]: '错误',
  [RuleSeverityEnum.WARNING]: '警告',
  [RuleSeverityEnum.INFO]: '提示',
};

export const RULE_SEVERITY_OPTIONS = generateOptions(RULE_SEVERITY_CHOICES, true);

export enum RuleCategoryEnum {
  CORRECTNESS = 1,
  SECURITY,
  PERFORMANCE,
  USABILITY,
  ACCESSIBILITY,
  I18N,
  CONVENTION,
  OTHER,
}

export const RULE_CATEGORY_CHOICES = {
  [RuleCategoryEnum.CORRECTNESS]: '功能',
  [RuleCategoryEnum.SECURITY]: '安全',
  [RuleCategoryEnum.PERFORMANCE]: '性能',
  [RuleCategoryEnum.USABILITY]: '可用性',
  [RuleCategoryEnum.ACCESSIBILITY]: '无障碍化',
  [RuleCategoryEnum.I18N]: '国际化',
  [RuleCategoryEnum.CONVENTION]: '风格',
  [RuleCategoryEnum.OTHER]: '其他',
};

export const RULE_CATEGORY_OPTIONS = generateOptions(RULE_CATEGORY_CHOICES, true);
