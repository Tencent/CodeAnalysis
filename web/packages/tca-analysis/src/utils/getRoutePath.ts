// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================


/**
 * 获取项目列表路由地址
 * @param orgSid
 */
export const getProjectListRouter = (orgSid: string) => `/t/${orgSid}/projects`;

/**
 * 获取项目概览路由地址
 * @param orgSid
 * @param name
 */
export const getProjectOverviewRouter = (orgSid: string, name: string) => `/t/${orgSid}/p/${name}/profile`;

/**
 * 获取基础路由前缀
 * @param orgSid
 * @param name
 */
export const getBaseRouter = (orgSid: string, name: string) => `/t/${orgSid}/p/${name}`;

/**
 * 获取代码库路由前缀
 * @param orgSid
 * @param name
 */
export const getReposRouter = (orgSid: string, name: string) => `/t/${orgSid}/p/${name}/repos`;

/**
 * 获取分支项目路由前缀
 * @param {string} [projectPath] - coding项目名
 * @param {string | number} repoId - 仓库ID
 * @param {string | number} [projectId] - 项目ID
 */
export const getProjectRouter = (orgSid: string, name: string, repoId: string | number, projectId?: string | number) => `${getBaseRouter(orgSid, name)}/code-analysis/repos/${repoId}/projects${projectId ? `/${projectId}` : ''}`;

/**
 * 获取分析方案路由前缀
 * @param {string} [projectPath] - coding项目名
 * @param {string | number} repoId - 仓库ID
 * @param {string | number} [schemeId] - 分析方案ID
 */
export const getSchemeRouter = (
  orgSid: string,
  name: string,
  repoId: string | number,
  schemeId?: string | number,
) => `${getBaseRouter(orgSid, name)}/code-analysis/repos/${repoId}/schemes${schemeId ? `/${schemeId}` : ''}`;

export const getTmplRouter = (orgSid: string, teamName: string) => `${getBaseRouter(orgSid, teamName)}/template`;

/**
 * 工具管理路由
 * @param orgSid
 * @param teamName
 * @param tab
 * @returns
 */
export const getToolsRouter = (orgSid: string, toolId: number, tab: string) => `/t/${orgSid}/tools/${toolId}/${tab}`;

export const getTeamMemberRouter = (orgSid: string) => `/t/${orgSid}/members`;
