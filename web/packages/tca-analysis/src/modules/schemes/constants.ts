// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

export const SCAN_LIST = [
  {
    label: '代码检查',
    value: 'lint_enabled',
    tips: '检查是否存在 bug 或不规范',

  },
  {
    label: '圈复杂度',
    value: 'cc_scan_enabled',
    tips: '检查是否存在复杂函数',
  },
  {
    label: '重复代码',
    value: 'dup_scan_enabled',
    tips: '可发现重复代码/复制代码',
  },
  {
    label: '代码统计',
    value: 'cloc_scan_enabled',
    tips: '统计代码行数',
  },
];

type PathTypes = {
  [key: number]: string
};

export const SCAN_TYPES: PathTypes = {
  1: 'include（包含）',
  2: 'exclude（过滤）',
};


export const PATH_TYPES: PathTypes = {
  1: '通配符',
  2: '正则表达式',
};

export const HOOKS_STATUS = {
  0: 'Success',
  100: 'Node Error',
  200: 'Server Error',
};

export const RULE_STATE = {
  1: '启用',
  2: '屏蔽',
};

export const SEVERITY = {
  1: '致命',
  2: '错误',
  3: '警告',
  4: '提示',
};

export const CATEGORY = {
  1: '功能',
  2: '安全',
  3: '性能',
  4: '可用性',
  5: '无障碍化',
  6: '国际化',
  7: '代码风格',
  8: '其他',
};
