/* eslint-disable */

export const ISSUE_STATUS = {
  1: '已修复',
  2: '无需修复',
  3: '误报',
  4: '重复单过滤',
  5: '路径过滤',
  6: '规则移除',
  7: '历史问题',
  8: '注释忽略',
};

// Enum name `RESOLUTIONS_ENUM` must match one of the following formats: PascalCase
enum RESOLUTIONS_ENUM {
  ACTIVE = 1,
  RESOLVED,
  CLOSED
}

export const RESOLUTIONS = {
  [RESOLUTIONS_ENUM.ACTIVE]: '未处理',
  [RESOLUTIONS_ENUM.RESOLVED]: '已处理',
  [RESOLUTIONS_ENUM.CLOSED]: '已关闭',
};

enum CC_TYPE_ENUM {
  None,
  Add,
  Delete,
  Update,
}

export const CC_TYPES = {
  [CC_TYPE_ENUM.None]: '无变化',
  [CC_TYPE_ENUM.Add]: '新增',
  [CC_TYPE_ENUM.Delete]: '删除',
  [CC_TYPE_ENUM.Update]: '修改',
};

export const CC_CHANGE_TYPE_CHOICES = {
  0: {
    label: '无变化',
    labelColor: 'rgb(96, 108, 128)',
    color: 'rgb(218, 223, 230)',
  },
  1: {
    label: '新增',
    labelColor: 'rgb(0, 82, 204)',
    color: 'rgb(204, 234, 255)',
  },
  2: {
    label: '删除',
    labelColor: 'rgb(153, 15, 18)',
    color: 'rgb(255, 204, 204)',
  },
  3: {
    label: '修改',
    labelColor: 'rgb(55, 166, 0)',
    color: 'rgb(228, 255, 204)',
  },
};

export const CC_STATES = {
  1: {
    label: '需要关注',
    color: 'rgb(245, 166, 35)',
  },
  2: {
    label: '无需关注',
    color: 'rgb(178, 188, 203)',
  },
};

export const CC_STATE = [{
  text: '未处理',
  value: 1,
}, {
  text: '已关闭',
  value: 3,
}];

export const CC_CHANGE_TYPE_OPTIONS = [
  {
    text: '无变化',
    value: 0,
  },
  {
    text: '新增',
    value: 1,
  },
  {
    text: '删除',
    value: 2,
  },
  {
    text: '修改',
    value: 3,
  },
];

export const CC_FILE_ISSUES_FILTER_FORM_LIST = [
  {
    cName: 'i',
    name: 'last_modifier',
    label: '最近修改人',
  },
  {
    cName: 's',
    name: 'change_type',
    label: '方法变更类型',
    multiple: true,
    options: CC_CHANGE_TYPE_OPTIONS,
  },
  {
    cName: 'i',
    name: 'ccn_gte',
    label: '圈复杂度 >=',
    type: 'number',
  },
  {
    cName: 'i',
    name: 'ccn_lte',
    label: '圈复杂度 <=',
    type: 'number',
  },
];

export const CC_FILES_FILTER_FORM_LIST = [
  {
    cName: 's',
    name: 'change_type',
    label: '文件内方法变更类型',
    multiple: true,
    options: CC_CHANGE_TYPE_OPTIONS,
  },
  {
    cName: 'i',
    name: 'file_path',
    label: '文件路径包含',
  },
  {
    cName: 'i',
    name: 'over_cc_func_count_gte',
    label: '超标方法个数 >=',
    type: 'number',
  },
  {
    cName: 'i',
    name: 'over_cc_func_count_lte',
    label: '超标方法个数 <=',
    type: 'number',
  },
  {
    cName: 'i',
    name: 'over_cc_avg_gte',
    label: '超标方法平均圈复杂度 >=',
    type: 'number',
  },
  {
    cName: 'i',
    name: 'over_cc_avg_lte',
    label: '超标方法平均圈复杂度 <=',
    type: 'number',
  },
  {
    cName: 'i',
    name: 'scan_open',
    label: '发现问题的分析ID',
    type: 'number',
  },
  {
    cName: 'i',
    name: 'scan_close',
    label: '关闭问题的分析ID',
    type: 'number',
  },
  {
    cName: 'i',
    name: 'last_modifier',
    label: '最近修改人',
  },
];

