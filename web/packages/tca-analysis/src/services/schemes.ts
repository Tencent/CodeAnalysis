// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * description      分析方案请求
 * author           luochunlan@coding.net
 * create at        2020-10-23
 */

import { get, post, put, del } from './index';
import { MAIN_SERVER_API, getMainBaseURL } from './common';

/**
 * 获取分析方案列表
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param query 筛选参数
 */
export const getSchemes = (orgSid: string, teamName: string, repoId: string | number, query?: any) => get(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/`, query);

/**
 * 获取平台语言列表
 */
export const getLanguages = () => get(`${MAIN_SERVER_API}/languages/?limit=100`);

/**
 * 获取规则包标签列表
 */
export const getLabels = () => get(`${MAIN_SERVER_API}/labels/?limit=100`);

/**
 * 获取运行环境列表
 */
export const getTags = (orgId: string, params: any = null) => get(`${MAIN_SERVER_API}/orgs/${orgId}/nodes/tags/`, params);

/**
 * 拉取模板配置
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param schemeId 分析方案ID
 * @param data 参数
 */
export const pullTmpl = (orgSid: string, teamName: string, repoId: number, schemeId: number, data: any) => post(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/pull/`, data);

/**
 * 创建分析方案
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param data 参数
 */
export const createScheme = (orgSid: string, teamName: string, repoId: string | number, data: any) => post(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/initscheme/`, data);

/**
 * 拷贝分析方案
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param data 参数
 */
export const copyScheme = (orgSid: string, teamName: string, repoId: string | number, data: any) => post(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/copyscheme/`, data);

/**
 * 拷贝分析方案
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param schemeId 分析方案ID
 */
export const getSchemeBasic = (orgSid: string, teamName: string, repoId: string | number, schemeId: string | number) => get(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/basicconf/`);

/**
 * 更新分析方案基础信息
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param schemeId 分析方案ID
 * @param data 参数
 * @returns
 */
export const updateSchemeBasic = (orgSid: string, teamName: string, repoId: string | number, schemeId: string | number, data: any) => put(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/basicconf/`, data);

// ============================================ 分析方案 - 代码检查 ============================================

/**
 * 获取分析方案代码检查配置信息
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param schemeId 分析方案ID
 */
export const getLintConfig = (orgSid: string, teamName: string, repoId: string | number, schemeId: string | number) => get(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/lintconf/`);

/**
 * 更新分析方案代码检查配置信息
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param schemeId 分析方案ID
 * @param data
 * @returns
 */
export const updateLintConfig = (orgSid: string, teamName: string, repoId: string | number, schemeId: string | number, data: any) => put(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/lintconf/`, data);

/**
 * 获取分析方案代码检查-官方规则包列表
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param schemeId 分析方案ID
 * @param query 筛选项
 * @returns
 */
export const getCheckPackages = (orgSid: string, teamName: string, repoId: string | number, schemeId: string | number, query: any) => get(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/checkprofile/checkpackages/`, query);

/**
 * 获取全部官方规则包列表
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param schemeId 分析方案ID
 * @param params
 * @returns
 */
export const getAllCheckPackages = (orgSid: string, teamName: string, repoId: string | number, schemeId: string | number, params: any = null) => get(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/allcheckpackages/`, params);

/**
 * 给规则配置添加规则包
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param schemeId 分析方案ID
 * @param data 参数
 * @returns
 */
export const addCheckPackages = (orgSid: string, teamName: string, repoId: string | number, schemeId: string | number, data: any) => post(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/checkprofile/checkpackages/`, {
  checkpackages: data,
});

/**
 * 给规则配置移除规则包
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param schemeId 分析方案ID
 * @param pkgId 规则包ID
 * @returns
 */
export const delCheckPackage = (orgSid: string, teamName: string, repoId: string | number, schemeId: string | number, pkgId: number) => del(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/checkprofile/checkpackages/${pkgId}/`);

/**
 * 获取规则包详情
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param schemeId 分析方案ID
 * @param pkgId 规则包ID
 * @returns
 */
