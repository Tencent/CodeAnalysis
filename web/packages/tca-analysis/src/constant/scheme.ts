import { SearchFormField } from '@tencent/micro-frontend-shared/tdesign-component/search';
import { RULE_CATEGORY_OPTIONS, RULE_SEVERITY_OPTIONS } from '@src/constant';

/** 方案模板列表 定义筛选字段结构 */
export const TEMPLATE_SEARCH_FIELDS: SearchFormField[] = [{
  name: 'name',
  label: '名称',
  formType: 'input',
  type: 'string',
  placeholder: '模板名称',
}, {
  name: 'scope',
  label: '类型',
  formType: 'select',
  type: 'string',
  options: [{
    label: '系统模板',
    value: 'system',
  }, {
    label: '非系统模板',
    value: 'not_system',
  }, {
    label: '可编辑模板',
    value: 'editable',
  }],
}];

/** 整体的筛选字段 */
export const TEMPLATE_FILTER_FIELDS = TEMPLATE_SEARCH_FIELDS;

/** 方案模板列表 定义筛选字段结构 */
export const getPkgSearchFields = (languages: any[], labels: any []): SearchFormField[] => [{
  name: 'lang',
  label: '语言',
  formType: 'multiselect',
  type: 'string',
  options: languages,
  keys: {
    value: 'name',
    label: 'display_name',
  },
}, {
  name: 'label',
  label: '分类',
  formType: 'multiselect',
  type: 'string',
  options: labels,
  keys: {
    value: 'name',
    label: 'name',
  },
}];

const BUILD_FLAG_OPTIONS = [{
  value: 'true',
  label: '需要编译',
}, {
  value: 'false',
  label: '无需编译',
}];

/** 方案模板列表 定义筛选字段结构 */
export const getPkgRuleSearchFields = (
  severitys: any[],
  category: any[],
  tools: any[],
  languages: any[],
  getFilterOptions: (listData: any) => any[],
): SearchFormField[] => [{
  name: 'severity',
  label: '问题级别',
  formType: 'multiselect',
  type: 'string',
  options: getFilterOptions(severitys),
}, {
  name: 'checkrule_category',
  label: '规则分类',
  formType: 'multiselect',
  type: 'string',
  options: getFilterOptions(category),
}, {
  name: 'checktool',
  label: '所属工具',
  formType: 'select',
  type: 'string',
  options: getFilterOptions(tools),
}, {
  name: 'checkrule_language',
  label: '适用语言',
  formType: 'select',
  type: 'string',
  options: getFilterOptions(languages),
}, {
  name: 'checktool_build_flag',
  label: '是否需要编译',
  formType: 'select',
  type: 'string',
  options: BUILD_FLAG_OPTIONS,
}, {
  name: 'checkrule_name',
  label: '规则名称',
  formType: 'input',
  type: 'string',
}];

/** 方案模板列表 定义筛选字段结构 */
export const getAllRuleSearchFields = (
  packages: any[],
  tools: any[],
  languages: any[],
): SearchFormField[] => [{
  name: 'checkpackage',
  label: '官方规则包',
  formType: 'multiselect',
  type: 'string',
  options: packages,
  keys: {
    label: 'name',
    value: 'id',
  },
}, {
  name: 'severity',
  label: '问题级别',
  formType: 'multiselect',
  type: 'string',
  options: RULE_SEVERITY_OPTIONS,
}, {
  name: 'category',
  label: '规则分类',
  formType: 'multiselect',
  type: 'string',
  options: RULE_CATEGORY_OPTIONS,
}, {
  name: 'checktool',
  label: '所属工具',
  formType: 'select',
  type: 'string',
  options: tools,
  keys: {
    label: 'display_name',
    value: 'id',
  },
}, {
  name: 'language_name',
  label: '适用语言',
  formType: 'select',
  type: 'string',
  options: languages,
  keys: {
    value: 'name',
    label: 'display_name',
  },
}, {
  name: 'real_name',
  label: '规则名称',
  formType: 'input',
  type: 'string',
}];

/** 规则包规则列表 列数据在数据项中对应的 key */
export const ALL_PKG_RULE_COLUMN_INDEX = {
  rule_display_name: 'real_name',
  rule_title: 'rule_title',
  tool_display_name: ['checktool', 'display_name'],
  rule_severity: 'severity',
  rule_category_name: 'category_name',
  rule_compile: ['checktool', 'build_flag'],
};

/** 规则包规则列表 列数据在数据项中对应的 key */
export const PKG_RULE_COLUMN_INDEX = {
  rule_display_name: ['checkrule', 'real_name'],
  rule_title: ['checkrule', 'rule_title'],
  tool_display_name: ['checktool', 'display_name'],
  rule_severity: 'severity',
  rule_category_name: ['checkrule', 'category_name'],
  rule_compile: ['checktool', 'build_flag'],
};

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

export const CODE_METRIC_DEFAULT_VALUE = {
  min_ccn: 20,
  dup_block_length_min: 120,
  dup_min_dup_times: 2,
  dup_issue_limit: 1000,
};
