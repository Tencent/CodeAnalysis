import { t } from '@src/i18n/i18next';

export const TEAM_STATUS_ENUM = {
  ACTIVE: 1,
  INACTIVE: 2,
};

export const TEAM_STATUS_CHOICES = {
  [TEAM_STATUS_ENUM.ACTIVE]: t('活跃'),
  [TEAM_STATUS_ENUM.INACTIVE]: t('禁用'),
};

export const TEAM_STATUS_OPTIONS = [
  {
    label: TEAM_STATUS_CHOICES[TEAM_STATUS_ENUM.ACTIVE],
    value: TEAM_STATUS_ENUM.ACTIVE,
  },
  {
    label: TEAM_STATUS_CHOICES[TEAM_STATUS_ENUM.INACTIVE],
    value: TEAM_STATUS_ENUM.INACTIVE,
  },
];
