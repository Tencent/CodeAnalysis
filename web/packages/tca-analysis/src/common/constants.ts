// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================


// 分页默认值
export const DEFAULT_PAGER = {
  count: 0,
  pageSize: 10,
  pageStart: 0,
};


export const BASE_ROUTE_PREFIX = '/t/:org_sid/p/:team_name';

export const REPOS_ROUTE_PREFIX = `${BASE_ROUTE_PREFIX}/repos`;

export const PROJECT_ROUTE_PREFIX = `${BASE_ROUTE_PREFIX}/code-analysis/repos/:repoId/projects/:projectId`;

export const SCHEMES_ROUTE_PREFIX = `${BASE_ROUTE_PREFIX}/code-analysis/repos/:repoId/schemes/:schemeId`;

export const TMPL_ROUTE_PREFIX = `${BASE_ROUTE_PREFIX}/template`;

export const SCM_PLATFORM = {
  1: '其他',
  2: '腾讯工蜂',
  3: 'CODING',
  4: 'GitHub',
  5: 'Gitee',
  6: 'GitLab',
};