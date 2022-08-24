import { MAIN_SERVER_API, get, put } from './common';

/**
 *
 * @param params 获取项目组列表
 */
export const getTeams = (params: any = null) => get(`${MAIN_SERVER_API}/teams/`, params);

/**
 * 禁用/恢复项目组
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param params 参数
 */
export const putTeamStatus = (orgSid: string, teamName: string, params: any) => put(`${MAIN_SERVER_API}/orgs/${orgSid}/teams/${teamName}/status/`, params);