export const getCheckPackagesDetail = (orgSid: string, teamName: string, repoId: string | number, schemeId: string | number, pkgId: number) => get(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/checkprofile/checkpackages/${pkgId}/`);

/**
 * 获取规则包规则列表
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param schemeId 分析方案ID
 * @param pkgId 规则包ID
 * @param query 筛选项
 * @returns
 */
export const getPackagesRule = (
  orgSid: string,
  teamName: string,
  repoId: string | number,
  schemeId: string | number,
  pkgId: number,
  query: any,
) => get(
  `${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/checkprofile/checkpackages/${pkgId}/rules/`,
  query,
);

/**
 * 获取规则包下规则的过滤信息
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param schemeId 分析方案ID
 * @param pkgId 规则包ID
 * @returns
 */
export const getRulesFilter = (orgSid: string, teamName: string, repoId: string | number, schemeId: string | number, pkgId: number) => get(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/checkprofile/checkpackages/${pkgId}/rules/filter/`);

/**
 * 代码检查-规则配置-修改规则状态
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param schemeId 分析方案ID
 * @param data 参数
 * @returns
 */
export const modifyRuleState = (orgSid: string, teamName: string, repoId: string | number, schemeId: string | number, data: any) => put(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/checkprofile/rules/modifystate/`, data);

/**
 * 代码检查-规则配置-修改规则严重级别
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param schemeId 分析方案ID
 * @param data 参数
 * @returns
 */
export const modifyRuleSeverity = (orgSid: string, teamName: string, repoId: string | number, schemeId: string | number, data: any) => put(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/checkprofile/rules/modifyseverity/`, data);

/**
 * 代码检查-规则配置-修改规则信息
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param schemeId 分析方案ID
 * @param data 参数
 * @returns
 */
export const modifyRule = (orgSid: string, teamName: string, repoId: string | number, schemeId: string | number, data: any) => put(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/checkprofile/rules/modify/`, data);

/**
 * 代码检查-规则配置-移除规则
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param schemeId 分析方案ID
 * @param data
 * @returns
 */
export const delRule = (orgSid: string, teamName: string, repoId: string | number, schemeId: string | number, data: any) => del(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/checkprofile/rules/delete/`, data);

/**
 * 获取全部规则列表
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param schemeId 分析方案ID
 * @param query 筛选项
 * @returns
 */
export const getAllRules = (orgSid: string, teamName: string, repoId: string | number, schemeId: string | number, query: any) => get(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/allrules/`, query);

/**
 * 代码检查-规则配置-批量添加规则
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param schemeId 分析方案ID
 * @param data 参数
 * @returns
 */
export const addRule = (orgSid: string, teamName: string, repoId: string | number, schemeId: string | number, data: any) => post(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/checkprofile/rules/create/`, data);

/**
 * 代码检查 - 规则配置 - 规则详情
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param schemeId 分析方案ID
 * @param ruleId
 * @returns
 */
export const getRuleDetail = (orgSid: string, teamName: string, repoId: string | number, schemeId: string | number, ruleId: number) => get(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/allrules/${ruleId}/`);

/**
 * 代码检查 - 获取指定规则的详细信息
 * @param {*} toolName - 工具名称
 * @param {*} ruleRealName - 规则真实名称
 * @returns
 */
export const getRuleDetailByName = (toolName: string, ruleRealName: string) => get(`${MAIN_SERVER_API}/conf/checkrules/byname/}`, {
  checktool_name: toolName,
  checkrule_real_name: ruleRealName,
});

// ============================================ 分析方案 - 代码度量 ============================================

/**
 * 分析方案获取代码度量配置
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param schemeId 分析方案ID
 * @returns
 */
export const getCodeMetrics = (orgSid: string, teamName: string, repoId: string | number, schemeId: string | number) => get(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/metricconf/`);

/**
 * 更新代码度量数据
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param schemeId 分析方案ID
 * @param data 参数
 * @returns
 */
export const updateCodeMetrics = (orgSid: string, teamName: string, repoId: number, schemeId: number, data: any) => put(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/metricconf/`, data);

// ============================================ 分析方案 - 过滤路径 ============================================

/**
 * 获取系统过滤路径
 * @param orgSid
 * @param teamName
 * @param repoId
 * @param schemeId
 * @param query
 */
export const getSysPath = (orgSid: string, teamName: string, repoId: number, schemeId: number, query: any = {}) => get(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/defaultpaths/`, {
  limit: 500,
  ...query,
});

/**
 * 开启系统默认过滤路径
 * @param orgSid
 * @param teamName
 * @param repoId
 * @param schemeId
 * @param pathId
 */
export const addSysPath = (orgSid: string, teamName: string, repoId: number, schemeId: number, pathId: number) => post(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/defaultpaths/`, {
  default_scan_path: pathId,
});

/**
 * 移除系统默认过滤路径
 * @param orgSid
 * @param teamName
 * @param repoId
 * @param schemeId
 * @param query
 */
export const delSysPath = (orgSid: string, teamName: string, repoId: number, schemeId: number, pathId: number) => del(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/defaultpaths/${pathId}/`);

/**
 * 获取过滤路径配置
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param schemeId 分析方案ID
 * @param query 晒筛选
 * @returns
 */
export const getScanDir = (orgSid: string, teamName: string, repoId: number, schemeId: number, query: any) => get(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/scandirs/`, query);

/**
 * 添加过滤路径
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param schemeId 分析方案ID
 * @param data 参数
 * @returns
 */
export const addScanDir = (orgSid: string, teamName: string, repoId: number, schemeId: number, data: any) => post(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/scandirs/`, data);

/**
 * 编辑过滤路径配置
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param schemeId 分析方案ID
 * @param scanDirId 路径ID
 * @param data 参数
 * @returns
 */
export const updateScanDir = (orgSid: string, teamName: string, repoId: number, schemeId: number, scanDirId: number, data: any) => put(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/scandirs/${scanDirId}/`, data);

/**
 * 移除过滤路径配置
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param schemeId 分析方案ID
 * @param scanDirId 路径ID
 * @returns
 */
export const delScanDir = (orgSid: string, teamName: string, repoId: number, schemeId: number, scanDirId: number) => del(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/scandirs/${scanDirId}/`);

/**
 * 情况过滤路径配置
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param schemeId 分析方案ID
 * @returns
 */
export const delAllScanDir = (orgSid: string, teamName: string, repoId: number, schemeId: number) => del(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/scandirs/clear/`);

/**
 * 批量导入过滤路径配置
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param schemeId 分析方案ID
 * @param data 参数
 * @returns
 */
export const importScanDir = (orgSid: string, teamName: string, repoId: number, schemeId: number, data: any) => post(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/scandirs/bulkcreate/`, data);

// ============================================ 已关联分支 ============================================

/**
 * 获取已关联分支列表
 * @param orgSid 团队唯一标识
 * @param teamName 项目唯一标识
 * @param repoId 代码库ID
 * @param schemeId 分析方案ID
 * @param query
 * @returns
 */
export const getBranchs = (orgSid: string, teamName: string, repoId: number, schemeId: number, query: any) => get(`${getMainBaseURL(orgSid, teamName)}/repos/${repoId}/schemes/${schemeId}/branchs/`, query);

/**
 * 获取工具列表
 * @param {*} query
 */
export const getCheckTools = (orgId: string, query: any) => get(`${MAIN_SERVER_API}/orgs/${orgId}/checktools/`, query);