export const PAGE_KEY = {
  OVERVIEW: 'overview',
  SCAN_HISTORY: 'scan-history',
  ISSUES_LIST: 'issues-list',
  CC: 'cc',
  CC_FUNS: 'cc', // cc-functions
  CC_FILES: 'cc-files',
  DUP_FILES: 'dup-files',
  CLOCS: 'clocs',
  COV_REPORT: 'cov-report',
  SINGLE_COV: 'single-cov', // 覆盖率单版本覆盖率
  DIFF_COV: 'diff-cov', // 覆盖率差异化覆盖率
  DIFF_COV_TASK: 'diff-cov-task', // 差异化覆盖率文件列表
  COV_DETAIL: 'cov-detail', // 覆盖率详情页
  COV_DETAIL_PACKAGE: 'cov-detail-package', // 覆盖率详情页按包展示
  COV_DETAIL_CLASS: 'cov-detail-class', // 覆盖率详情页按包展示类列表
  COV_DETAIL_FILE: 'cov-detail-file', // 覆盖率详情页按文件展示
  COV_DETAIL_CODE: 'cov-detail-code', // 覆盖率详情页代码展示
  JOB_SETTINGS: 'job-settings',
  METRIC: 'metric',
  CODE_TOOLS: 'code-tools',
};

export const CODE_STYLE_ITEMS = [
  { text: 'Agate', value: 'agate' },
  { text: 'AndroidStudio', value: 'androidstudio' },
  { text: 'Atom-One-Dark', value: 'atom-one-dark' },
  { text: 'Atom-One-Light', value: 'atom-one-light' },
  { text: 'Color-Brewer', value: 'color-brewer' },
  { text: 'Default', value: 'default' },
  { text: 'Dracula', value: 'dracula' },
  { text: 'Github', value: 'github' },
  { text: 'Zenburn', value: 'zenburn' },
];

export const CC_STATE_OPTIONS = [
  { text: '需要关注', value: 1, color: 'rgb(245, 166, 35)' },
  { text: '无需关注', value: 2, color: 'rgb(178, 188, 203)' },
];

export const DUP_FILE_STATE_ENUM = {
  ACTIVE: 1,
  IGNORED: 2,
  CLOSED: 3,
};

export const DUP_FILE_STATE_CHOICES = {
  [DUP_FILE_STATE_ENUM.ACTIVE]: '未处理',
  [DUP_FILE_STATE_ENUM.IGNORED]: '已忽略',
  [DUP_FILE_STATE_ENUM.CLOSED]: '已关闭',
};

export const DUP_FILE_STATE_OPTIONS = [
  { text: '未处理', value: 1, color: 'rgb(245, 166, 35)' },
  { text: '已忽略', value: 2, color: 'rgb(58, 194, 125)' },
  { text: '已关闭', value: 3, color: 'rgb(178, 188, 203)' },
];

export const DUP_STATES = {
  1: {
    label: '未处理',
    color: 'rgb(245, 166, 35)',
  },
  2: {
    label: '可忽略',
    color: 'rgb(58, 194, 125)',
  },
  3: {
    label: '已关闭',
    color: 'rgb(178, 188, 203)',
  },
};

export enum SEVERITY_ENUM {
  fatal = 1,
  error,
  warning,
  info
}

export const SEVERITY = {
  [SEVERITY_ENUM.fatal]: '致命',
  [SEVERITY_ENUM.error]: '错误',
  [SEVERITY_ENUM.warning]: '警告',
  [SEVERITY_ENUM.info]: '提示',
};

export const METRIC_PAGES = [
  {
    value: 'ccfiles',
    label: '圈复杂度',
  },
  {
    value: 'dupfiles',
    label: '重复代码',
  },
  {
    value: 'clocs',
    label: '代码统计',
  },
];

// 以下是nick定义

/**
 * 分析类型
 */
export const SCAN_TYPE = {
  INCR: 1,
  FULL: 2,
  MR: 3,
  COV: 4,
  EXPAND: 5,
  CR_FULL: 6,
  CR_INCR: 7,
};

export const SCAN_TYPE_TXT = {
  INCR: '增量分析',
  FULL: '全量分析',
  MR: '合流任务',
  COV: '覆盖率',
  EXPAND: '扩展功能',
  CR_FULL: 'CR 全量分析',
  CR_INCR: 'CR 增量分析',
};

export const SCAN_TYPE_CHOICES = {
  [SCAN_TYPE.INCR]: SCAN_TYPE_TXT.INCR,
  [SCAN_TYPE.FULL]: SCAN_TYPE_TXT.FULL,
  [SCAN_TYPE.MR]: SCAN_TYPE_TXT.MR,
  [SCAN_TYPE.COV]: SCAN_TYPE_TXT.COV,
  [SCAN_TYPE.EXPAND]: SCAN_TYPE_TXT.EXPAND,
  [SCAN_TYPE.CR_FULL]: SCAN_TYPE_TXT.CR_FULL,
  [SCAN_TYPE.CR_INCR]: SCAN_TYPE_TXT.CR_INCR,
};

/**
 * 严重级别
 */
export const SEVERITY_OPTIONS = [
  {
    label: '致命',
    en_label: 'fatal',
    value: 1,
  },
  {
    label: '错误',
    en_label: 'error',
    value: 2,
  },
  {
    label: '警告',
    en_label: 'warning',
    value: 3,
  },
  {
    label: '提示',
    en_label: 'info',
    value: 4,
  },
];

