/** 获取首页路由 */
export const getHomeRouter = () => '/';

/** 获取团队列表页路由 */
export const getTeamsRouter = () => '/teams';

/** 获取管理后台路由 */
export const getManageRouter = () => '/manage';

/** 获取团队首页路由 */
export const getTeamRouter = (orgSid: string) => `/t/${orgSid}`;

/** 获取团队工具列表路由 */
export const getToolsRouter = (orgSid: string) => `/t/${orgSid}/tools`;

/** 获取团队工作台路由 */
export const getWorkspaceRouter = (orgSid: string) => `/t/${orgSid}/workspace`;

/** 获取团队项目列表路由 */
export const getProjectsRouter = (orgSid: string) => `/t/${orgSid}/projects`;

/** 获取团队项目组路由 */
export const getProjectRouter = (orgSid: string, name: string) => `/t/${orgSid}/p/${name}`;

/** 获取代码分析代码库分支项目列表路由 */
export const getRepoRouter = (orgSid: string, teamName: string, repoId: number | string) => `/t/${orgSid}/p/${teamName}/code-analysis/repos/${repoId}/projects`;

/** 获取代码分析分支项目概览页路由 */
export const getRepoProjectRouter = (orgSid: string, teamName: string, repoId: number | string, projectId: number | string) => `/t/${orgSid}/p/${teamName}/code-analysis/repos/${repoId}/projects/${projectId}/overview`;

/** 获取个人中心用户信息路由 */
export const getUserProfileRouter = () => '/user/profile';

/** 获取个人中心凭证管理路由 */
export const getUserAuthRouter = () => '/user/auth';
