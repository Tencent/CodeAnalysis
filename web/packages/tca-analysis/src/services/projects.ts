// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * description      分析项目请求
 * author           luochunlan@coding.net
 * create at        2020-10-23
 */
import { MAIN_SERVER, MAIN_SERVER_API, ANALYSIS_SERVER_API, get, put, post, del, postFile, getFile } from '@plat/api';
import {  getMainBaseURL, getAnalysisBaseURL } from './common';

const getProjectBaseURL = (orgSid: string, teamName: string, repoId: string | number, projectId: number) => `${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}`;

/**
 * 获取分析项目
 * @param repoId - 代码库ID
 * @param query - 查询参数
 */
export const getProjects = (orgSid: string, teamName: string, repoId: string | number, query: any) => get(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/projects/`, query);

/**
 * 新建分析项目
 * @param repoId - 代码库ID
 * @param data
 */
export const createProject = (orgSid: string, teamName: string, repoId: string | number, data: any) => post(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/projects/`, data);

/**
 * 启动分析
 * @param orgSid
 * @param teamName
 * @param repoId
 * @param projectId
 * @param data
 */
export const createJob = (orgSid: string, teamName: string, repoId: string | number, projectId: string | number, data: any) => post(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/scans/`, data);

/**
 * 获取分析项目信息
 * @param repoId - 代码库ID
 * @param projectId - 项目ID
 */
export const getProjectDetail = (orgSid: string, teamName: string, repoId: string | number, projectId: string | number) => get(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/`);

/**
 * 获取分析项目信息
 * @param repoId - 代码库ID
 * @param projectId - 项目ID
 */
export const delProject = (orgSid: string, teamName: string, repoId: string | number, projectId: string | number) => del(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/`);

/**
 * 获取指定代码库下与 CodeDog 关联的分支
 * @param repoId - 代码库ID
 */
export const getBranchs = (orgSid: string, teamName: string, repoId: number) => get(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/branchnames/`, { offset: 0, limit: 500 });

/**
 * 获取指定分支关联的分析方案
 * @param repoId - 代码库ID
 * @param branch - 分支名称
 */
export const getSchemesByBranch = (orgSid: string, teamName: string, repoId: number, branch: string) => get(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/branch/projects/`, { branch, scheme_status: 1 });

/**
 * 开启第一次代码分析
 * @param repoId
 * @param data
 */
export const initRepos = (orgSid: string, teamName: string, repoId: number, data: any) => post(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/init/`, data);

/**
 * 本地分析 - 下载配置文件
 * @param orgSid
 * @param teamName
 * @param repoId
 * @param projectId
 * @param data: {source_dir: 本地代码绝对路径, total_scan: 是否全量分析}
 */
