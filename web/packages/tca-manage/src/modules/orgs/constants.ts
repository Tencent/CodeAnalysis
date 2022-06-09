import { t } from '@src/i18n/i18next';

export const ORG_STATUS_ENUM = {
  ACTIVE: 1,
  INACTIVE: 99,
};

export const ORG_STATUS_CHOICES = {
  [ORG_STATUS_ENUM.ACTIVE]: t('活跃'),
  [ORG_STATUS_ENUM.INACTIVE]: t('禁用'),
};

export const ORG_STATUS_OPTIONS = [
  {
    label: ORG_STATUS_CHOICES[ORG_STATUS_ENUM.ACTIVE],
    value: ORG_STATUS_ENUM.ACTIVE,
  },
  {
    label: ORG_STATUS_CHOICES[ORG_STATUS_ENUM.INACTIVE],
    value: ORG_STATUS_ENUM.INACTIVE,
  },
];
