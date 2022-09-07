import { SearchFormField } from '@tencent/micro-frontend-shared/component/search';
import { t } from '@tencent/micro-frontend-shared/i18n';
import { TOOL_STATUS_OPTIONS, ToolScopeEnum } from '@src/constant';

/** 定义筛选字段结构 */
export const TOOL_SEARCH_FIELDS: SearchFormField[] = [{
  name: 'display_name',
  type: 'string',
  formType: 'input',
  placeholder: t('工具名称'),
}, {
  name: 'status',
  type: 'number',
  formType: 'select',
  label: t('工具状态'),
  options: TOOL_STATUS_OPTIONS,
}, {
  name: 'scope',
  type: 'number',
  formType: 'checkbox',
  formValue: ToolScopeEnum.CUSTOM,
  placeholder: t('仅查看自定义工具'),
}];

/** 高级搜索的筛选字段 */
export const TOOL_MORE_SEARCH_FIELDS: SearchFormField[] = [];

/** 整体的筛选字段 */
export const TOOL_FILTER_FIELDS = TOOL_SEARCH_FIELDS.concat(TOOL_MORE_SEARCH_FIELDS);

interface Filter {
  count: number;
  display_name: number;
  value: number;
}
interface Filters {
  [key: string]: Filter[]
}

const generateFilterOptions = (filter: Filter[]) => filter.map(item => ({ ...item, label: `${item.display_name} (${item.count})` }));

export const getRuleSearchFields = ({
  severity = [], category = [], language_name: languageName = [],
}: Filters): SearchFormField[] => {
  const severityOptions = generateFilterOptions(severity);
  const categoryOptions = generateFilterOptions(category);
  const languageOptions = generateFilterOptions(languageName);
  return [{
    name: 'severity',
    type: 'number',
    formType: 'select',
    label: t('严重级别'),
    options: severityOptions,
    style: { width: 100 },
  }, {
    name: 'category',
    type: 'number',
    formType: 'select',
    label: t('规则类别'),
    options: categoryOptions,
    style: { width: 100 },
  }, {
    name: 'language_name',
    type: 'string',
    formType: 'select',
    label: t('适用语言'),
    options: languageOptions,
    style: { width: 100 },
  }, {
    name: 'disable',
    type: 'string',
    formType: 'select',
    label: t('规则状态'),
    options: [{ value: 'false', label: t('可用') }, { value: 'true', label: t('不可用') }],
    style: { width: 100 },
  }, {
    name: 'display_name',
    type: 'string',
    formType: 'input',
    placeholder: t('规则名称'),
  }];
};

export const getRuleFilterFields = (filters: Filters) => getRuleSearchFields(filters);
