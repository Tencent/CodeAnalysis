// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { omit, toNumber, isString, omitBy, pick, isEqual } from 'lodash';

import { DEFAULT_PAGER } from '@src/common/constants';
import { getQuery } from '@src/utils';

/**
 * 获取当前页面查询参数 hooks
 */
export const useQuery = () => new URLSearchParams(useLocation().search);

interface SortType {
  key: string;
  order: 'ascend' | 'descend' | undefined
}

/**
 * QueryParams
 * 返回：filter，sort，searchParams, currentPage
 */
export const useURLParams = (FILTER_FIELDS: Array<string> = []) => {
  // 当用到useURLParams，需要传递该接口生效的筛选字段，剔除那些定义外的
  const query: any = pick(getQuery(), ['limit', 'offset', 'ordering', ...FILTER_FIELDS]);
  const limit = toNumber(query.limit) || DEFAULT_PAGER.pageSize;
  const offset = toNumber(query.offset) || DEFAULT_PAGER.pageStart;
  const ordering = isString(query.ordering) ? query.ordering : '';
  const sort: SortType = { key: ordering.replace('-', ''), order: ordering.includes('-') ? 'descend' : 'ascend' };
  const searchParams: any = omitBy(omit(query, ['offset', 'limit']), item => !item);
  const currentPage = Math.floor(offset / limit) + 1;
  const filter = {
    limit, offset, ...searchParams,
  };
  if (ordering) {
    filter.ordering = ordering;
  }
  return {
    filter, sort, searchParams, currentPage,
  };
};

/**
 * useeffect，第二个参数可采用对象，通过对比对象是否变更触发fn
 * @param fn
 * @param deps
 */
export const useDeepEffect = (fn: (...args: any[]) => any, deps: any) => {
  const isFirst = useRef(true);
  const prevDeps = useRef(deps);

  useEffect(() => {
    const isFirstEffect = isFirst.current;
    const isSame = prevDeps.current.every((obj: any, index: number) => isEqual(obj, deps[index]));

    isFirst.current = false;
    prevDeps.current = deps;

    if (isFirstEffect || !isSame) {
      fn();
    }
  }, deps);
};
