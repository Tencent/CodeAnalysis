/** 平台类型 */
export enum ScmPlatformEnum {
  TGIT = 1,
  GIT_TENCENT,
  CODING,
  GITHUB,
  GITEE,
  GITLAB,
  OTHER,
}

export const SCM_PLATFORM_CHOICES = {
  [ScmPlatformEnum.TGIT]: '腾讯工蜂(OA)',
  [ScmPlatformEnum.GIT_TENCENT]: '腾讯工蜂',
  [ScmPlatformEnum.CODING]: 'Coding',
  [ScmPlatformEnum.GITHUB]: 'GitHub',
  [ScmPlatformEnum.GITEE]: 'Gitee',
  [ScmPlatformEnum.GITLAB]: 'GitLab',
  [ScmPlatformEnum.OTHER]: '其它平台',
};

/**
 * 凭证类型
 */
export const AUTH_TYPE = {
  HTTP: 'password',
  SSH: 'ssh_token',
  OAUTH: 'oauth',
};

export const AUTH_TYPE_TXT = {
  HTTP: '用户名 + 密码',
  SSH: 'SSH',
  OAUTH: 'OAuth',
};

// 凭证映射，对应 api 返回的字段名
export const SCM_MAP = {
  [AUTH_TYPE.HTTP]: 'scm_account',
  [AUTH_TYPE.SSH]: 'scm_ssh',
  [AUTH_TYPE.OAUTH]: 'scm_oauth',
};
