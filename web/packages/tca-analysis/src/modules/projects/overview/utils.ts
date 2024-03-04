// Copyright (c) 2021-2024 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import get from 'lodash/get';

// 项目内
import {
  SEVERITY_TYPE,
  SEVERITY_TYPE_TXT,
  STANDARD_TYPE,
  RISK_TYPE,
  RISK_TYPE_TXT,
  CATEGORY_TYPE_TXT,
  LINT_STATE_TYPE_TXT,
} from '@src/modules/projects/constants';
import { formatDate } from '@src/utils';
import { CLOC_TYPE, CLOC_TYPE_TXT } from './codecloc';
import { CYC_TYPE, CYC_TYPE_TXT } from './codecc';
import { LINT_HISTORY_TYPE, LINT_HISTORY_TYPE_TXT } from './codelint';
import { isEmpty } from 'lodash';

/**
 * 格式化时间，获取表格时间格式
 * @param time 时间
 */
export const formatChartDate = (time: any) => formatDate(time, 'MM-DD HH:mm');

/**
 * 格式化代码检查最新数据
 * @param latestLintData 代码检查最新数据
 */
export const formatLatestLintData = (latestLintData: any) => {
  if (latestLintData) {
    const res = {
      total: 0, // 问题总量
      fatal: 0, // 致命
      error: 0, // 错误
      warning: 0, // 警告
      info: 0, // 提示
    };
    res.total = latestLintData.lint_issue_num;
    const list = latestLintData.lint_issue_severity_list;
    Object.values(list).forEach((value: any) => {
      if (value.severity === SEVERITY_TYPE.FATAL) {
        res.fatal = value.num;
      } else if (value.severity === SEVERITY_TYPE.ERROR) {
        res.error = value.num;
      } else if (value.severity === SEVERITY_TYPE.WARNING) {
        res.warning = value.num;
      } else if (value.severity === SEVERITY_TYPE.INFO) {
        res.info = value.num;
      }
    });
    return res;
  }
  return {
    total: '-',
    fatal: '-',
    error: '-',
    warning: '-',
    info: '-',
  };
};

/**
 * 获取圈复杂度简要数据，用于分支概览
 * @param cycScans 圈复杂度历史详情数据
 */
export const getBriefCycData = (cycScans: any) => (cycScans.length > 0
  ? cycScans[0].custom_summary || cycScans[0].default_summary
  : null);

/**
 * 获取重复代码简要数据，用于分支概览
 * @param dupScans 重复代码历史详情数据
 */
export const getBriefDupData = (dupScans: any) => {
  if (dupScans.length > 0) {
    return {
      duplicate_rate: dupScans[0].duplicate_rate,
      duplicate_block_count: dupScans[0].duplicate_block_count,
    };
  }
  return null;
};

/**
 * 获取代码检查历史发现问题趋势数据
 * @param scans 代码检查历史数据
 */
export const getLintLineChartData = (scans: any) => {
  if (scans && scans.length > 0) {
    const rowsTotal: any = [];
    const rowsPending: any = [];
    scans.forEach((item: any) => {
      if (item.total_summary) {
        let totalCount = 0;
        let activeCount = 0;
        Object.values(item.total_summary).forEach((dict1: any) => {
          Object.values(Object(dict1)).forEach((dict2: any) => {
            if (Object(dict2).active) {
              activeCount += Object(dict2).active;
            }
            Object.keys(dict2).forEach((key) => {
              if (key !== 'rule_count') {
                totalCount += dict2[key];
              }
            });
          });
        });
        rowsTotal.push({
          date: formatChartDate(item.scan.scan_time),
          num: totalCount,
          type: LINT_HISTORY_TYPE_TXT.TOTAL,
        });
        rowsPending.push({
          date: formatChartDate(item.scan.scan_time),
          num: activeCount,
          type: LINT_HISTORY_TYPE_TXT.UNDEAL,
        });
      }
    });
    return {
      [LINT_HISTORY_TYPE.TOTAL]: rowsTotal.reverse(),
      [LINT_HISTORY_TYPE.UNDEAL]: rowsPending.reverse(),
    };
  }
  return { [LINT_HISTORY_TYPE.TOTAL]: [], [LINT_HISTORY_TYPE.UNDEAL]: [] };
};

/**
 * 获取代码检查未处理、存量饼图、表格数据
 * @param scans 代码检查数据
 */
