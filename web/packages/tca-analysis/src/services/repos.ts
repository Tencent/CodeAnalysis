// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * description      分支项目请求
 * author           luochunlan@coding.net
 * create at        2020-10-23
 */
import { get, post, put } from './index';
import { MAIN_SERVER_API, getMainBaseURL } from './common';

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
 * 登记代码库
 * @param data: { name: 代码库名称, scm_type: 代码库来源 git/svn, scm_url: 代码库地址 }
 */
export const postRepo = (org_sid: string, name: string, data: any) => post(`${getMainBaseURL(org_sid, name)}/repos/`, data);

/**
 * 认证方式
 * @param repoId: 代码库id
 */
export const putRepoAuth = (orgSid: string, teamName: string, repoId: any, data: any) => put(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/auth/`, data);

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
 * 添加代码库成员
 * @param orgSid
 * @param teamName
 * @param repoId
 * @param data
 * @returns
 */
export const postRepoMembers = (orgSid: string, teamName: string, repoId: any, data: any) => post(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/memberconf/`, data);
