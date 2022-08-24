/**
 * shared hooks - useURLParams 获取url参数hooks
 */
import { useMemo } from 'react';

import { getFilterFieldByURLSearch } from '../util/route';
import { FilterField } from '../util/types';

/**
 * 根据筛选字段列表获取路由筛选相关信息数据
 * @param filterFields 筛选字段列表
 * @returns
 */
const getURLParams = (filterFields: FilterField[]) => {
  const filter = getFilterFieldByURLSearch(filterFields);
  const { limit, offset, ordering, ...searchParams } = filter;
  const pageSize = limit as number;
  const pageStart = offset as number;
  const currentPage = Math.floor(pageStart / pageSize) + 1;
  return {
    /** 全部筛选项，筛选参数+分页参数+排序参数 */
    filter,
    /** 当前页码 */
    currentPage,
    /** 当前每页数量 */
    pageSize,
    /** 当前偏移数量 */
    pageStart,
    /** 筛选参数  */
    searchParams,
    /** 排序参数 */
    ordering,
  };
};

/** 根据路由变化，获取参数 */
const useURLParams = (filterFields: FilterField[] = []) => useMemo(() => getURLParams(filterFields), [
  window.location.search,
]);

export default useURLParams;
