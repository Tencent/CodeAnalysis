import { SearchFormField } from '@tencent/micro-frontend-shared/component/search';
import { LIB_ENV_OPTIONS } from '@src/constant';

/** 定义筛选字段结构 */
export const TOOLLIB_SEARCH_FIELDS: SearchFormField[] = [{
  name: 'name',
  type: 'string',
  formType: 'input',
  placeholder: '依赖名称',
}, {
  name: 'os',
  type: 'string',
  formType: 'select',
  label: '适用系统',
  options: LIB_ENV_OPTIONS,
}];

/** 高级搜索的筛选字段 */
export const TOOLLIB_MORE_SEARCH_FIELDS: SearchFormField[] = [];

/** 整体的筛选字段 */
export const TOOLLIB_FILTER_FIELDS = TOOLLIB_SEARCH_FIELDS.concat(TOOLLIB_MORE_SEARCH_FIELDS);
