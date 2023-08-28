import { generateOptions } from '../../util';
import { PLATFORM_CHOICES_DEFAULT, PLATFORM_NAME_ENUM_DEFAULT, PLATFORM_ICON_ENUM_DEFAULT } from './common-constant';
import codingIcon from './icons/coding.svg';
import giteeIcon from './icons/gitee.svg';
import githubIcon from './icons/github.svg';
import gitlabIcon from './icons/gitlab.svg';
import tgitIcon from './icons/tgit.svg';
import defaultIcon from './icons/default.svg';

/** 凭证类型枚举 */
export enum AuthTypeEnum {
  HTTP = 'password',
  SSH = 'ssh_token',
  OAUTH = 'oauth',
}

/** 凭证类型文本枚举 */
export enum AuthTypeTxtEnum {
  HTTP = '用户名 + 密码',
  SSH = 'SSH',
  OAUTH = 'OAuth',
}

/** 凭证类型 kv */
export const AUTH_TYPE_CHOICES = {
  [AuthTypeEnum.HTTP]: AuthTypeTxtEnum.HTTP,
  [AuthTypeEnum.SSH]: AuthTypeTxtEnum.SSH,
  [AuthTypeEnum.OAUTH]: AuthTypeTxtEnum.OAUTH,
};

/** 凭证类型 options，排除 oauth */
export const AUTH_TYPE_OPTIONS = [{
  label: AUTH_TYPE_CHOICES[AuthTypeEnum.HTTP],
  value: AuthTypeEnum.HTTP,
}, {
  label: AUTH_TYPE_CHOICES[AuthTypeEnum.SSH],
  value: AuthTypeEnum.SSH,
}];

/** 凭证映射，对应 api 返回的字段名*/
export const SCM_MAP = {
  [AuthTypeEnum.HTTP]: 'scm_account',
  [AuthTypeEnum.SSH]: 'scm_ssh',
  [AuthTypeEnum.OAUTH]: 'scm_oauth',
};

/** OAuth 所属平台类型枚举 */
export enum ScmPlatformEnum {
  DEFAULT = 1,
  GIT_TENCENT,
  CODING,
  GITHUB,
  GITEE,
  GITLAB,
  OTHER,
}


/** OAuth 所属平台类型 kv */
export const SCM_PLATFORM_CHOICES = {
  // 暂时定制兼容
  [ScmPlatformEnum.DEFAULT]: PLATFORM_CHOICES_DEFAULT,
  [ScmPlatformEnum.GIT_TENCENT]: '腾讯工蜂',
  [ScmPlatformEnum.CODING]: 'Coding',
  [ScmPlatformEnum.GITHUB]: 'GitHub',
  [ScmPlatformEnum.GITEE]: 'Gitee',
  [ScmPlatformEnum.GITLAB]: 'GitLab',
  [ScmPlatformEnum.OTHER]: '其它平台',
};

/** OAuth 所属平台类型 options */
export const SCM_PLATFORM_OPTIONS = generateOptions(SCM_PLATFORM_CHOICES, true);

/** OAuth 所属平台类型名称 */
export const ScmPlatformNameEnum = {
  DEFAULT: PLATFORM_NAME_ENUM_DEFAULT,
  GIT_TENCENT: 'tgitsaas',
  CODING: 'coding',
  GITHUB: 'github',
  GITEE: 'gitee',
  GITLAB: 'gitlab',
};

/** OAuth 所属平台类型名称 kv */
export const SCM_PLATFORM_NAME_CHOICES = {
  [ScmPlatformNameEnum.DEFAULT]: {
    id: ScmPlatformEnum.DEFAULT,
    scm_platform: ScmPlatformEnum.DEFAULT,
    scm_platform_name: ScmPlatformNameEnum.DEFAULT,
    auth_type: AuthTypeEnum.OAUTH,
  },
  [ScmPlatformNameEnum.GIT_TENCENT]: {
    id: ScmPlatformEnum.GIT_TENCENT,
    scm_platform: ScmPlatformEnum.GIT_TENCENT,
    scm_platform_name: ScmPlatformNameEnum.GIT_TENCENT,
    auth_type: AuthTypeEnum.OAUTH,
  },
  [ScmPlatformNameEnum.CODING]: {
    id: ScmPlatformEnum.CODING,
    scm_platform: ScmPlatformEnum.CODING,
    scm_platform_name: ScmPlatformNameEnum.CODING,
    auth_type: AuthTypeEnum.OAUTH,
  },
  [ScmPlatformNameEnum.GITHUB]: {
    id: ScmPlatformEnum.GITHUB,
    scm_platform: ScmPlatformEnum.GITHUB,
    scm_platform_name: ScmPlatformNameEnum.GITHUB,
    auth_type: AuthTypeEnum.OAUTH,
  },
  [ScmPlatformNameEnum.GITEE]: {
    id: ScmPlatformEnum.GITEE,
    scm_platform: ScmPlatformEnum.GITEE,
    scm_platform_name: ScmPlatformNameEnum.GITEE,
    auth_type: AuthTypeEnum.OAUTH,
  },
  [ScmPlatformNameEnum.GITLAB]: {
    id: ScmPlatformEnum.GITLAB,
    scm_platform: ScmPlatformEnum.GITLAB,
    scm_platform_name: ScmPlatformNameEnum.GITLAB,
    auth_type: AuthTypeEnum.OAUTH,
  },
};

export const SCM_PLATFORM_ICONS = {
  [ScmPlatformEnum.DEFAULT]: PLATFORM_ICON_ENUM_DEFAULT,
  [ScmPlatformEnum.GIT_TENCENT]: tgitIcon,
  [ScmPlatformEnum.CODING]: codingIcon,
  [ScmPlatformEnum.GITHUB]: githubIcon,
  [ScmPlatformEnum.GITEE]: giteeIcon,
  [ScmPlatformEnum.GITLAB]: gitlabIcon,
  [ScmPlatformEnum.OTHER]: defaultIcon,
};
