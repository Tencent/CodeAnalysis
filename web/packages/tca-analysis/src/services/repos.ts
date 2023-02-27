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
import { MAIN_SERVER_API, get, post, put, del } from '@plat/api';
import { getMainBaseURL } from './common';

/**
 * 获取http凭证列表
 * @param query - 查询参数
 */
export const getScmAccounts = () => get(`${MAIN_SERVER_API}/authen/scmaccounts/`, { limit: 200 });

/**
 * 获取SSH凭证列表
 */
export const getSSHInfo = () => get(`${MAIN_SERVER_API}/authen/scmsshinfos/`, { limit: 200 });

/**
 * 查询所有OAuth授权状况
 */
export const getOAuthInfo = () => get(`${MAIN_SERVER_API}/authen/scmauthinfos/`);

/**
 * 查询OAuth授权配置状况
 * @param scm_platform_name 平台名
 */
export const getPlatformStatus = (param: any = null) => get(`${MAIN_SERVER_API}/authen/oauthsettings/`, param);

/**
 * 登记代码库
 * @param data: { name: 代码库名称, scm_type: 代码库来源 git/svn, scm_url: 代码库地址 }
 */
export const postRepo = (orgSid: string, name: string, data: any) => post(`${getMainBaseURL(orgSid, name)}/repos/`, data);

/**
 * 认证方式
 * @param repoId: 代码库id
 * @param scmAuth
 */
export const putRepoAuth = (orgSid: string, teamName: string, repoId: any, scmAuth: any) => put(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/auth/`, { scm_auth: scmAuth });

/**
 * 获取代码库概览
 * @param repoId: 代码库id
 */
export const getRepo = (orgSid: string, teamName: string, repoId: any) => get(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/`);

/**
 * 代码库概览
 * @param repoId: 代码库id
 */
export const putRepo = (orgSid: string, teamName: string, repoId: any, data: any) => put(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/`, data);

/**
 * 获取代码库成员
 * @param orgSid
 * @param teamName
 * @param repoId
 * @returns
 */
export const getRepoMembers = (orgSid: string, teamName: string, repoId: any) => get(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/memberconf/`);


/**
 * 添加代码库成员
 * @param orgSid
 * @param teamName
 * @param repoId
 * @param data
 * @returns
 */
export const postRepoMembers = (orgSid: string, teamName: string, repoId: any, data: any) => post(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/memberconf/`, data);

/**
 * 删除代码库成员
 * @param orgSid
 * @param teamName
 * @param repoId
 * @param username
 * @returns
 */
export const delRepoMembers = (orgSid: string, teamName: string, repoId: any, username: string) => del(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/memberconf/1/${username}/`);

/**
 * 删除代码库
 * @param repoId: 代码库id
 */
export const delRepo = (orgSid: string, teamName: string, repoId: any) => del(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/`);

/**
 * 关注关注代码库
 * @param repoId
 * @returns
 */
export const subscribedRepo = (orgSid: string, teamName: string, repoId: number) => post(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/subscribed/`, {});

/**
 * 取消关注代码库
 * @param repoId
 * @returns
 */
export const cancelSubscribedRepo = (orgSid: string, teamName: string, repoId: number) => del(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/subscribed/`);
