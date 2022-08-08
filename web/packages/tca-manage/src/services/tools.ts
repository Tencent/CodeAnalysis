import { MAIN_SERVER_API, get, put, ToolAPI } from './common';

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

export const putToolOpen = (toolId: number | string, params: any) => put(`${MAIN_SERVER_API}/checktools/${toolId}/open/`, params);

/**
 * 获取官方规则包列表
 * @param params 筛选参数
 * @returns 官方规则包列表 Promise
 */
export const getPackages = (params: any = null) => get(`${MAIN_SERVER_API}/conf/checkpackages/`, params);

/**
 * 获取分析方案模板列表
 * @param params 筛选参数
 * @returns 分析方案模板列表 Promise
 */
export const getSchemes = (params: any = null) => get(`${MAIN_SERVER_API}/schemes/`, params);
