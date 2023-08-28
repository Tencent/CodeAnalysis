// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * description      方案模板请求
 * author           luochunlan@coding.net
 * create at        2021-01-04
 */

import { MAIN_SERVER_API, get, post, put, del } from '@plat/api';

export const getTmplBaseURL = (orgSid: string) => `${MAIN_SERVER_API}/orgs/${orgSid}/schemes`;

/**
 * 获取模板列表
 * @param query
 */
export const getTmplList = (orgSid: string, query: any) => get(`${getTmplBaseURL(orgSid)}/`, query);

/**
 * 创建模板
 * @param data
 */
export const createTmpl = (orgSid: string, data: any) => post(`${getTmplBaseURL(orgSid)}/`, data);

/**
 * 查询模板基本信息
 * @param id
 */
export const getTmplInfo = (orgSid: string, id: number) => get(`${getTmplBaseURL(orgSid)}/${id}/`);

/**
 * 更新模板信息
 * @param id
 * @param data
 */
export const updateTmpl = (orgSid: string, id: number, data: any) => put(`${getTmplBaseURL(orgSid)}/${id}/`, data);

/**
 * 获取模板代码检查信息
 * @param id
 */
export const getTmplLint = (orgSid: string, id: number) => get(`${getTmplBaseURL(orgSid)}/${id}/lintconf/`);

/**
 * 更新模板代码检查
 * @param id
 * @param data
 */
export const updateTmplLint = (orgSid: string, id: number, data: any) => put(`${getTmplBaseURL(orgSid)}/${id}/lintconf/`, data);

/**
 * 获取分析方案代码检查-官方规则包列表
 * @param orgSid 团队唯一标识
 * @param id
 * @param query 筛选项
 * @returns
 */
export const getCheckPackages = (orgSid: string, id: number, query: any) => get(`${getTmplBaseURL(orgSid)}/${id}/checkprofile/checkpackages/`, query);

/**
 * 获取全部官方规则包列表
 * @param orgSid 团队唯一标识
 * @param id
 */
export const getAllCheckPackages = (orgSid: string, id: number) => get(`${getTmplBaseURL(orgSid)}/${id}/allcheckpackages/`);

/**
 * 给规则配置添加规则包
 * @param orgSid 团队唯一标识
 * @param id
 * @param data 参数
 */
export const addCheckPackages = (orgSid: string, id: number, data: any) => post(`${getTmplBaseURL(orgSid)}/${id}/checkprofile/checkpackages/`, {
  checkpackages: data,
});

/**
 * 给规则配置移除规则包
 * @param orgSid 团队唯一标识
 * @param id
 * @param pkgId 规则包ID
 */
export const delCheckPackage = (orgSid: string, id: number, pkgId: number) => del(`${getTmplBaseURL(orgSid)}/${id}/checkprofile/checkpackages/${pkgId}/`);

/**
 * 获取规则包详情
 * @param orgSid 团队唯一标识
 * @param id
 * @param pkgId 规则包ID
 */
export const getCheckPackagesDetail = (orgSid: string, id: number, pkgId: number) => get(`${getTmplBaseURL(orgSid)}/${id}/checkprofile/checkpackages/${pkgId}/`);

/**
 * 获取规则包规则列表
 * @param orgSid 团队唯一标识
 * @param id
 * @param pkgId 规则包ID
 * @param query 筛选项
 */
export const getPackagesRule = (orgSid: string, id: number, pkgId: number, query: any) => get(`${getTmplBaseURL(orgSid)}/${id}/checkprofile/checkpackages/${pkgId}/rules/`, query);

/**
 * 获取规则包下规则的过滤信息
 * @param orgSid 团队唯一标识
 * @param id
 * @param pkgId 规则包ID
 */
export const getRulesFilter = (orgSid: string, id: number, pkgId: number) => get(`${getTmplBaseURL(orgSid)}/${id}/checkprofile/checkpackages/${pkgId}/rules/filter/`);

/**
 * 代码检查-规则配置-修改规则状态
 * @param orgSid 团队唯一标识
 * @param id
 * @param data 参数
 */
export const modifyRuleState = (orgSid: string, id: number, data: any) => put(`${getTmplBaseURL(orgSid)}/${id}/checkprofile/rules/modifystate/`, data);

/**
 * 代码检查-规则配置-修改规则严重级别
 * @param orgSid 团队唯一标识
 * @param id
 * @param data 参数
 */
export const modifyRuleSeverity = (orgSid: string, id: number, data: any) => put(`${getTmplBaseURL(orgSid)}/${id}/checkprofile/rules/modifyseverity/`, data);

/**
 * 代码检查-规则配置-修改规则信息
 * @param orgSid 团队唯一标识
 * @param id
 * @param data 参数
 */
