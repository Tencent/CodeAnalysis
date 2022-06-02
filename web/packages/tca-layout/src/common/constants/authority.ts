
import { t } from '@src/i18n/i18next';

/**
 * 凭证类型
 */
 export const AUTH_TYPE = {
  HTTP: 'password',
  SSH: 'ssh_token',
  OAUTH: 'oauth',
};

export const AUTH_TYPE_TXT = {
  HTTP: t('用户名 + 密码'),
  SSH: t('ssh'),
  OAUTH: t('OAuth'),
};

// 平台类型
enum SCM_PLATFORM_ENUM {
  OTHER = 1,
  TGIT,
  CODING,
  GITHUB,
  GITEE,
  GITLAB
}

export const SCM_PLATFORM = {
  [SCM_PLATFORM_ENUM.OTHER]: t('其他'),
  [SCM_PLATFORM_ENUM.TGIT]: t('腾讯工蜂'),
  [SCM_PLATFORM_ENUM.CODING]: t('CODING'),
  [SCM_PLATFORM_ENUM.GITHUB]: t('GitHub'),
  [SCM_PLATFORM_ENUM.GITEE]: t('Gitee'),
  [SCM_PLATFORM_ENUM.GITLAB]: t('GitLab'),
};

// 凭证映射，对应 api 返回的字段名
export const SCM_MAP = {
  [AUTH_TYPE.HTTP]: 'scm_account',
  [AUTH_TYPE.SSH]: 'scm_ssh',
  [AUTH_TYPE.OAUTH]: 'scm_oauth'
}