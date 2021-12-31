import { t } from '@src/i18n/i18next';

// 分页默认值
export const DEFAULT_PAGER = {
  count: 0,
  pageSize: 10,
  pageStart: 0,
};

/**
 * 凭证类型
 */
export const AUTH_TYPE = {
  HTTP: 'http',
  SSH: 'ssh',
};

/**
 * 凭证类型options
 */
export const AUTH_TYPE_OPTIONS = [
  {
    label: t('用户名 + 密码'),
    value: AUTH_TYPE.HTTP,
  },
  {
    label: t('SSH'),
    value: AUTH_TYPE.SSH,
  },
];

/**
 * 凭证类型choices
 */
export const AUTH_TYPE_CHOICES = {
  [AUTH_TYPE.HTTP]: t('用户名 + 密码'),
  [AUTH_TYPE.SSH]: t('SSH'),
};

export const SCM_PLATFORM = {
  1: t('其他'),
  2: t('腾讯工蜂'),
  3: t('CODING'),
  4: t('GitHub'),
  5: t('Gitee'),
  6: t('GitLab'),
};

/**
 * 审批状态
 */
export const APPLY_STATUS_TYPE = {
  CHECKING: 1, // 申请中
  CHECKED: 2, // 审批完成
  CANCELED: 3, // 取消申请
};

/**
 * 审批结果
 */
export const APPLY_RESULT_TYPE = {
  PASS: 1,
  NO_PASS: 2,
};

export const MATOMO_URL = 'MATOMO_URL';
