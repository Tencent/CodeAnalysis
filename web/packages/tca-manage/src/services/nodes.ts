import { get, post, put, del } from './index';
import { MAIN_SERVER_API } from './common';

/**
 * 获取节点列表
 * @param params 筛选参数
 */
export const getNodes = (params: any = null) => get(`${MAIN_SERVER_API}/nodes/`, params);

export const getNode = (nodeId: number | string) => get(`${MAIN_SERVER_API}/nodes/${nodeId}/`);

export const putNode = (nodeId: number | string, params: any) => put(`${MAIN_SERVER_API}/nodes/${nodeId}/`, params);

export const delNode = (nodeId: number | string) => del(`${MAIN_SERVER_API}/nodes/${nodeId}/`);

export const getNodeProcess = (nodeId: number | string) => get(`${MAIN_SERVER_API}/nodes/${nodeId}/processes/`);

export const putNodeProcess = (nodeId: number | string, data: any) => put(`${MAIN_SERVER_API}/nodes/${nodeId}/processes/`, data);

export const getTags = (params: any = null) => get(`${MAIN_SERVER_API}/tags/?limit=100`, params);

export const postTags = (params: any = null) => post(`${MAIN_SERVER_API}/tags/`, params);

export const putTag = (tagId: number | string, params: any = null) => put(`${MAIN_SERVER_API}/tags/${tagId}/`, params);

export const delTag = (tagId: number | string) => del(`${MAIN_SERVER_API}/tags/${tagId}/`);
