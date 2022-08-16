/** 筛选字段数据类型 */
export type FilterFieldType = 'string' | 'number' | 'boolean' | 'time' | 'array_string' | 'array_number';

/** 筛选字段格式 */
export interface FilterField {
  /** 字段名称，唯一标识 */
  name: string;
  /** 字段格式类型 */
  type: FilterFieldType
}

/** 解析路由参数后字段值类型 */
export type URLSearchValue = string;

/** 路由字段结构 */
export interface URLSearch {
  [name: string]: URLSearchValue
}

/** 解析筛选字段值类型 */
export type FilterValue = URLSearchValue | URLSearchValue[] | number | number[];

/** 筛选字段结构 */
export interface Filter {
  [name: string]: FilterValue
}
