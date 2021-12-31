import qs from 'qs';
import { getProjectRouter } from '@src/utils/getRoutePath';
/**
 * 获取分支项目代码检查issue列表路由前缀
 * @param repoId 代码库ID
 * @param projectId 分支项目ID
 * @param query 筛选参数
 */
export const getProjectLintIssueRouter = (
  orgSid: string,
  teamName: string,
  repoId: string | number,
  projectId: string | number,
  query?: any,
) => `${getProjectRouter(orgSid, teamName, repoId, projectId)}/codelint-issues${query ? `?${qs.stringify(query)}` : ''
}`;

/**
* 获取分支项目圈复杂度方法issue列表路由前缀
* @param repoId 代码库ID
* @param projectId 分支项目ID
* @param query 筛选参数
*/
export const getProjectCCFunIssueRouter = (
  orgSid: string,
  teamName: string,
  repoId: string | number,
  projectId: string | number,
  query?: any,
) => `${getProjectRouter(orgSid, teamName, repoId, projectId)}/metric/ccissues${query ? `?${qs.stringify(query)}` : ''
}`;

/**
* 获取分支项目圈复杂度文件issue列表路由前缀
* @param repoId 代码库ID
* @param projectId 分支项目ID
* @param query 筛选参数
*/
export const getProjectCCFileIssueRouter = (
  orgSid: string,
  teamName: string,
  repoId: string | number,
  projectId: string | number,
  query?: any,
) => `${getProjectRouter(orgSid, teamName, repoId, projectId)}/metric/ccfiles${query ? `?${qs.stringify(query)}` : ''
}`;

/**
* 获取分支项目重复代码issue列表路由前缀
* @param repoId 代码库ID
* @param projectId 分支项目ID
* @param query 筛选参数
*/
export const getProjectDupIssueRouter = (
  orgSid: string,
  teamName: string,
  repoId: string | number,
  projectId: string | number,
  query?: any,
) => `${getProjectRouter(orgSid, teamName, repoId, projectId)}/metric/dupfiles${query ? `?${qs.stringify(query)}` : ''
}`;


export const getProjectScanRouter = (
  orgSid: string,
  teamName: string, repoId: string | number, projectId: string | number,
) => `${getProjectRouter(orgSid, teamName, repoId, projectId)}/scan-history`;