export const SEVERITY_TYPE = {
  FATAL: 1, // 致命
  ERROR: 2, // 错误
  WARNING: 3, // 警告
  INFO: 4, // 提示
};

export const SEVERITY_TYPE_TXT = {
  FATAL: '致命',
  ERROR: '错误',
  WARNING: '警告',
  INFO: '提示',
};

/**
 * 规则类别
 */
export const CATEGORY_TYPE_TXT = {
  NULL: '-',
  CORRECTNESS: '功能',
  SECURITY: '安全',
  PERFORMANCE: '性能',
  USABILITY: '可用性',
  ACCESSIBILITY: '无障碍化',
  I18N: '国际化',
  CONVENTION: '代码风格',
  OTHER: '其他',
};

export const CATEGORY_TYPE = {
  CORRECTNESS: 1,
  SECURITY: 2,
  PERFORMANCE: 3,
  USABILITY: 4,
  ACCESSIBILITY: 5,
  I18N: 6,
  CONVENTION: 7,
  OTHER: 8,
};

export const CATEGORY_OPTIONS = [
  {
    label: CATEGORY_TYPE_TXT.CORRECTNESS,
    value: CATEGORY_TYPE.CORRECTNESS,
  },
  {
    label: CATEGORY_TYPE_TXT.SECURITY,
    value: CATEGORY_TYPE.SECURITY,
  },
  {
    label: CATEGORY_TYPE_TXT.PERFORMANCE,
    value: CATEGORY_TYPE.PERFORMANCE,
  },
  {
    label: CATEGORY_TYPE_TXT.USABILITY,
    value: CATEGORY_TYPE.USABILITY,
  },
  {
    label: CATEGORY_TYPE_TXT.ACCESSIBILITY,
    value: CATEGORY_TYPE.ACCESSIBILITY,
  },
  {
    label: CATEGORY_TYPE_TXT.I18N,
    value: CATEGORY_TYPE.I18N,
  },
  {
    label: CATEGORY_TYPE_TXT.CONVENTION,
    value: CATEGORY_TYPE.CONVENTION,
  },
  {
    label: CATEGORY_TYPE_TXT.OTHER,
    value: CATEGORY_TYPE.OTHER,
  },
];

/**
 * 代码检查状态type
 */
export const LINT_STATE_TYPE = {
  ACTIVE: 1, // 未处理
  RESOLVED: 2, // 已处理
  CLOSED: 3, // 关闭
};

export const LINT_STATE_TYPE_TXT = {
  ACTIVE: '未处理',
  RESOLVED: '已处理',
  CLOSED: '已关闭',
};

export const LINT_STATE_OPTIONS = [
  {
    label: LINT_STATE_TYPE_TXT.ACTIVE,
    value: LINT_STATE_TYPE.ACTIVE,
  },
  {
    label: LINT_STATE_TYPE_TXT.RESOLVED,
    value: LINT_STATE_TYPE.RESOLVED,
  },
  {
    label: LINT_STATE_TYPE_TXT.CLOSED,
    value: LINT_STATE_TYPE.CLOSED,
  },
];

/**
 * 标准定义 ****************
 */
export const STANDARD_TYPE = {
  DEFAULT: 'default',
  CUSTOM: 'custom',
};

export const STANDARD_TYPE_TXT = {
  DEFAULT: '默认标准',
  CUSTOM: '自定义标准',
};

export const STANDARD_OPTIONS = [
  {
    label: STANDARD_TYPE_TXT.DEFAULT,
    value: STANDARD_TYPE.DEFAULT,
  },
  {
    label: STANDARD_TYPE_TXT.CUSTOM,
    value: STANDARD_TYPE.CUSTOM,
  },
];

/**
 * 风险定义 **************
 */
export const RISK_TYPE = {
  EXHI: 'exhi',
  HIGH: 'high',
  MIDD: 'midd',
  LOW: 'low',
};

export const RISK_TYPE_TXT = {
  EXHI: '极高风险',
  HIGH: '高风险',
  MIDD: '中风险',
  LOW: '低风险',
};

export const RISK_OPTIONS = [
  {
    label: RISK_TYPE_TXT.EXHI,
    value: RISK_TYPE.EXHI,
  },
  {
    label: RISK_TYPE_TXT.HIGH,
    value: RISK_TYPE.HIGH,
  },
  {
    label: RISK_TYPE_TXT.MIDD,
    value: RISK_TYPE.MIDD,
  },
  {
    label: RISK_TYPE_TXT.LOW,
    value: RISK_TYPE.LOW,
  },
];

// 扩展功能 - 工具状态
export const TOOLS_STATUS = {
  0: '正常运营',
  1: '暂停使用',
  2: '已下架',
  3: '体验运营',
};
