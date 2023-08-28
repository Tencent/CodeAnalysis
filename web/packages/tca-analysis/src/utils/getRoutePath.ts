// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================
import { formatBlankHref } from '@plat/routes';
import { isTrue } from '@tencent/micro-frontend-shared/util';

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
 * 获取团队基础路由前缀
 * @param orgSid
 * @param name
 */
export const getGroupBaseRouter = (orgSid: string) => `/t/${orgSid}`;

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
 * 代码分析基础路由
 * @returns
 */
export const getAnalysisBaseRouter =  (orgSid: string, name: string) => `${getBaseRouter(orgSid, name)}/code-analysis`;

/** 代码分析-分析项目基础路由 */
const getAnalysisProjectBaseRouter = (orgSid: string, name: string) => {
  const analysisBasePath = getAnalysisBaseRouter(orgSid, name);
  if (isTrue(process.env.ENABLE_ANALYSIS_PREFIX_EXACT_MATCH)) {
    return `${analysisBasePath}/project`;
  }
  return analysisBasePath;
};

/** 代码分析-分析方案基础路由 */
const getAnalysisSchemeBaseRouter = (orgSid: string, name: string) => {
  const analysisBasePath = getAnalysisBaseRouter(orgSid, name);
  if (isTrue(process.env.ENABLE_ANALYSIS_PREFIX_EXACT_MATCH)) {
    return `${analysisBasePath}/scheme`;
  }
  return analysisBasePath;
};

/**
 * 获取分析项目路由前缀
 * @param {string} [projectPath] - coding项目名
 * @param {string | number} repoId - 仓库ID
 * @param {string | number} [projectId] - 项目ID
 */
export const getProjectRouter = (orgSid: string, name: string, repoId: string | number, projectId?: string | number) => `${getAnalysisProjectBaseRouter(orgSid, name)}/repos/${repoId}/projects${projectId ? `/${projectId}` : ''}`;

export const getProjectBlankRouter = (
  orgSid: string,
  name: string,
  repoId: string | number,
  projectId?: string | number,
) => formatBlankHref(getProjectRouter(orgSid, name, repoId, projectId));

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
) => `${getAnalysisSchemeBaseRouter(orgSid, name)}/repos/${repoId}/schemes${schemeId ? `/${schemeId}` : ''}`;

export const getSchemeBlankRouter = (
  orgSid: string,
  name: string,
  repoId: string | number,
  schemeId?: string | number,
) => formatBlankHref(getSchemeRouter(orgSid, name, repoId, schemeId));

export const getTmplRouter = (orgSid: string) => `${getGroupBaseRouter(orgSid)}/template`;

export const getTmplBlankRouter = (orgSid: string) => formatBlankHref(getTmplRouter(orgSid));

/**
 * 工具管理路由
 * @param orgSid
 * @param teamName
 * @param tab
 * @returns
 */
export const getToolsRouter = (orgSid: string, toolId: number, tab: string) => `/t/${orgSid}/tools/${toolId}/${tab}`;

export const getTeamMemberRouter = (orgSid: string) => `/t/${orgSid}/members`;

/** 用户凭证管理路由 */
export const getUserAuthRouter = () => '/user/auth';

export const getUserAuthBlankRouter = () => formatBlankHref(getUserAuthRouter());
