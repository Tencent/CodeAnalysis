export const SCAN_LIST = [
  { label: '代码检查', value: 'lint_enabled' },
  { label: '圈复杂度', value: 'cc_scan_enabled' },
  { label: '重复代码', value: 'dup_scan_enabled' },
  { label: '代码统计', value: 'cloc_scan_enabled' },
];

export const SCAN_TYPES = {
  1: 'include（包含）',
  2: 'exclude（过滤）',
};

export const PATH_TYPES = {
  1: '通配符',
  2: '正则表达式',
};
