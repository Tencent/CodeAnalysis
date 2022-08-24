import { MAIN_SERVER_API, get, post, put } from './common';

/**
 * 获取团队列表
 * @param params 筛选参数
 */
export const getOrgs = (params: any = null) => get(`${MAIN_SERVER_API}/orgs/`, params);


/**
 * 获取团队信息
 * @param orgSid 团队唯一标识
 */
export const getOrg = (orgSid: string) => get(`${MAIN_SERVER_API}/orgs/${orgSid}/`);


/**
 * 更新审批单
 * @param applyId 审批单ID
 * @param params 参数
 */
export const putOrgsPerm = (applyId: number, params: any) => put(`${MAIN_SERVER_API}/orgs/perms/${applyId}/`, params);

export const postOrgLelel = (orgSid: string, params: any) => post(`${MAIN_SERVER_API}/orgs/${orgSid}/level/`, params);

/**
 * 禁用/恢复团队
 * @param orgSid 团队唯一标识
 * @param params 参数
 */
export const putOrgStatus = (orgSid: string, params: any) => put(`${MAIN_SERVER_API}/orgs/${orgSid}/status/`, params);
