import { MAIN_SERVER_API, get, put, post, del } from '@plat/api';

/**
 * 获取团队列表
 * @param params 筛选参数
 */
export const getTeams = (params: any = null) => get(`${MAIN_SERVER_API}/orgs/`, params);

/**
 * 创建团队
 * @param params 参数
 */
export const createTeam = (params: any) => post(`${MAIN_SERVER_API}/orgs/`, params);

/**
 * 禁用团队
 * @param orgSid 团队唯一标识
 * @param params 参数
 */
export const disableTeam = (orgSid: string, params: any) => put(`${MAIN_SERVER_API}/orgs/${orgSid}/status/`, params);

/**
 * 获取团队详情
 * @param orgSid 团队唯一标识
 */
export const getTeamInfo = (orgSid: string) => get(`${MAIN_SERVER_API}/orgs/${orgSid}/`);

/**
 * 更新团队信息
 * @param params: any
 */
export const updateTeamInfo = (orgSid: string, params: any) => put(`${MAIN_SERVER_API}/orgs/${orgSid}/`, params);

/**
 * 获取团队成员
 * @param orgSid 团队唯一标识
 */
export const getTeamMember = (orgSid: string) => get(`${MAIN_SERVER_API}/orgs/${orgSid}/memberconf/`);

/**
 * 通过邀请码添加团队成员
 * @param params: any
 */
export const addMemberByInvite = (code: string) => post(`${MAIN_SERVER_API}/orgs/invited/${code}/`, null);

/**
 * 获取团队成员邀请码
 * @param orgSid 团队唯一标识
 */
export const getInviteCode = (orgSid: string, params: any) => post(`${MAIN_SERVER_API}/orgs/${orgSid}/memberconf/`, params);

/**
 * 移除成员
 * @param orgSid 团队唯一标识
 * @param role 角色
 * @param username 用户UID
 * @returns
 */
export const removeMember = (orgSid: string, role: number, username: string) => del(`${MAIN_SERVER_API}/orgs/${orgSid}/memberconf/${role}/${username}/`);

/**
 * 获取项目列表
 * @param orgSid 团队唯一标识
 * @param params 筛选参数
 */
export const getProjects = (orgSid: string, params?: any) => get(`${MAIN_SERVER_API}/orgs/${orgSid}/teams/`, params);

/**
 * 创建项目
 * @param orgSid
 * @param params
 */
export const createProject = (orgSid: string, params: any) => post(`${MAIN_SERVER_API}/orgs/${orgSid}/teams/`, params);

/**
 * 获取团队代码库
 * @param orgSid 团队唯一标识
 * @param params 筛选参数
 */
export const getTeamRepos = (orgSid: string, params: any = null) => get(`${MAIN_SERVER_API}/orgs/${orgSid}/repos/`, params);
