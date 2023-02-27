// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import { MAIN_SERVER_API, ANALYSIS_SERVER_API, LOGIN_SERVER_API, get, put, post, del } from '@plat/api';

export const getBaseURL = (orgSid: string, teamName: string) => `/orgs/${orgSid}/teams/${teamName}`;

export const getMainBaseURL = (orgSid: string, teamName: string) => `${MAIN_SERVER_API}${getBaseURL(orgSid, teamName)}`;

export const getAnalysisBaseURL = (orgSid: string, teamName: string) => `${ANALYSIS_SERVER_API}${getBaseURL(orgSid, teamName)}`;

/**
 * 获取代码库列表
 * @param query
 */
export const getRepos = (orgSid: string, teamName: string, query: any) => get(`${MAIN_SERVER_API}/orgs/${orgSid}/teams/${teamName}/repos/`, { ...query, scope: 'all' });

/**
 * 根据用户UID获取用户信息
 * @param uid
 */
export const getUIDUserInfo = (uid: string) => get(`${LOGIN_SERVER_API}/login/users/${uid}/`);

/*
 * 获取指定代码库下的成员权限
 * @param repoId
 */
export const getMembers = (orgSid: string, teamName: string, repoId: any) => get(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/memberconf/`);

/**
 * 获取项目信息
 * @param orgSid
 * @param teamName
 */
export const getProjectTeam = (orgSid: string, teamName: string) => get(`${getMainBaseURL(orgSid, teamName)}/`);

/**
 * 更新项目信息
 * @param orgSid
 * @param teamName
 * @param data
 */
export const putProjectTeam = (orgSid: string, teamName: string, data: any) => put(`${getMainBaseURL(orgSid, teamName)}/`, data);

/**
 * 获取项目成员
 * @param orgSid
 * @param teamName
 */
export const getProjectTeamMembers = (orgSid: string, teamName: string) => get(`${getMainBaseURL(orgSid, teamName)}/memberconf/`);

/**
 * 添加项目成员
 * @param orgSid
 * @param teamName
 * @param data
 */
export const postProjectTeamMembers = (orgSid: string, teamName: string, data: any) => post(`${getMainBaseURL(orgSid, teamName)}/memberconf/`, data);

/**
 * 移除项目成员
 * @param orgSid
 * @param teamName
 * @param role
 * @param username
 * @returns
 */
export const delProjectTeamMember = (orgSid: string, teamName: string, role: number, username: string) => del(`${getMainBaseURL(orgSid, teamName)}/memberconf/${role}/${username}/`);

/**
 * 获取团队成员列表
 * @param orgSid
 */
export const getOrgMembers = (orgSid: string) => get(`${MAIN_SERVER_API}/orgs/${orgSid}/memberconf/`);

/**
 * 禁用团队项目
 * @param orgSid
 * @param teamName
 * @param params
 */
export const disableProject = (orgSid: string, teamName: string, params: any) => put(`${getMainBaseURL(orgSid, teamName)}/status/`, params);