export const downloadIniFile = (orgSid: string, teamName: string, repoId: number, projectId: number, data: any) => {
  const env = `${window.location.origin}${MAIN_SERVER}`;
  return postFile(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/scans/puppyini/`, { codedog_env: env, ...data });
};
// ============================================ 分支概览 ============================================

/**
 * 获取代码检查最近问题信息
 * @param projectId 分析项目ID
 */
export const getLatestLintScans = (orgSid: string, teamName: string, repoId: number, projectId: number) => get(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/overview/lintscans/latest/`);

/**
 * 获取代码检查历史详情数据
 * @param projectId 分析项目ID
 * @param query 查询参数
 */
export const getLintScans = (orgSid: string, teamName: string, repoId: number, projectId: number, query?: any) => get(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/overview/lintscans/`, query);

/**
 * 获取圈复杂度历史详情数据
 * @param projectId 分析项目ID
 * @param query 查询参数
 */
export const getCCScans = (orgSid: string, teamName: string, repoId: number, projectId: number, query?: any) => get(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/overview/cycscans/`, query);

/**
 * 获取重复代码历史详情数据
 * @param projectId 分析项目ID
 * @param query 查询参数
 */
export const getDupScans = (orgSid: string, teamName: string, repoId: number, projectId: number, query?: any) => get(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/overview/dupscans/`, query);

/**
 * 获取代码统计历史详情数据
 * @param projectId 分析项目ID
 * @param query 查询参数
 */
export const getClocScans = (orgSid: string, teamName: string, repoId: number, projectId: number, query?: any) => get(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/overview/clocscans/`, query);

/**
 * 获取与我相关的数据
 * @param projectId 分析项目ID
 */
export const getMineOverview = (orgSid: string, teamName: string, repoId: number, projectId: number) => get(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/overview/mine/`);

// ============================================ 问题列表 ============================================

/**
 * 问题列表 - 获取问题列表数据
 * @param projectId
 * @param query
 */
export const getIssues = (orgSid: string, teamName: string, repoId: number, projectId: number, query: any) => get(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codelint/issues/`, query);

/**
 * 问题列表 - 批量处理问题
 * @param projectId
 * @param data
 */
export const handleIssues = (orgSid: string, teamName: string, repoId: number, projectId: number, data: any) => put(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codelint/issues/resolution/`, data);

/**
 * 问题列表 - 获取问题详情
 * @param projectId
 * @param issueId
 */
export const getIssueDetail = (orgSid: string, teamName: string, repoId: number, projectId: number, issueId: number) => get(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codelint/issues/${issueId}/`);

/**
 * 问题列表 - 文件代码
 * @param projectId
 * @param data
 */
export const getCodeFile = (orgSid: string, teamName: string, repoId: number, projectId: number, data: any) => get(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codefile/`, data);

/**
 * 问题列表 - 获取指定 issue 操作记录
 * @param projectId
 * @param issueId
 */
export const getIssueDetailComments = (orgSid: string, teamName: string, repoId: number, projectId: number, issueId: number) => get(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codelint/issues/${issueId}/comments/`);

/**
 * 问题列表 - 更新指定 issue 的严重级别
 * @param projectId
 * @param issueId
 * @param severity - 严重级别
 */
export const updateIssueSeverity = (orgSid: string, teamName: string, repoId: number, projectId: number, issueId: number, severity: number) => put(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codelint/issues/${issueId}/severity/`, {
  severity,
});

/**
 * 问题列表 - 更新指定 issue 的责任人
 * @param projectId
 * @param issueId
 * @param author - 责任人
 */
export const updateIssueAuthor = (orgSid: string, teamName: string, repoId: number, projectId: number, issueId: number, author: string) => put(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codelint/issues/${issueId}/author/`, {
  author,
});

/**
 * 问题列表 - 批量更新问题责任人
 * @param orgSid
 * @param teamName
 * @param repoId
 * @param projectId
 * @param data
 */
export const updateIssuesAuthor = (orgSid: string, teamName: string, repoId: number, projectId: number, data: any) => put(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codelint/issues/author/`, data);

/**
 * 问题列表 - 忽略问题
 * @param projectId
 * @param issueId
 * @param data
 */
export const resoluteIssue = (
  orgSid: string,
  teamName: string,
  repoId: number,
  projectId: number,
  issueId: number,
  data: any,
) => put(
  `${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codelint/issues/${issueId}/resolution/`,
  data,
);

/**
 * 代码统计 目录和文件列表
 * @param projectId 分析项目id
 * @param path  查询路径
 */
export const getClocFiles = (orgSid: string, teamName: string, repoId: number, projectId: number | string, path = '') => get(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codemetric/clocs/`, { path });

/**
 * 获取代码统计的项目语言分布
 * @param projectId 分析项目id
 * @param data 筛选参数
 */
export const getClocLangs = (orgSid: string, teamName: string, repoId: number, projectId: number | string, data: any = { limit: 100 }) => get(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codemetric/cloclangs/`, data);

// ============================================ 度量结果 ============================================
/**
 * 圈复杂度 - 获取圈复杂度文件列表，issue列表数据
 * @param projectId 分析项目ID
 * @param query 查询参数
 */
export const getCCFilesIssues = (orgSid: string, teamName: string, repoId: number, projectId: number, query: any) => get(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codemetric/ccfiles/`, query);

/**
 * 圈复杂度 - 获取圈复杂度方法列表，issue列表数据
 * @param projectId 分析项目ID
 * @param query 查询参数
 */
export const getCCFunIssues = (orgSid: string, teamName: string, repoId: number, projectId: number, query: any) => get(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codemetric/ccissues/`, query);

/**
 * 圈复杂度 - 获取圈复杂度文件详情
 * @param projectId 分析项目ID
 * @param fileId 文件ID
 */
export const getCCFileDetail = (orgSid: string, teamName: string, repoId: number, projectId: number, fileId: any) => get(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codemetric/ccfiles/${fileId}/`);

/**
 * 圈复杂度 - 获取圈复杂度文件issue详情
 * @param projectId 分析项目ID
 * @param issueId 问题ID
 */
export const getCCIssueDetail = (orgSid: string, teamName: string, repoId: number, projectId: number, issueId: any) => get(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codemetric/ccissues/${issueId}/`);


/**
* 圈复杂度 - 获取圈复杂度文件评论
* @param projectId 分析项目ID
* @param fileId 文件ID
* @param query 查询参数
*/
export const getCCFileDetailComments = (orgSid: string, teamName: string, repoId: number, projectId: number, fileId: any, query: any) => get(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codemetric/ccfiles/${fileId}/comments/`, query);

/**
 * 圈复杂度 - 获取圈复杂度文件issue列表
 * @param projectId 分析项目ID
 * @param fileId 文件ID
 * @param query 查询参数
 */
export const getCCFileIssues = (orgSid: string, teamName: string, repoId: number, projectId: number, fileId: any, query: any) => get(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codemetric/ccfiles/${fileId}/ccissues/`, query);

export const setCCIssueStatus = (orgSid: string, teamName: string, repoId: number, projectId: number, putData: any) => put(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codemetric/ccissues/status/`, putData);

export const modifyIssueResolution = (orgSid: string, teamName: string, repoId: number, projectId: number, issueId: any, putData: any) => put(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codelint/issues/${issueId}/resolution/`, putData);

export const modifyIssueSeverity = (orgSid: string, teamName: string, repoId: number, projectId: number, issueId: any, putData: any) => put(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codelint/issues/${issueId}/severity/`, putData);

export const modifyIssueAuthor = (orgSid: string, teamName: string, repoId: number, projectId: number, issueId: any, putData: any) => put(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codelint/issues/${issueId}/author/`, putData);

export const modifyCCIssueAuthor = (orgSid: string, teamName: string, repoId: number, projectId: number, issueId: any, putData: any) => put(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codemetric/ccissues/${issueId}/author/`, putData);

/**
 * 重复代码 - 获取重复代码列表数据
 * @param projectId
 * @param query
 */
export const getDupIssues = (orgSid: string, teamName: string, repoId: number, projectId: number, query: any) => get(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codemetric/dupfiles/`, query);

/**
 * 重复代码 - 获取重复代码问题详情
 * @param projectId
 * @param issueId
 */
export const getDupIssuesDetail = (orgSid: string, teamName: string, repoId: number, projectId: number, issueId: any) => get(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codemetric/dupfiles/${issueId}/`);

/**
 * 重复代码 - 获取重复代码块详情
 * @param projectId
 * @param issueId
 * @param query
 */
export const getDupFileBlocks = (orgSid: string, teamName: string, repoId: number, projectId: number, issueId: any, query: any) => get(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codemetric/dupfiles/${issueId}/blocks/`, query);

/**
 * 重复代码 - 获取重复代码块关联代码块
 * @param projectId
 * @param issueId
 * @param blockId
 * @param query
 */
export const getDupFileBlockRelatedBlocks = (orgSid: string, teamName: string, repoId: number, projectId: number, issueId: any, blockId: any, query: any) => get(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codemetric/dupfiles/${issueId}/blocks/${blockId}/related/`, query);


/**
 * 重复代码 - 获取重复代码内容
 * @param projectId
 * @param query
 */
export const getDupCodeFile = (orgSid: string, teamName: string, repoId: number, projectId: number, query: any) => get(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codefile/`, query);

/**
 * 重复代码 - 获取重复代码块详情
 * @param projectId
 * @param issueId
 * @param blockId
 */
export const getDupFileBlockDetail = (orgSid: string, teamName: string, repoId: number, projectId: number, issueId: any, blockId: any) => get(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codemetric/dupfiles/${issueId}/blocks/${blockId}/`);

/**
 * 重复代码 - 修改重复代码问题状态
 * @param projectId
 * @param issueId
 * @param putData
 */
export const modifyDupFileIssueState = (orgSid: string, teamName: string, repoId: number, projectId: number, issueId: any, putData: any) => put(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codemetric/dupissues/${issueId}/state/`, putData);

/**
 * 重复代码 - 修改重复代码问题责任人
 * @param projectId
 * @param issueId
 * @param putData
 */
export const modifyDupFileIssueAuthor = (orgSid: string, teamName: string, repoId: number, projectId: number, issueId: any, putData: any) => put(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codemetric/dupissues/${issueId}/owner/`, putData);

/**
 * 重复代码 - 获取重复率趋势
 * @param projectId
 * @param issueId
 */
export const getDupFileHistory = (orgSid: string, teamName: string, repoId: number, projectId: number, issueId: any) => get(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codemetric/dupfiles/${issueId}/history/`);

/**
 * 重复代码 - 获取重复率操作历史
 * @param projectId
 * @param issueId
 */
export const getDupFileIssueComments = (orgSid: string, teamName: string, repoId: number, projectId: number, issueId: any) => get(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/codemetric/dupissues/${issueId}/comments/`);

// ============================================ 分析历史 ============================================

/**
 * 分析历史 - 获取分析历史数据
 * @param projectId - 分析项目ID
 * @param query - 查询参数
 */
export const getScans = (orgSid: string, teamName: string, repoId: number, projectId: number, query: any) => get(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/scans/`, query);

/**
 * 获取分析历史结果
 * @param orgSid
 * @param teamName
 * @param repoId
 * @param projectId
 * @param scanId
 */
export const getScansResult = (orgSid: string, teamName: string, repoId: number, projectId: number, scanId: number) => get(`${getAnalysisBaseURL(orgSid, teamName)}/repos/${repoId}/projects/${projectId}/scans/${scanId}/`);


/**
 * 分析历史 - 获取分析历史详情
 * @param orgSid
 * @param teamName
 * @param repoId
 * @param projectId
 * @param jobId
 */
export const getScanDetail = (orgSid: string, teamName: string, repoId: number, projectId: number, jobId: number) => get(`${getProjectBaseURL(orgSid, teamName, repoId, projectId)}/jobs/${jobId}/`);

/**
 * 分析历史 - 获取分析历史详情 - 子任务详细信息
 * @param orgSid
 * @param teamName
 * @param repoId
 * @param projectId
 * @param jobId
 * @param taskId
 */
export const getTaskDetail = (orgSid: string, teamName: string, repoId: number, projectId: number, jobId: number, taskId: number) => get(`${getProjectBaseURL(orgSid, teamName, repoId, projectId)}/jobs/${jobId}/tasks/${taskId}/`);

/**
 * 分析历史 - 取消分析
 * @param jobId
 */
export const cancelScan = (orgSid: string, teamName: string, repoId: number, projectId: number, jobId: number) => post(`${MAIN_SERVER_API}/orgs/${orgSid}/teams/${teamName}/repos/${repoId}/projects/${projectId}/jobs/${jobId}/cancel/`, { remarks: '用户取消' });


export const getLog = (url: string) => getFile(url);

// ============================================ 扩展功能 ============================================

/**
 * 获取扩展功能列表
 * @param repoId - 代码库ID
 * @param projectId - 项目ID
 * @param query
 */
export const getCodeTools = (repoId: number, projectId: number, query: any) => get(`${MAIN_SERVER_API}/repos/${repoId}/projects/${projectId}/codetools/`, query);

/**
 * 扩展功能 - 获取指定工具的详细信息
 * @param repoId - 代码库ID
 * @param projectId - 项目ID
 * @param toolName - 工具名
 */
export const getCodeToolDetail = (repoId: number, projectId: number, toolName: string) => get(`${MAIN_SERVER_API}/repos/${repoId}/projects/${projectId}/codetools/${toolName}/`);

/**
 * 扩展功能 - 获取指定工具的启动参数
 * @param repoId - 代码库ID
 * @param projectId - 项目ID
 * @param toolName - 工具名
 */
export const getCodeToolParams = (repoId: number, projectId: number, toolName: string) => get(`${MAIN_SERVER_API}/repos/${repoId}/projects/${projectId}/codetools/${toolName}/params/`);

/**
 * 扩展功能 - 获取指定工具的分析列表
 * @param projectId - 项目ID
 * @param toolName - 工具名
 * @param query - 查询参数
 */
export const getCodeToolScans = (projectId: number, toolName: string, query: any) => get(`${ANALYSIS_SERVER_API}/projects/${projectId}/codetools/${toolName}/scans/`, query);

/**
 * 扩展功能 - 启动任务
 * @param repoId - 代码库ID
 * @param projectId - 项目ID
 * @param toolName - 工具名
 * @param data - 启动参数
 */
export const createToolScans = (repoId: number, projectId: number, toolName: string, data: any) => post(`${MAIN_SERVER_API}/repos/${repoId}/projects/${projectId}/codetools/${toolName}/scans/`, {
  task_params: data,
});
