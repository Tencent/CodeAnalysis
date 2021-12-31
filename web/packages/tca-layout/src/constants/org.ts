import { t } from '@src/i18n/i18next';

export const STATUS_ENUM = {
  ACTIVE: 1,
  DISACTIVE: 2,
};

export const STATUS_CHOICES = {
  [STATUS_ENUM.ACTIVE]: t('已激活'),
  [STATUS_ENUM.DISACTIVE]: t('审核中'),
};

export const APPLY_STATUS_ENUM = {
  CHECKING: 1,
  CHECKED: 2,
  CANCELED: 3,
};

export const APPLY_STATUS_CHOICES = {
  [APPLY_STATUS_ENUM.CHECKING]: t('审核中'),
  [APPLY_STATUS_ENUM.CHECKED]: t('审核完成'),
  [APPLY_STATUS_ENUM.CANCELED]: t('取消申请'),
};

export const CHECK_RESULT_ENUM = {
  PASS: 1,
  NO_PASS: 2,
};

export const CHECK_RESULT_CHOICES = {
  [CHECK_RESULT_ENUM.PASS]: t('审核通过'),
  [CHECK_RESULT_ENUM.NO_PASS]: t('审核不通过'),
};
