import { t } from '@src/utils/i18n';
import { generateOptions } from '@tencent/micro-frontend-shared/util';

/** 节点工作状态 */
export enum NodeStateEnum {
  /** 忙碌 */
  FREE,
  /** 空闲 */
  BUSY
}

/** 节点工作状态 kv */
export const STATE_CHOICES = {
  [NodeStateEnum.BUSY]: '忙碌',
  [NodeStateEnum.FREE]: '空闲',
};

/** 节点工作状态 options */
export const NODE_STATE_OPTIONS = generateOptions(STATE_CHOICES, true);

/** 节点可用状态 */
export enum NodeEnabledEnum {
  /** 不可用 */
  DISACTIVE =0,
  /** 活跃 */
  ACTIVE,
  /** 离线 */
  OFFLINE,
}

/** 节点可用状态 kv */
export const NODE_ENABLED_CHOICES = {
  [NodeEnabledEnum.DISACTIVE]: '不可用',
  [NodeEnabledEnum.ACTIVE]: '活跃',
  [NodeEnabledEnum.OFFLINE]: '离线',
};

/** 节点可用状态 options */
export const NODE_ENABLED_OPTIONS = generateOptions(NODE_ENABLED_CHOICES, true);

/** 节点标签类型 */
export enum TagTypeEnum {
  /** 公共 */
  PUBLIC = 1,
  /** 团队私有 */
  PRIVATE,
  /** 停用 */
  DISABLED = 99,
}

/** 节点标签类型 kv */
export const TAG_TYPE_CHOICES = {
  [TagTypeEnum.PUBLIC]: t('公共'),
  [TagTypeEnum.PRIVATE]: t('团队'),
  [TagTypeEnum.DISABLED]: t('停用'),
};

/** 节点标签类型 options */
export const TAG_TYPE_OPTIONS = generateOptions(TAG_TYPE_CHOICES, true);

/** 节点标签类型颜色 */
export const TAG_TYPE_COLOR = {
  [TagTypeEnum.PUBLIC]: 'blue',
  [TagTypeEnum.PRIVATE]: 'cyan',
  [TagTypeEnum.DISABLED]: 'default',
};

/** 节点批量编辑表单项 */
export interface NodeMultiEditFormItem {
  /** 字段名称，唯一标识 */
  name: string;
  /** 表单项标签 */
  label: string;
  /** 表单项下拉选项 */
  options: Array<any>;
  /** 是否多选 */
  multiSelect?: boolean;
}