export const modifyRule = (orgSid: string, id: number, data: any) => put(`${getTmplBaseURL(orgSid)}/${id}/checkprofile/rules/modify/`, data);

/**
 * 代码检查-规则配置-移除规则
 * @param orgSid 团队唯一标识
 * @param id
 * @param data
 */
export const delRule = (orgSid: string, id: number, data: any) => del(`${getTmplBaseURL(orgSid)}/${id}/checkprofile/rules/delete/`, data);

/**
 * 获取全部规则列表
 * @param orgSid 团队唯一标识
 * @param id
 * @param query 筛选项
 */
export const getAllRules = (orgSid: string, id: number, query: any) => get(`${getTmplBaseURL(orgSid)}/${id}/allrules/`, query);

/**
 * 获取所有已配置的规则
 * @param orgSid 团队唯一标识
 * @param id
 * @param query 筛选项
 */
export const getAllCheckRules = (orgSid: string, id: number, query: any) => get(`${getTmplBaseURL(orgSid)}/${id}/checkrules/`, query);

/**
 * 获取所有已配置规则的筛选项
 * @param orgSid 团队唯一标识
 * @param id
 * @param query 筛选项
 */
export const getAllCheckRulesFilters = (orgSid: string, id: number, query: any) => get(`${getTmplBaseURL(orgSid)}/${id}/checkrules/filter/`, query);

/**
 * 代码检查-规则配置-批量添加规则
 * @param orgSid 团队唯一标识
 * @param id
 * @param data 参数
 */
export const addRule = (orgSid: string, id: number, data: any) => post(`${getTmplBaseURL(orgSid)}/${id}/checkprofile/rules/create/`, data);

/**
 * 代码检查 - 规则配置 - 规则详情
 * @param orgSid 团队唯一标识
 * @param id
 * @param ruleId
 */
export const getRuleDetail = (orgSid: string, id: number, ruleId: number) => get(`${getTmplBaseURL(orgSid)}/${id}/allrules/${ruleId}/`);

/**
 * 获取代码度量数据
 * @param id
 */
export const getTmplMetrics = (orgSid: string, id: number) => get(`${getTmplBaseURL(orgSid)}/${id}/metricconf/`);

/**
 * 更新代码度量数据
 * @param id
 * @param data
 */
export const updateTmplMetrics = (orgSid: string, id: number, data: any) => put(`${getTmplBaseURL(orgSid)}/${id}/metricconf/`, data);

/**
 * 获取过滤路径
 * @param id
 * @param query
 */
export const getTmplScanDir = (orgSid: string, id: number, query?: any) => get(`${getTmplBaseURL(orgSid)}/${id}/scandirs/`, query);

/**
 * 添加过滤路径
 * @param id
 * @param data
 */
export const addTmplScanDir = (orgSid: string, id: number, data: any) => post(`${getTmplBaseURL(orgSid)}/${id}/scandirs/`, data);

/**
 * 编辑过滤路径
 * @param id
 * @param data
 */
export const updateTmplScanDir = (orgSid: string, id: number, scanDirId: number, data: any) => put(`${getTmplBaseURL(orgSid)}/${id}/scandirs/${scanDirId}/`, data);

/**
 * 删除过滤路径
 * @param id
 * @param scanDirId
 */
export const delTmplScanDir = (orgSid: string, id: number, scanDirId: number) => del(`${getTmplBaseURL(orgSid)}/${id}/scandirs/${scanDirId}/`);

/**
 * 批量删除过滤路径
 * @param id
 */
export const delAllTmplScanDir = (orgSid: string, id: number) => del(`${getTmplBaseURL(orgSid)}/${id}/scandirs/clear/`);

/**
 * 批量导入过滤路径
 * @param id
 * @param data
 */
export const importTmplScanDir = (orgSid: string, id: number, data: any) => post(`${getTmplBaseURL(orgSid)}/${id}/scandirs/bulkcreate/`, data);

/**
 * 获取指定模板生成的分析方案
 * @param id
 */
export const getSchemeList = (orgSid: string, id: number, query: any) => get(`${getTmplBaseURL(orgSid)}/${id}/childrens/`, query);

/**
 * 模板同步
 * @param orgSid 团队唯一标识
 * @param id
 * @param data
 */
export const syncScheme = (orgSid: string, id: number, data: any) => post(`${getTmplBaseURL(orgSid)}/${id}/push/`, data);

/**
 * 获取模板权限
 * @param id
 */
export const getPermConf = (orgSid: string, id: number) => get(`${getTmplBaseURL(orgSid)}/${id}/permconf/`);

/**
 * 修改模板权限
 * @param id
 * @param data
 */
export const updatePermConf = (orgSid: string, id: number, data: any) => put(`${getTmplBaseURL(orgSid)}/${id}/permconf/`, data);
