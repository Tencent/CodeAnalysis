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
  [STATE_ENUM.BUSY]: '忙碌',
  [STATE_ENUM.FREE]: '空闲'
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
  PROJECT: 0,
  NODE: 1,
};

export const TAG_TYPE_CHOICES = {
  [TAG_TYPE_ENUM.PROJECT]: t('项目&节点'),
  [TAG_TYPE_ENUM.NODE]: t('节点'),
};
