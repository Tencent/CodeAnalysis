import { t } from '@src/i18n/i18next';

export const ORG_STATE_ENUM = {
  ACTIVE: 1,
  INACTIVE: 99,
};

export const ORG_STATE_CHOICES = {
  [ORG_STATE_ENUM.ACTIVE]: t('活跃'),
  [ORG_STATE_ENUM.INACTIVE]: t('禁用'),
};

export const ORG_STATE_OPTIONS = [
  {
    label: ORG_STATE_CHOICES[ORG_STATE_ENUM.ACTIVE],
    value: ORG_STATE_ENUM.ACTIVE,
  },
  {
    label: ORG_STATE_CHOICES[ORG_STATE_ENUM.INACTIVE],
    value: ORG_STATE_ENUM.INACTIVE,
  },
];
