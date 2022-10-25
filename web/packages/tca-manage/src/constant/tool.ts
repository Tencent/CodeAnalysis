import invert from 'lodash/invert';
import { generateOptions } from '@tencent/micro-frontend-shared/util';

export enum RuleEditParamEnum {
  SEVERITY,
  STATUS,
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

export const RULE_STATE_OPTIONS = [
  {
    label: '活跃',
    value: false,
  },
  {
    label: '失效',
    value: true,
  },
];

export enum PkgRuleStateEnum {
  ENABLE = 1,
  DISABLE,
}

export const PkgRuleStateInvertEnum = invert(PkgRuleStateEnum);

export const PKG_RULE_STATE_CHOICES = {
  [PkgRuleStateEnum.ENABLE]: '启用',
  [PkgRuleStateEnum.DISABLE]: '屏蔽',
};

export const PKG_RULE_STATE_OPTIONS = generateOptions(PKG_RULE_STATE_CHOICES, true);

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

export const RULE_CATEGORY_OPTIONS = generateOptions(RULE_CATEGORY_CHOICES);

enum LibEnvEnum {
  LINUX = 'linux',
  MAC = 'mac',
  WINDOWS = 'windows',
  ARM64_LINUX = 'linux_arm64'
}

export const LIB_ENV = {
  [LibEnvEnum.LINUX]: 'Linux',
  [LibEnvEnum.MAC]: 'Mac',
  [LibEnvEnum.WINDOWS]: 'Windows',
  [LibEnvEnum.ARM64_LINUX]: 'Linux ARM64',
};

export const LIB_ENV_OPTIONS = generateOptions(LIB_ENV, false);

export enum ToolStatusEnum {
  RUNNING = 0,
  SUSPENDING,
  DISABLE,
  TRIAL,
}

export const TOOL_STATUS_CHOICES = {
  [ToolStatusEnum.RUNNING]: '正常运营',
  [ToolStatusEnum.SUSPENDING]: '暂停使用',
  [ToolStatusEnum.DISABLE]: '已下架',
  [ToolStatusEnum.TRIAL]: '体验运营',
};

export const TOOL_STATUS_OPTIONS = generateOptions(TOOL_STATUS_CHOICES);

export enum ToolScopeEnum {
  PUBLIC = 0,
  PRIVATE = 1,
}

export const TOOL_SCOPE_CHOICES = {
  [ToolScopeEnum.PUBLIC]: '公开',
  [ToolScopeEnum.PRIVATE]: '私有',
};

export const TOOL_SCOPE_OPTIONS = generateOptions(TOOL_SCOPE_CHOICES);
