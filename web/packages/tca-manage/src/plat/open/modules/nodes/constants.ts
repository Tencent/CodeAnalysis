import { t } from '@tencent/micro-frontend-shared/i18n';
import { SearchFormField } from '@tencent/micro-frontend-shared/tdesign-component/search';
import { generateOptions } from '@tencent/micro-frontend-shared/util';

export const getNodeSearchFields = (tagOptions: any[]): SearchFormField[] => [{
  name: 'name',
  label: '名称',
  type: 'string',
  formType: 'input',
  placeholder: '节点名称',
}, {
  name: 'manager',
  label: '负责人',
  type: 'string',
  formType: 'input',
  placeholder: '负责人',
}, {
  name: 'exec_tags',
  label: '标签',
  type: 'string',
  formType: 'select',
  placeholder: '全部',
  options: tagOptions,
}];

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
