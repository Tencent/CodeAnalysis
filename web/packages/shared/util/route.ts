/**
 * utils - route 工具库，与路由相关的
 */
import qs from 'qs';
import { pick, forEach, pickBy, toNumber, toString } from 'lodash';
import { URLSearch, Filter, FilterField, FilterFieldType } from './types';

/**
 * 获取page、page_size分页参数
 * @param page 页码
 * @param pageSize 每页显示数量
 * @returns page, page_size
 */
const getPageNumberPaginationParams = (page: number, pageSize: number) => ({
  page,
  page_size: pageSize,
});

/**
 * 获取limit、offset分页参数
 * @param offset 偏移数
 * @param limit 每页显示数量
 * @returns limit, offset
 */
const getLimitOffsetPaginationParams = (offset: number, limit: number) => ({
  limit, offset,
});


type Use = 'limitOffset' | 'pageNumber';

/**
 * 根据页码和每页显示数量返回对应的后端分页筛选所需字段
 * @param page 页码
 * @param pageSize 每页显示数量
 * @param use 使用返回格式类型，默认使用limitOffset
 * @returns 返回后端分页筛选所需字段，如limit, offset或page, page_size
 */
export const getPaginationParams = (page: number, pageSize: number, use: Use = 'limitOffset') => {
  if (use === 'limitOffset') {
    return getLimitOffsetPaginationParams((page - 1) * pageSize, pageSize);
  }
  return getPageNumberPaginationParams(page, pageSize);
};


const DEFAULT_FILTER_FIELDS: FilterField[] = [{
  name: 'limit',
  type: 'number',
}, {
  name: 'offset',
  type: 'number',
}, {
  name: 'ordering',
  type: 'string',
}];

/** 筛选默认字段名称 */
const DEFAULT_FILTER_FIELD_NAMES = DEFAULT_FILTER_FIELDS.map(field => field.name);

/**
 * 根据筛选参数变更并获取路由参数
 * @param filterFields 额外允许的筛选字段
 * @param params 筛选传入参数
 * @returns 路由筛选参数（已剔除空值）
 */
export const getURLSearchByFilterParams = (filterFields: FilterField[] = [], filter: Filter = {}) => {
  // 获取并解析路由参数
  const search = getURLSearch();
  // 获取筛选字段名称
  const fieldNames = filterFields.map(field => field.name);
  // 从filter对象中pick字段，并将对应值赋予search
  forEach(pick(filter, [...DEFAULT_FILTER_FIELD_NAMES, ...fieldNames]), (value, key) => {
    search[key] = toString(value);
  });
  // 清楚search中为''的值
  return pickBy(search, value => value !== '');
};

/**
 * 获取变更路由
 * @param params 参数
 * @param filterFields 允许filter的字段
 * @returns path
 */
export const getURLPathByFilterParams = (filterFields: FilterField[] = [], filter: Filter = {}) => {
  const search = getURLSearchByFilterParams(filterFields, filter);
  return `${window.location.pathname}?${qs.stringify(search)}`;
};

/**
 * 通过路由参数获取filter字段
 * @param filterFields 允许filter的字段
 */
export const getFilterFieldByURLSearch = (filterFields: FilterField[] = [], pager = { limit: 10, offset: 0 }) => {
  // 解析路由参数，设置pager默认值
  const search = Object.assign({}, pager, getURLSearch());
  // 获取fitterFields的name:type
  const filterFieldKV: { [name: string]: FilterFieldType } = {};
  [...DEFAULT_FILTER_FIELDS, ...filterFields].forEach((field) => {
    filterFieldKV[field.name] = field.type;
  });
  // 仅选取必要的筛选字段，并进行类型转换
  const filter: Filter = {};
  Object.keys(search).forEach((key) => {
    const value = search[key];
    switch (filterFieldKV[key]) {
      case 'string':
        filter[key] = value;
        break;
      case 'boolean':
        filter[key] = value;
        break;
      case 'number':
        filter[key] = toNumber(value);
        break;
      case 'array_number':
        filter[key] = value.split(',').map(item => toNumber(item));
        break;
      case 'array_string':
        filter[key] = value.split(',');
        break;
      case 'time':
        filter[key] = value;
        break;
      default:
        break;
    }
  });
  return filter;
};


/**
 * 获取路由参数
 * @returns 路由参数
 */
export const getURLSearch = () => qs.parse(window.location.search.replace('?', '')) as URLSearch;

/**
 * 防止url调整漏洞，对回调地址进行校验
 * @param href 回调地址
 * @param validHostNames 域名白名单列表，默认[window.location.hostname]
 * @returns 回调链接
 */
export const xssRedirectUri = (redirectUri: string, validHostNames = [window.location.hostname]) => {
  const a = document.createElement('a');
  a.href = decodeURIComponent(redirectUri) || '';
  // 接下来对hostname进行域名白名单的判断
  if (validHostNames.includes(a.hostname)) {
    return a.href;
  }
  return '';
};
