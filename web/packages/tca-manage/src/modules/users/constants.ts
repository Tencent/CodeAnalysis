import { t } from '@src/i18n/i18next';

export const LEVEL_ENUM = {
  NORMAL: 1,
  VIP: 2,
  SUPER_VIP: 3,
};

export const LEVEL_CHOICES = {
  [LEVEL_ENUM.NORMAL]: t('普通用户'),
  [LEVEL_ENUM.VIP]: t('VIP用户'),
  [LEVEL_ENUM.SUPER_VIP]: t('超级VIP用户'),
};

export const LEVEL_OPTIONS = [{
  label: LEVEL_CHOICES[LEVEL_ENUM.NORMAL],
  value: LEVEL_ENUM.NORMAL,
}, {
  label: LEVEL_CHOICES[LEVEL_ENUM.VIP],
  value: LEVEL_ENUM.VIP,
}, {
  label: LEVEL_CHOICES[LEVEL_ENUM.SUPER_VIP],
  value: LEVEL_ENUM.SUPER_VIP,
}];

export const LEVEL_TAG_CHOICES = {
  [LEVEL_ENUM.NORMAL]: 'default',
  [LEVEL_ENUM.VIP]: 'gold',
  [LEVEL_ENUM.SUPER_VIP]: 'volcano',
};

export const STATUS_ENUM = {
  ACTIVE: 1,
  DISACTIVE: 2,
  EXPIRED: 3,
  FORBIDEN: 99,
};

export const STATUS_CHOICES = {
  [STATUS_ENUM.ACTIVE]: t('已激活'),
  [STATUS_ENUM.DISACTIVE]: t('待激活'),
  [STATUS_ENUM.EXPIRED]: t('已过期'),
  [STATUS_ENUM.FORBIDEN]: t('禁止'),
};

export const STATUS_OPTIONS = [{
  label: STATUS_CHOICES[STATUS_ENUM.ACTIVE],
  value: STATUS_ENUM.ACTIVE,
}, {
  label: STATUS_CHOICES[STATUS_ENUM.DISACTIVE],
  value: STATUS_ENUM.DISACTIVE,
}];