export const getLintPieChartData = (scans: any) => {
  const summaryDict = {
    undealData: {},
    totalData: {},
  };
  if (scans && scans.length > 0) {
    let scanFlag = false;
    let totalFlag = false;
    Object.values(scans).forEach((value: any) => {
      const {
        scan_summary: scanSummary,
        total_summary: totalSummary,
        status,
      } = value;
      // 如果成功，则取成功那次结果，否则取最近一次成功有数据的
      if (
        !scanFlag
        && ((status >= 0 && status < 100) || JSON.stringify(scanSummary) !== '{}')
      ) {
        summaryDict.undealData = scanSummary;
        scanFlag = true;
      }
      if (
        !totalFlag
        && ((status >= 0 && status < 100) || JSON.stringify(totalSummary) !== '{}')
      ) {
        summaryDict.totalData = totalSummary;
        totalFlag = true;
      }
    });
  }

  return {
    undealData: lintSummary2Chart(summaryDict.undealData),
    totalData: lintSummary2Chart(summaryDict.totalData),
  };
};

/**
 * 用于格式化处理未处理问题、存量问题数据
 * @param summary 代码检查每次分析的简要数据 total_summary or scan_summary
 */
const lintSummary2Chart = (summary: any) => {
  const categoryDict = {};
  const severityDict = {};
  const rows: Array<any> = [];
  const stateChoices = {
    ...LINT_STATE_TYPE_TXT,
    RULE_COUNT: '涵盖规则数',
  };
  Object.keys(summary).forEach((key) => {
    const dict = summary[key];
    Object.keys(dict).forEach((key2) => {
      const value = dict[key2];
      const { active } = Object(dict[key2]);
      if (active) {
        if (categoryDict[key]) {
          categoryDict[key] += active;
        } else {
          categoryDict[key] = active;
        }
        if (severityDict[key2]) {
          severityDict[key2] += active;
        } else {
          severityDict[key2] = active;
        }
      }
      Object.keys(value).forEach((key3) => {
        if (key3 === 'active') {
          rows.push({
            category: CATEGORY_TYPE_TXT[key.toUpperCase()],
            severity: SEVERITY_TYPE_TXT[key2.toUpperCase()],
            state: stateChoices[key3.toUpperCase()],
            counts: value.active,
          });
        }
      });
    });
  });
  const category = Object.keys(categoryDict).map(key => ({
    value: categoryDict[key],
    type: CATEGORY_TYPE_TXT[key.toUpperCase()],
  }));
  const severity = Object.keys(severityDict).map(key => ({
    value: severityDict[key],
    type: SEVERITY_TYPE_TXT[key.toUpperCase()],
  }));
  return {
    category,
    severity,
    rows,
  };
};

/**
 * 获取圈复杂度详情数据形式
 * @param scans 圈复杂度详情数据
 * @param standard 默认/自定义标准
 */
export const getCyCLineChartData = (scans: any, standard: string) => {
  if (scans && scans.length > 0) {
    const rowsTotal: Array<any> = [];
    const rowsExcess: Array<any> = [];
    scans.forEach((scan: any) => {
      const summary =        standard === STANDARD_TYPE.CUSTOM && scan.custom_summary
        ? scan.custom_summary
        : scan.default_summary;
      if (summary) {
        const date = formatChartDate(scan.scan_time);

        rowsTotal.push({
          date,
          num: summary.under_cc_func_count + summary.over_cc_func_count,
          type: CYC_TYPE_TXT.TOTAL,
        });
        rowsExcess.push({
          date,
          num: summary.over_cc_func_count,
          type: CYC_TYPE_TXT.OVER,
        });
      }
    });
    return {
      [CYC_TYPE.TOTAL]: rowsTotal.reverse(),
      [CYC_TYPE.OVER]: rowsExcess.reverse(),
    };
  }
  return { [CYC_TYPE.TOTAL]: [], [CYC_TYPE.OVER]: [] };
};

/**
 * 获取圈复杂度方法分布数据
 * @param scans 圈复杂度数据
 * @param standard 标准
 */
export const getCycPieChartData = (scans: any, standard: string) => {
  for (const data of scans) {
    if (data.default_summary) {
      const summary = standard === STANDARD_TYPE.CUSTOM && data.custom_summary
        ? data.custom_summary
        : data.default_summary;
      return [
        { type: CYC_TYPE_TXT.OVER, value: summary.over_cc_func_count },
        { type: CYC_TYPE_TXT.EXCESS, value: summary.under_cc_func_count },
      ];
    }
  }
  return [];
};

/**
 * 获取重复代码历史趋势数据
 * @param scans 重复代码数据
 * @param standard 标准
 */
