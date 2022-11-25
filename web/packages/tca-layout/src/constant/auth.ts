export enum AuthTypeEnum {
  HTTP = 'password',
  SSH = 'ssh_token',
  OAUTH = 'oauth',
}

export enum AuthTypeTxtEnum {
  HTTP = '用户名 + 密码',
  SSH = 'SSH',
  OAUTH = 'OAuth',
}

/** 凭证映射，对应 api 返回的字段名*/
export const SCM_MAP = {
  [AuthTypeEnum.HTTP]: 'scm_account',
  [AuthTypeEnum.SSH]: 'scm_ssh',
  [AuthTypeEnum.OAUTH]: 'scm_oauth',
};

export const AUTH_TYPE_CHOICES = {
  [AuthTypeEnum.HTTP]: AuthTypeTxtEnum.HTTP,
  [AuthTypeEnum.SSH]: AuthTypeTxtEnum.SSH,
  [AuthTypeEnum.OAUTH]: AuthTypeTxtEnum.OAUTH,
};

export const AUTH_TYPE_OPTIONS = [{
  label: AUTH_TYPE_CHOICES[AuthTypeEnum.HTTP],
  value: AuthTypeEnum.HTTP,
}, {
  label: AUTH_TYPE_CHOICES[AuthTypeEnum.SSH],
  value: AuthTypeEnum.SSH,
}];

/** OAuth平台类型名称 */
export enum ScmPlatformNameEnum {
  TGIT = 'tgit',
  GIT_TENCENT = 'tgitsaas',
  CODING = 'coding',
  GITHUB = 'github',
  GITEE = 'gitee',
  GITLAB = 'gitlab',
}

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

export enum LevelEnum {
  NORMAL = 1,
  VIP,
  SUPER_VIP,
}
