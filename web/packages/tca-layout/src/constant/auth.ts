import { generateOptions } from '@tencent/micro-frontend-shared/util';

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

export const SCM_PLATFORM_OPTIONS = generateOptions(SCM_PLATFORM_CHOICES, true);

export const DEFAULT_SCM_PLATFORM = [
  {
    id: ScmPlatformEnum.TGIT,
    scm_platform: ScmPlatformEnum.TGIT,
    scm_platform_name: ScmPlatformNameEnum.TGIT,
  },
  {
    id: ScmPlatformEnum.GIT_TENCENT,
    scm_platform: ScmPlatformEnum.GIT_TENCENT,
    scm_platform_name: ScmPlatformNameEnum.GIT_TENCENT,
  },
  {
    id: ScmPlatformEnum.CODING,
    scm_platform: ScmPlatformEnum.CODING,
    scm_platform_name: ScmPlatformNameEnum.CODING,
  },
  {
    id: ScmPlatformEnum.GITHUB,
    scm_platform: ScmPlatformEnum.GITHUB,
    scm_platform_name: ScmPlatformNameEnum.GITHUB,
  },
  {
    id: ScmPlatformEnum.GITEE,
    scm_platform: ScmPlatformEnum.GITEE,
    scm_platform_name: ScmPlatformNameEnum.GITEE,
  },
  {
    id: ScmPlatformEnum.GITLAB,
    scm_platform: ScmPlatformEnum.GITLAB,
    scm_platform_name: ScmPlatformNameEnum.GITLAB,
  },
];

export enum LevelEnum {
  NORMAL = 1,
  VIP,
  SUPER_VIP,
}
