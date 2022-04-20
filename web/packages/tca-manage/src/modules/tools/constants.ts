
export const STATUS_ENUM = {
  RUNNING: 0,
  SUSPENDING: 1,
  DISABLE: 2,
  TRIAL: 3,
};

export const STATUS_CHOICES = {
  [STATUS_ENUM.RUNNING]: '正常运营',
  [STATUS_ENUM.SUSPENDING]: '暂停使用',
  [STATUS_ENUM.DISABLE]: '已下架',
  [STATUS_ENUM.TRIAL]: '体验运营',
};

export const PERM_ENUM = {
  TEAM: 1,
  ALL: 2,
  ALL_CUSTOM: 3,
};

export const PERM_OPTIONS = [
  {
    label: '团队内可用',
    value: PERM_ENUM.TEAM,
  },
  {
    label: '全平台可用',
    value: PERM_ENUM.ALL,
  },
  {
    label: '支持自定义规则，全平台可用',
    value: PERM_ENUM.ALL_CUSTOM,
  },
];

/** 定义筛选字段结构 */
export const TOOL_SEARCH_FIELDS = [{
  name: 'display_name',
  formType: 'input',
  type: 'string',
  placeholder: '工具名称',
}];

/** 高级搜索的筛选字段 */
export const TOOL_MORE_SEARCH_FIELDS: any = [];

/** 整体的筛选字段 */
export const TOOL_FILTER_FIELDS = TOOL_SEARCH_FIELDS.concat(TOOL_MORE_SEARCH_FIELDS);
