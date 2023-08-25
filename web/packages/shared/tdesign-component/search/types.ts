import { FilterField } from '../../util/types';
import { Input, Select, DatePicker } from 'tdesign-react';

/** search 组件 表单类型 */
export type SearchFormFieldType = 'input' | 'select' | 'datepicker';

export const SearchFormFieldComponent = {
  input: Input,
  select: Select,
  datepicker: DatePicker,
};

/** search 组件表单字段类型 */
export interface SearchFormField extends FilterField {
  /** 表单类型 */
  formType: SearchFormFieldType;
  /** 表单value */
  defaultValue?: string | number;
  /** form item 名称  */
  label?: string;
  /** 表单 placeholder */
  placeholder?: string;
  /** 表单 加载状态 */
  loading?: boolean;
  /** select options，仅type为select时生效 */
  options?: any[];
  /** select 可选择，仅type为select时生效 */
  keys?: any;
  /** select 可选择，仅type为select时生效 */
  filterable?: boolean;
  /** 表单样式 */
  style?: React.CSSProperties;
}
