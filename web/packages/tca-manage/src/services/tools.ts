import { MAIN_SERVER_API, get, put, post, ToolAPI } from './common';

/**
 * 获取工具列表
 * @param params 筛选参数
 * @returns 工具列表 Promise
 */
export const getTools = (params: any = null) => ToolAPI.getTools(params);

/**
 * 获取规则列表
 * @param params 筛选参数
 * @returns 规则列表 Promise
 */
export const getRules = (params: any = null) => get(`${MAIN_SERVER_API}/conf/checkrules/`, params);

/**
 * 获取工具依赖列表
 * @param params 筛选参数
 * @returns 工具依赖列表 Promise
 */
export const getToolLibs = (params: any = null) => get(`${MAIN_SERVER_API}/conf/toollibs/`, params);

/**
 * 添加工具依赖
 * @param orgId
 * @param data
 * @returns
 */
export const addToolLib = (data: any) => post(`${MAIN_SERVER_API}/conf/toollibs/`, data);

/**
 * 获取工具依赖详情
 * @param orgId
 * @param libId
 * @returns
 */
export const getLibDetail = (libId: number) => get(`${MAIN_SERVER_API}/conf/toollibs/${libId}/`);

/**
 * 更新工具依赖
 * @param orgId
 * @param libId
 * @param data
 * @returns
 */
export const updateToolLib = (libId: number, data: any) => put(`${MAIN_SERVER_API}/conf/toollibs/${libId}/`, data);

export const putToolOpen = (toolId: number | string, params: any) => put(`${MAIN_SERVER_API}/checktools/${toolId}/open/`, params);

/**
 * 获取官方规则包列表
 * @param params 筛选参数
 * @returns 官方规则包列表 Promise
 */
export const getPackages = (params: any = null) => get(`${MAIN_SERVER_API}/conf/checkpackages/`, params);
