import { MAIN_SERVER_API, fetchAPIManager, get, put } from '@plat/api';

/** node restful api */
export const nodeAPI = fetchAPIManager(`${MAIN_SERVER_API}/nodes/`);

/**
 * 批量更新节点信息
 * @param data 更新数据
 * @returns
 */
export const putMultiNode = (data: any) => put(`${MAIN_SERVER_API}/nodes/batchupdate/`, data);

/**
 * 获取节点子进程配置列表
 * @param nodeId 节点ID
 * @returns
 */
export const getNodeProcess = (nodeId: number) => get(`${MAIN_SERVER_API}/nodes/${nodeId}/processes/`);

/**
 * 获取通用工具进程配置列表
 * @returns
 */
export const getProcess = () => get(`${MAIN_SERVER_API}/nodes/processes/`);

/**
 * 获取节点任务列表
 * @param nodeId 节点ID
 * @returns
 */
export const getNodeTask = (nodeId: number | string, params: any) => get(`${MAIN_SERVER_API}/nodes/${nodeId}/tasks/`, params);

/**
 * 更新节点子进程配置
 * @param nodeId 节点ID
 * @param data 更新数据
 * @returns
 */
export const putNodeProcess = (nodeId: number, data: any) => put(`${MAIN_SERVER_API}/nodes/${nodeId}/processes/`, data);

/**
 * 批量更新节点子进程配置
 * @param data 更新数据
 * @returns
 */
export const putMultiNodeProcess = (data: any) => put(`${MAIN_SERVER_API}/nodes/processes/batchupdate/`, data);

/** tag restful api */
export const tagAPI = fetchAPIManager(`${MAIN_SERVER_API}/tags/`);
