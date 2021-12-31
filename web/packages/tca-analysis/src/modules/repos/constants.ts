import { t } from '@src/i18n/i18next';

/**
 * 代码库页面的tab 切换
 */
export const REPO_TAB_TYPE = {
  MEMBER: 'member',
  AUTH: 'auth',
  OVERVIEW: 'overview',
};

export const REPO_TAB_TYPE_TXT = {
  MEMBER: t('成员权限'),
  AUTH: t('认证方式'),
  OVERVIEW: t('仓库信息'),
};

export const REPO_TAB_OPTIONS = [
  {
    label: REPO_TAB_TYPE_TXT.MEMBER,
    value: REPO_TAB_TYPE.MEMBER,
  },
  {
    label: REPO_TAB_TYPE_TXT.AUTH,
    value: REPO_TAB_TYPE.AUTH,
  },
  {
    label: REPO_TAB_TYPE_TXT.OVERVIEW,
    value: REPO_TAB_TYPE.OVERVIEW,
  },
];

/**
 * 凭证类型
 */
export const AUTH_TYPE = {
  HTTP: 'password',
  SSH: 'ssh_token',
};

export const AUTH_TYPE_TXT = {
  HTTP: t('用户名 + 密码'),
  SSH: t('ssh'),
};

export const AUTH_TYPE_OPTIONS = [
  {
    label: AUTH_TYPE_TXT.HTTP,
    value: AUTH_TYPE.HTTP,
  },
  {
    label: AUTH_TYPE_TXT.SSH,
    value: AUTH_TYPE.SSH,
  },
];

export const AUTH_TYPE_CHOICES = {
  [AUTH_TYPE.HTTP]: AUTH_TYPE_TXT.HTTP,
};

/**
 * 仓库类型
 */
export const REPO_TYPE = {
  GIT: 'git',
  SVN: 'svn',
};

export const REPO_TYPE_OPTIONS = [REPO_TYPE.GIT, REPO_TYPE.SVN];
