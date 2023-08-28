export const DEFAULT_PAGER = {
  count: 0,
  pageSize: 10,
  pageStart: 0,
  current: 1,
};

/** 团队基础路由前缀 */
export const GROUP_BASE_ROUTE_PREFIX = '/t/:orgSid';

/** 基础路由前缀 */
export const BASE_ROUTE_PREFIX = '/t/:orgSid/p/:teamName';

/** 仓库登录路由前缀 */
export const REPOS_ROUTE_PREFIX = `${BASE_ROUTE_PREFIX}/repos`;

/** 分析项目路由前缀 */
export const PROJECT_ROUTE_PREFIX = `${BASE_ROUTE_PREFIX}/code-analysis/(project)?/repos/:repoId/projects/:projectId`;

/** 分析方案路由前缀 */
export const SCHEMES_ROUTE_PREFIX = `${BASE_ROUTE_PREFIX}/code-analysis/(scheme)?/repos/:repoId/schemes/:schemeId`;

/** 分析方案模板路由前缀 */
export const TMPL_ROUTE_PREFIX = `${GROUP_BASE_ROUTE_PREFIX}/template`;

export * from './rule';
export * from './scheme';
