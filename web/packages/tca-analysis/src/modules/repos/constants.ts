// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================


/**
 * 代码库页面的tab 切换
 */
export const REPO_TAB_TYPE = {
  MEMBER: 'member',
  AUTH: 'auth',
  OVERVIEW: 'overview',
};

export const REPO_TAB_TYPE_TXT = {
  MEMBER: '成员权限',
  AUTH: '认证方式',
  OVERVIEW: '仓库信息',
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
  OAUTH: 'oauth',
};

export const AUTH_TYPE_TXT = {
  HTTP: '用户名 + 密码',
  SSH: 'ssh',
  OAUTH: 'OAuth',
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

export const DEFAULT_SCM_PLATFORM = [
  {
    scm_platform: 2,
    scm_platform_name: 'tgitsaas',
  },
  {
    scm_platform: 4,
    scm_platform_name: 'github',
  },
  {
    scm_platform: 5,
    scm_platform_name: 'gitee',
  },
  {
    scm_platform: 6,
    scm_platform_name: 'gitlab',
  },
];

export const SCM_PLATFORM = {
  1: '其他',
  2: '腾讯工蜂',
  3: 'CODING',
  4: 'GitHub',
  5: 'Gitee',
  6: 'GitLab',
};
