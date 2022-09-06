import { t } from '@tencent/micro-frontend-shared/i18n';

export const TAG_TYPE_ENUM = {
  PUBLIC: 1,
  PRIVATE: 2,
  DISABLED: 99,
};

export const TAG_TYPE_CHOICES = {
  [TAG_TYPE_ENUM.PUBLIC]: t('公共'),
  [TAG_TYPE_ENUM.PRIVATE]: t('团队'),
  [TAG_TYPE_ENUM.DISABLED]: t('停用'),
};
