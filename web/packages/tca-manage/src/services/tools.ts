import { get, put } from './index';
import { MAIN_SERVER_API } from './common';

/**
 * 获取工具列表
 * @param params 筛选参数
 */
export const getTools = (params: any = null) => get(`${MAIN_SERVER_API}/checktools/`, params);

export const putToolOpen = (toolId: number | string, params: any) => put(`${MAIN_SERVER_API}/checktools/${toolId}/open/`, params);
