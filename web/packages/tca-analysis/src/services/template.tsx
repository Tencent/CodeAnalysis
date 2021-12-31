/**
 * description      方案模板请求
 * author           luochunlan@coding.net
 * create at        2021-01-04
 */

import { get, post, put, del } from './index';
import { MAIN_SERVER_API } from './common';

export const getTmplBaseURL = (org_sid: string) => `${MAIN_SERVER_API}/orgs/${org_sid}/schemes`;

/**
 * 获取模板列表
 * @param query
 */
export const getTmplList = (org_sid: string, query: any) => get(`${getTmplBaseURL(org_sid)}/`, query);

/**
 * 创建模板
 * @param data
 */
export const createTmpl = (org_sid: string, data: any) => post(`${getTmplBaseURL(org_sid)}/`, data);

/**
 * 查询模板基本信息
 * @param id
 */
export const getTmplInfo = (org_sid: string, id: number) => get(`${getTmplBaseURL(org_sid)}/${id}/`);

/**
 * 更新模板信息
 * @param id
 * @param data
 */
export const updateTmpl = (org_sid: string, id: number, data: any) => put(`${getTmplBaseURL(org_sid)}/${id}/`, data);

/**
 * 获取模板代码检查信息
 * @param id
 */
export const getTmplLint = (org_sid: string, id: number) => get(`${getTmplBaseURL(org_sid)}/${id}/lintconf/`);

/**
 * 更新模板代码检查
 * @param id
 * @param data
 */
export const updateTmplLint = (org_sid: string, id: number, data: any) => put(`${getTmplBaseURL(org_sid)}/${id}/lintconf/`, data);

/**
 * 获取分析方案代码检查-官方规则包列表
 * @param org_sid 团队唯一标识
 * @param id
 * @param query 筛选项
 * @returns
 */
export const getCheckPackages = (org_sid: string, id: number, query: any) => get(`${getTmplBaseURL(org_sid)}/${id}/checkprofile/checkpackages/`, query);

/**
 * 获取全部官方规则包列表
 * @param org_sid 团队唯一标识
 * @param id
 */
export const getAllCheckPackages = (org_sid: string, id: number) => get(`${getTmplBaseURL(org_sid)}/${id}/allcheckpackages/`);

/**
 * 给规则配置添加规则包
 * @param org_sid 团队唯一标识
 * @param id
 * @param data 参数
 */
export const addCheckPackages = (org_sid: string, id: number, data: any) => post(`${getTmplBaseURL(org_sid)}/${id}/checkprofile/checkpackages/`, {
  checkpackages: data,
});

/**
 * 给规则配置移除规则包
 * @param org_sid 团队唯一标识
 * @param id
 * @param pkgId 规则包ID
 */
export const delCheckPackage = (org_sid: string, id: number, pkgId: number) => del(`${getTmplBaseURL(org_sid)}/${id}/checkprofile/checkpackages/${pkgId}/`);

/**
 * 获取规则包详情
 * @param org_sid 团队唯一标识
 * @param id
 * @param pkgId 规则包ID
 */
export const getCheckPackagesDetail = (org_sid: string, id: number, pkgId: number) => get(`${getTmplBaseURL(org_sid)}/${id}/checkprofile/checkpackages/${pkgId}/`);

/**
 * 获取规则包规则列表
 * @param org_sid 团队唯一标识
 * @param id
 * @param pkgId 规则包ID
 * @param query 筛选项
 */
export const getPackagesRule = (org_sid: string, id: number, pkgId: number, query: any) => get(`${getTmplBaseURL(org_sid)}/${id}/checkprofile/checkpackages/${pkgId}/rules/`, query);

/**
 * 获取规则包下规则的过滤信息
 * @param org_sid 团队唯一标识
 * @param id
 * @param pkgId 规则包ID
 */
export const getRulesFilter = (org_sid: string, id: number, pkgId: number) => get(`${getTmplBaseURL(org_sid)}/${id}/checkprofile/checkpackages/${pkgId}/rules/filter/`);

/**
 * 代码检查-规则配置-修改规则状态
 * @param org_sid 团队唯一标识
 * @param id
 * @param data 参数
 */
export const modifyRuleState = (org_sid: string, id: number, data: any) => put(`${getTmplBaseURL(org_sid)}/${id}/checkprofile/rules/modifystate/`, data);

/**
 * 代码检查-规则配置-修改规则严重级别
 * @param org_sid 团队唯一标识
 * @param id
 * @param data 参数
 */
