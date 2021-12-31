
/**
 * 获取基础路由前缀
 * @param org_sid
 * @param name
 */

export const getBaseRouter = (org_sid: string, name: string) => `/t/${org_sid}/p/${name}`;

/**
 * 获取代码库路由前缀
 * @param org_sid
 * @param name
 */
export const getReposRouter = (org_sid: string, name: string) => `/t/${org_sid}/p/${name}/repos`;

/**
 * 获取分支项目路由前缀
 * @param {string} [projectPath] - coding项目名
 * @param {string | number} repoId - 仓库ID
 * @param {string | number} [projectId] - 项目ID
 */
export const getProjectRouter = (org_sid: string, name: string, repoId: string | number, projectId?: string | number) => `${getBaseRouter(org_sid, name)}/code-analysis/repos/${repoId}/projects${projectId ? `/${projectId}` : ''}`;

/**
 * 获取分析方案路由前缀
 * @param {string} [projectPath] - coding项目名
 * @param {string | number} repoId - 仓库ID
 * @param {string | number} [schemeId] - 分析方案ID
 */
export const getSchemeRouter = (
  org_sid: string,
  name: string,
  repoId: string | number,
  schemeId?: string | number,
) => `${getBaseRouter(org_sid, name)}/code-analysis/repos/${repoId}/schemes${schemeId ? `/${schemeId}` : ''}`;

export const getTmplRouter = (orgSid: string, teamName: string) => `${getBaseRouter(orgSid, teamName)}/template`;

export const getTeamMemberRouter = (org_sid: string) => `/t/${org_sid}/members`;
