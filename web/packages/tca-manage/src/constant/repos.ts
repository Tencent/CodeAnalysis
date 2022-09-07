import { generateOptions } from '@tencent/micro-frontend-shared/util';

export enum RepoTypeEnum {
  GIT = 'git',
  SVN = 'svn'
}

export const REPO_TYPE_CHOICES = {
  [RepoTypeEnum.GIT]: 'GIT',
  [RepoTypeEnum.SVN]: 'SVN',
};

export const REPO_TYPE_OPTIONS = generateOptions(REPO_TYPE_CHOICES);

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