export const getDupLineChartData = (scans: any, standard: string) => {
  if (scans && scans.length > 0) {
    const rowsExhi: Array<any> = [];
    const rowsHigh: Array<any> = [];
    const rowsMidd: Array<any> = [];
    const rowsLow: Array<any> = [];
    scans.forEach((scan: any) => {
      const summary = standard === STANDARD_TYPE.CUSTOM && scan.custom_summary
        ? scan.custom_summary
        : scan.default_summary;
      if (summary) {
        const date = formatChartDate(scan.scan_time);
        rowsExhi.push({
          date,
          num: get(summary, 'exhi_risk.file_count', 0),
          type: RISK_TYPE_TXT.EXHI,
        });
        rowsHigh.push({
          date,
          num: get(summary, 'high_risk.file_count', 0),
          type: RISK_TYPE_TXT.HIGH,
        });
        rowsMidd.push({
          date,
          num: get(summary, 'midd_risk.file_count', 0),
          type: RISK_TYPE_TXT.MIDD,
        });
        rowsLow.push({
          date,
          num: get(summary, 'low_risk.file_count', 0),
          type: RISK_TYPE_TXT.LOW,
        });
      }
    });
    return {
      [RISK_TYPE.EXHI]: rowsExhi.reverse(),
      [RISK_TYPE.HIGH]: rowsHigh.reverse(),
      [RISK_TYPE.MIDD]: rowsMidd.reverse(),
      [RISK_TYPE.LOW]: rowsLow.reverse(),
    };
  }
  return {
    [RISK_TYPE.EXHI]: [],
    [RISK_TYPE.HIGH]: [],
    [RISK_TYPE.MIDD]: [],
    [RISK_TYPE.LOW]: [],
  };
};

/**
 * 获取重复代码文件重复率分布数据
 * @param scans 重复代码数据
 * @param standard 标准
 */
export const getDupBarChartData = (scans: any, standard: string) => {
  if (isEmpty(scans)) {
    return [];
  }

  // for (const data of scans) {
  for (const data of scans) {
    if (data.default_summary) {
      const summary = standard === STANDARD_TYPE.CUSTOM && data.custom_summary
        ? data.custom_summary
        : data.default_summary;
      return [
        {
          type: RISK_TYPE_TXT.EXHI,
          value: get(summary, 'exhi_risk.file_count', 0),
        },
        {
          type: RISK_TYPE_TXT.HIGH,
          value: get(summary, 'high_risk.file_count', 0),
        },
        {
          type: RISK_TYPE_TXT.MIDD,
          value: get(summary, 'midd_risk.file_count', 0),
        },
        {
          type: RISK_TYPE_TXT.LOW,
          value: get(summary, 'low_risk.file_count', 0),
        },
      ];
    }
    return [];
  }
  // });
};

/**
 * 获取代码统计表格数据
 * @param scans 代码统计数据
 */
export const getClocLineChartData = (scans: any) => {
  if (scans && scans.length > 0) {
    const rowsTotal: any = [];
    const rowsCode: any = [];
    const rowsComment: any = [];
    const rowsBlank: any = [];
    scans.forEach((item: any) => {
      if (item) {
        const date = formatChartDate(item.scan_time);
        rowsTotal.push({
          date,
          num: item.total_line_num,
          type: CLOC_TYPE_TXT.TOTAL,
        });
        rowsCode.push({
          date,
          num: item.code_line_num,
          type: CLOC_TYPE_TXT.CODE,
        });
        rowsComment.push({
          date,
          num: item.comment_line_num,
          type: CLOC_TYPE_TXT.COMMENT,
        });
        rowsBlank.push({
          date,
          num: item.blank_line_num,
          type: CLOC_TYPE_TXT.BLANK,
        });
      }
    });
    return {
      [CLOC_TYPE.TOTAL]: rowsTotal.reverse(),
      [CLOC_TYPE.CODE]: rowsCode.reverse(),
      [CLOC_TYPE.COMMENT]: rowsComment.reverse(),
      [CLOC_TYPE.BLANK]: rowsBlank.reverse(),
    };
  }
  return {
    [CLOC_TYPE.TOTAL]: [],
    [CLOC_TYPE.CODE]: [],
    [CLOC_TYPE.COMMENT]: [],
    [CLOC_TYPE.BLANK]: [],
  };
};

/**
 * 获取代码统计饼图数据
 * @param scans 代码统计数据
 */
export const getClocPieChartData = (scans: any) => {
  if (scans && scans.length > 0) {
    return [
      {
        type: CLOC_TYPE_TXT.CODE,
        value: scans[0].code_line_num,
      },
      {
        type: CLOC_TYPE_TXT.COMMENT,
        value: scans[0].comment_line_num,
      },
      {
        type: CLOC_TYPE_TXT.BLANK,
        value: scans[0].blank_line_num,
      },
    ];
  }
  return [];
};

/**
 * 获取与我相关的进度计算
 * @param count 分子
 * @param total 分母
 */
export const getMineFormatData = (count: any, total: any) => {
  let progress = 0;
  if (typeof count === 'number' && typeof total === 'number') {
    progress = total === 0 ? 0 : count / total;
  } else {
    count = '-';
    total = '-';
  }
  return {
    progress,
    count,
    total,
  };
};
