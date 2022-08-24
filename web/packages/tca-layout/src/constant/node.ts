import { SearchFormField } from '@tencent/micro-frontend-shared/component/search';
import { generateOptions } from '@tencent/micro-frontend-shared/util';

export const STATUS_ENUM = {
  DISACTIVE: 0,
  ACTIVE: 1,
  OFFLINE: 2,
};

export const STATUS_CHOICES = {
  [STATUS_ENUM.DISACTIVE]: '不可用',
  [STATUS_ENUM.ACTIVE]: '活跃',
  [STATUS_ENUM.OFFLINE]: '离线',
};

export const STATUS_OPTIONS = generateOptions(STATUS_CHOICES, true);

export const STATE_ENUM = {
  FREE: 0,
  BUSY: 1,
};

export const STATE_CHOICES = {
  [STATE_ENUM.BUSY]: '忙碌',
  [STATE_ENUM.FREE]: '空闲',
};

export const TAG_TYPE_ENUM = {
  PUBLIC: 1,
  PRIVATE: 2,
  DISABLED: 99,
};

export const TAG_TYPE_CHOICES = {
  [TAG_TYPE_ENUM.PUBLIC]: '公共',
  [TAG_TYPE_ENUM.PRIVATE]: '团队',
  [TAG_TYPE_ENUM.DISABLED]: '停用',
};

export const TAG_TYPE_OPTIONS = generateOptions(TAG_TYPE_CHOICES, true);

export const TAG_TYPE_COLOR = {
  [TAG_TYPE_ENUM.PUBLIC]: 'geekblue',
  [TAG_TYPE_ENUM.PRIVATE]: 'blue',
  [TAG_TYPE_ENUM.DISABLED]: 'default',
};

export const TASK_STATE_ENUM = {
  WAITING: 0,
  RUNNING: 1,
  CLOSED: 2,
  CLOSING: 3,
  INITING: 4,
  INITED: 5,
};

export const TASK_STATE_CHOICES = {
  [TASK_STATE_ENUM.WAITING]: '等待中',
  [TASK_STATE_ENUM.RUNNING]: '执行中',
  [TASK_STATE_ENUM.CLOSED]: '已结束',
  [TASK_STATE_ENUM.CLOSING]: '入库中',
  [TASK_STATE_ENUM.INITING]: '初始化',
  [TASK_STATE_ENUM.INITED]: '已初始化',
};

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