export const modifyRuleSeverity = (org_sid: string, id: number, data: any) => put(`${getTmplBaseURL(org_sid)}/${id}/checkprofile/rules/modifyseverity/`, data);

/**
 * 代码检查-规则配置-修改规则信息
 * @param org_sid 团队唯一标识
 * @param id
 * @param data 参数
 */
export const modifyRule = (org_sid: string, id: number, data: any) => put(`${getTmplBaseURL(org_sid)}/${id}/checkprofile/rules/modify/`, data);

/**
 * 代码检查-规则配置-移除规则
 * @param org_sid 团队唯一标识
 * @param id
 * @param data
 */
export const delRule = (org_sid: string, id: number, data: any) => del(`${getTmplBaseURL(org_sid)}/${id}/checkprofile/rules/delete/`, data);

/**
 * 获取全部规则列表
 * @param org_sid 团队唯一标识
 * @param id
 * @param query 筛选项
 */
export const getAllRules = (org_sid: string, id: number, query: any) => get(`${getTmplBaseURL(org_sid)}/${id}/allrules/`, query);

/**
 * 代码检查-规则配置-批量添加规则
 * @param org_sid 团队唯一标识
 * @param id
 * @param data 参数
 */
export const addRule = (org_sid: string, id: number, data: any) => post(`${getTmplBaseURL(org_sid)}/${id}/checkprofile/rules/create/`, data);

/**
 * 代码检查 - 规则配置 - 规则详情
 * @param org_sid 团队唯一标识
 * @param id
 * @param ruleId
 */
export const getRuleDetail = (org_sid: string, id: number, ruleId: number) => get(`${getTmplBaseURL(org_sid)}/${id}/allrules/${ruleId}/`);

/**
 * 获取代码度量数据
 * @param id
 */
export const getTmplMetrics = (org_sid: string, id: number) => get(`${getTmplBaseURL(org_sid)}/${id}/metricconf/`);

/**
 * 更新代码度量数据
 * @param id
 * @param data
 */
export const updateTmplMetrics = (org_sid: string, id: number, data: any) => put(`${getTmplBaseURL(org_sid)}/${id}/metricconf/`, data);

/**
 * 获取过滤路径
 * @param id
 * @param query
 */
export const getTmplScanDir = (org_sid: string, id: number, query: any) => get(`${getTmplBaseURL(org_sid)}/${id}/scandirs/`, query);

/**
 * 添加过滤路径
 * @param id
 * @param data
 */
export const addTmplScanDir = (org_sid: string, id: number, data: any) => post(`${getTmplBaseURL(org_sid)}/${id}/scandirs/`, data);

/**
 * 编辑过滤路径
 * @param id
 * @param data
 */
export const updateTmplScanDir = (org_sid: string, id: number, scanDirId: number, data: any) => put(`${getTmplBaseURL(org_sid)}/${id}/scandirs/${scanDirId}/`, data);

/**
 * 删除过滤路径
 * @param id
 * @param scanDirId
 */
export const delTmplScanDir = (org_sid: string, id: number, scanDirId: number) => del(`${getTmplBaseURL(org_sid)}/${id}/scandirs/${scanDirId}/`);

/**
 * 批量删除过滤路径
 * @param id
 */
export const delAllTmplScanDir = (org_sid: string, id: number) => del(`${getTmplBaseURL(org_sid)}/${id}/scandirs/clear/`);

/**
 * 批量导入过滤路径
 * @param id
 * @param data
 */
export const importTmplScanDir = (org_sid: string, id: number, data: any) => post(`${getTmplBaseURL(org_sid)}/${id}/scandirs/bulkcreate/`, data);

/**
 * 获取指定模板生成的分析方案
 * @param id
 */
export const getSchemeList = (org_sid: string, id: number, query: any) => get(`${getTmplBaseURL(org_sid)}/${id}/childrens/`, query);

/**
 * 模板同步
 * @param org_sid 团队唯一标识
 * @param id
 * @param data
 */
export const syncScheme = (org_sid: string, id: number, data: any) => post(`${getTmplBaseURL(org_sid)}/${id}/push/`, data);

/**
 * 获取模板权限
 * @param id
 */
export const getPermConf = (org_sid: string, id: number) => get(`${getTmplBaseURL(org_sid)}/${id}/permconf/`);

/**
 * 修改模板权限
 * @param id
 * @param data
 */
export const updatePermConf = (org_sid: string, id: number, data: any) => put(`${getTmplBaseURL(org_sid)}/${id}/permconf/`, data);
