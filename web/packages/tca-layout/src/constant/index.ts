import { generateOptions } from '@tencent/micro-frontend-shared/util';
export * from './org';
export * from './auth';
export * from './tool';
export * from './toollib';
export * from './node';

export const DEFAULT_PAGER = {
  count: 0,
  pageSize: 10,
  pageStart: 0,
};

export const DEFAULT_TEAM_PAGER = {
  count: 0,
  pageSize: 12,
  pageStart: 0,
  allLoaded: true,
};

export enum RepoTypeEnum {
  GIT = 'git',
  SVN = 'svn'
}

export const REPO_TYPE_CHOICES = {
  [RepoTypeEnum.GIT]: 'GIT',
  [RepoTypeEnum.SVN]: 'SVN',
};

export const REPO_TYPE_OPTIONS = generateOptions(REPO_TYPE_CHOICES);
