import { t } from '@src/i18n/i18next';

export const STATUS_ENUM = {
  DISACTIVE: 0,
  ACTIVE: 1,
  OFFLINE: 2,
};

export const STATUS_CHOICES = {
  [STATUS_ENUM.DISACTIVE]: t('不可用'),
  [STATUS_ENUM.ACTIVE]: t('活跃'),
  [STATUS_ENUM.OFFLINE]: t('离线'),
};

export const STATE_ENUM = {
  FREE: 0,
  BUSY: 1
}

export const STATE_CHOICES = {
  [STATE_ENUM.BUSY]: t('忙碌'),
  [STATE_ENUM.FREE]: t('空闲')
}

export const STATUS_OPTIONS = [{
  text: STATUS_CHOICES[STATUS_ENUM.ACTIVE],
  value: STATUS_ENUM.ACTIVE,
}, {
  text: STATUS_CHOICES[STATUS_ENUM.DISACTIVE],
  value: STATUS_ENUM.DISACTIVE,
}, {
  text: STATUS_CHOICES[STATUS_ENUM.OFFLINE],
  value: STATUS_ENUM.OFFLINE,
}];

export const TAG_TYPE_ENUM = {
  PUBLIC: 1,
  PRIVATE: 2,
  DISABLED: 99
};

export const TAG_TYPE_CHOICES = {
  [TAG_TYPE_ENUM.PUBLIC]: t('公共'),
  [TAG_TYPE_ENUM.PRIVATE]: t('团队'),
  [TAG_TYPE_ENUM.DISABLED]: t('停用'),
};

export const TAG_TYPE_OPTIONS = [{
  text: TAG_TYPE_CHOICES[TAG_TYPE_ENUM.PRIVATE],
  value: TAG_TYPE_ENUM.PRIVATE,
}, {
  text: TAG_TYPE_CHOICES[TAG_TYPE_ENUM.DISABLED],
  value: TAG_TYPE_ENUM.DISABLED,
}];

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
  [TASK_STATE_ENUM.WAITING]: t('等待中'),
  [TASK_STATE_ENUM.RUNNING]: t('执行中'),
  [TASK_STATE_ENUM.CLOSED]: t('已结束'),
  [TASK_STATE_ENUM.CLOSING]: t('入库中'),
  [TASK_STATE_ENUM.INITING]: t('初始化'),
  [TASK_STATE_ENUM.INITED]: t('已初始化'),
};
