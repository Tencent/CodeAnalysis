import { get, post, put, del, MAIN_SERVER_API } from '@plat/api';

const getNodePrefix = (orgId: string) => `${MAIN_SERVER_API}/orgs/${orgId}/nodes/`;

/**
 * 获取节点列表
 * @param orgId
 * @param params 筛选参数
 */
export const getNodes = (orgId: string, params: any = null) => get(getNodePrefix(orgId), params);

/**
 * 获取节点详情
 * @param orgId
 * @param nodeId
 */
export const getNode = (orgId: string, nodeId: number | string) => get(`${getNodePrefix(orgId)}${nodeId}/`);

/**
 * 更新节点详情
 * @param orgId
 * @param nodeId
 * @param data 更新数据
 */
export const putNode = (orgId: string, nodeId: number | string, data: any) => put(`${getNodePrefix(orgId)}${nodeId}/`, data);

/**
 * 删除节点
 * @param orgId
 * @param nodeId
 */
export const delNode = (orgId: string, nodeId: number | string) => del(`${getNodePrefix(orgId)}${nodeId}/`);

/**
 * 获取节点进程
 * @param orgId
 * @param nodeId
 */
export const getNodeProcess = (orgId: string, nodeId: number | string) => get(`${getNodePrefix(orgId)}${nodeId}/processes/`);

/**
 * 更新节点进程
 * @param orgId
 * @param nodeId
 * @param data 节点信息
 */
export const putNodeProcess = (orgId: string, nodeId: number | string, data: any) => put(`${getNodePrefix(orgId)}${nodeId}/processes/`, data);

/**
 * 查看节点执行任务列表
 * @param orgId
 * @param nodeId
 * @param params 筛选项
 */
export const getNodeTask = (orgId: string, nodeId: number | string, params: any) => get(`${getNodePrefix(orgId)}${nodeId}/tasks/`, params);

/**
 * 获取标签列表
 * @param orgId
 * @param params 筛选参数
 */
export const getTags = (orgId: string, params: any = null) => get(`${getNodePrefix(orgId)}tags/`, params);

/**
 * 创建标签
 * @param orgId
 * @param data 标签信息
 */
export const postTags = (orgId: string, params: any = null) => post(`${getNodePrefix(orgId)}tags/`, params);

/**
 * 更新标签
 * @param orgId
 * @param data 标签信息
 */
export const putTag = (orgId: string, tagId: number | string, params: any = null) => put(`${getNodePrefix(orgId)}tags/${tagId}/`, params);

/**
 * 删除标签
 * @param orgId
 */
export const delTag = (orgId: string, tagId: number | string) => del(`${getNodePrefix(orgId)}tags/${tagId}/`);
