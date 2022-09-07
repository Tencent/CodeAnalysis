import { MAIN_SERVER_API, get, put, post, del } from '@plat/api';

const getToolPrefix = (orgId: string) => `${MAIN_SERVER_API}/orgs/${orgId}/checktools/`;

/**
 * 获取工具列表数据
 * @param orgId
 * @param params
 */
export const getTools = (orgId: string, params: any) => get(getToolPrefix(orgId), params);

/**
 * 创建工具
 * @param orgId
 * @param data
 */
export const createTool = (orgId: string, data: any) => post(getToolPrefix(orgId), data);

/**
 * 修改工具
 * @param orgId
 * @param data
 */
export const updateTool = (orgId: string, toolId: number, data: any) => put(`${getToolPrefix(orgId)}${toolId}/`, data);

/**
 * 更新工具运营状态
 * @param orgId
 * @param toolId
 * @param status
 */
export const updateToolStatus = (orgId: string, toolId: number, status: any) => put(`${getToolPrefix(orgId)}${toolId}/status/`, { status });

/**
 * 获取指定工具详情
 * @param orgId
 * @param toolId
 */
export const getToolDetail = (orgId: string, toolId: number) => get(`${getToolPrefix(orgId)}${toolId}/`);

/**
 * 获取语言
 */
export const getLanguages = () => get(`${MAIN_SERVER_API}/languages/`, { limit: 100 });

/**
 * 获取指定工具的规则列表
 * @param orgId
 * @param toolId
 * @param params
 */
export const getRules = (orgId: string, toolId: number, params: any) => get(`${getToolPrefix(orgId)}${toolId}/rules/`, params);

/**
 * 获取规则的过滤筛选项
 * @param orgId
 * @param toolId
 */
export const getRulesFilters = (orgId: string, toolId: number) => get(`${getToolPrefix(orgId)}${toolId}/rules/filter/`);

/**
 * 添加规则
 * @param orgId
 * @param toolId
 * @param data
 */
export const createRule = (orgId: string, toolId: number, data: any) => post(`${getToolPrefix(orgId)}${toolId}/rules/`, data);

/**
 * 更新规则
 * @param orgId
 * @param toolId
 * @param ruleId
 * @param data
 */
export const updateRule = (orgId: string, toolId: number, ruleId: number, data: any) => put(`${getToolPrefix(orgId)}${toolId}/rules/${ruleId}/`, data);

/**
 * 删除规则
 * @param orgId
 * @param toolId
 * @param ruleId
 */
export const deleteRule = (orgId: string, toolId: number, ruleId: number) => del(`${getToolPrefix(orgId)}${toolId}/rules/${ruleId}/`);

/**
 * 获取规则的过滤筛选项
 * @param orgId
 * @param toolId
 */
export const getCustomRulesFilters = (orgId: string, toolId: number) => get(`${getToolPrefix(orgId)}${toolId}/rules/custom/filter/`);

/**
 * 获取自定义规则列表
 * @param orgId
 * @param toolId
 * @param params
 */
export const getCustomRules = (orgId: string, toolId: number, params: any) => get(`${getToolPrefix(orgId)}${toolId}/rules/custom/`, params);

/**
 * 添加自定义规则 - 用于协同工具
 * @param orgId
 * @param toolId
 * @param data
 */
export const createCustomRule = (orgId: string, toolId: number, data: any) => post(`${getToolPrefix(orgId)}${toolId}/rules/custom/`, data);

/**
 * 更新自定义规则
 * @param orgId
 * @param toolId
 * @param ruleId
 * @param data
 */
export const updateCustomRule = (orgId: string, toolId: number, ruleId: number, data: any) => put(`${getToolPrefix(orgId)}${toolId}/rules/custom/${ruleId}/`, data);

/**
 * 删除规则
 * @param orgId
 * @param toolId
 * @param ruleId
 */
export const deleteCustomRule = (orgId: string, toolId: number, ruleId: number) => del(`${getToolPrefix(orgId)}${toolId}/rules/custom/${ruleId}/`);


/**
 * 获取指定工具白名单列表
 * @param orgId
 * @param toolId
 * @returns
 */
export const getToolWhiteList = (orgId: string, toolId: number) => get(`${getToolPrefix(orgId)}${toolId}/whitelist/`);

/**
 * 添加工具白名单
 * @param orgId
 * @param toolId
 * @param orgSids - 团队 org_sid
 * @returns
 */
export const updateToolWhiteList = (orgId: string, toolId: number, string: string) => post(`${getToolPrefix(orgId)}${toolId}/whitelist/`, {
  org_sid: string,
});

/**
  * 添加工具白名单
  * @param orgId
  * @param toolId
  * @param orgSids - 团队 org_sid
  * @returns
  */
export const addToolWhiteList = (orgId: string, toolId: number, orgSids: Array<string>) => post(`${getToolPrefix(orgId)}${toolId}/whitelist/create/`, {
  organizations: orgSids,
});

/**
 * 删除工具白名单
 * @param orgId - 当前团队
 * @param toolId
 * @param id - 白名单id
 * @returns
 */
export const delToolWhiteList = (orgId: string, toolId: number, id: number) => del(`${getToolPrefix(orgId)}${toolId}/whitelist/${id}/`);


// ====================== 工具依赖 ======================

const getToollibsPrefix = (orgId: string) => `${MAIN_SERVER_API}/orgs/${orgId}/toollibs/`;

/**
 * 获取工具依赖列表
 * @param orgId
 * @param params
 * @returns
 */
export const getToolLibs = (orgId: string, params: any) => get(`${getToollibsPrefix(orgId)}`, params);

/**
 * 添加工具依赖
 * @param orgId
 * @param data
 * @returns
 */
export const addToolLib = (orgId: string, data: any) => post(`${getToollibsPrefix(orgId)}`, data);

/**
 * 获取工具依赖详情
 * @param orgId
 * @param libId
 * @returns
 */
export const getLibDetail = (orgId: string, libId: number) => get(`${getToollibsPrefix(orgId)}${libId}/`);

/**
 * 更新工具依赖
 * @param orgId
 * @param libId
 * @param data
 * @returns
 */
export const updateToolLib = (orgId: string, libId: number, data: any) => put(`${getToollibsPrefix(orgId)}${libId}/`, data);

/**
 * 获取工具依赖方案列表
 * @param orgId
 * @param toolId
 * @returns
 */
export const getToolSchemes = (orgId: string, toolId: number) => get(`${getToolPrefix(orgId)}${toolId}/schemes/`);

/**
 * 创建工具依赖方案
 * @param orgId
 * @param toolId
 * @param data
 * @returns
 */
export const addToolSchemes = (orgId: string, toolId: number, data: any) => post(`${getToolPrefix(orgId)}${toolId}/schemes/`, data);

/**
 * 修改工具依赖方案
 * @param orgId
 * @param toolId
 * @param data
 * @returns
 */
export const updateToolSchemes = (orgId: string, toolId: number, schemeId: number, data: any) => put(`${getToolPrefix(orgId)}${toolId}/schemes/${schemeId}/`, data);

/**
 * 移除工具依赖
 * @param orgId
 * @param toolId
 * @param libSchemeId
 * @returns
 */
export const delToolScheme = (orgId: string, toolId: number, libSchemeId: number) => del(`${getToolPrefix(orgId)}${toolId}/schemes/${libSchemeId}/`);
